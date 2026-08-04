"""
策略引擎封装：OPA 优先（若装了）→ 退化到 check.py（YAML 规则）。

设计哲学：
- check.py 的 YAML 规则适合 80% 简单场景（正则匹配 / 路径黑白名单）
- OPA/Rego 适合 20% 复杂场景（上下文感知 / stateful 熔断 / 时间窗判断）
- 用户没装 OPA 时自动退化到 check.py，能力不丢

使用方式：
    from agentseed.policy_engine import decide
    result = decide(tool_name="Bash", tool_input={"command": "git push"}, context={...})
"""
from __future__ import annotations
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


# 检测 OPA 是否可用
def _opa_available() -> bool:
    """检测系统是否装了 opa binary。"""
    try:
        result = subprocess.run(
            ["opa", "version"],
            capture_output=True, text=True, timeout=3,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _find_rego_policy() -> Path | None:
    """查找 core/policy.rego 路径。"""
    candidates = []
    env_repo = os.environ.get("AGENTSEED_REPO")
    if env_repo:
        candidates.append(Path(env_repo) / "core" / "policy.rego")
    candidates.append(Path.home() / ".cache" / "agentseed" / "core" / "policy.rego")
    candidates.append(Path.cwd() / "core" / "policy.rego")
    candidates.append(Path.cwd() / "agentseed" / "core" / "policy.rego")
    for c in candidates:
        if c.exists():
            return c
    return None


def decide_with_opa(
    tool_name: str,
    tool_input: dict,
    context: dict | None = None,
    rego_path: Path | None = None,
) -> dict:
    """用 OPA 执行 Rego 策略决策。
    返回格式与 check.decide 一致：
      {"deny": bool, "require_approval": bool, "warn": str, "reason": str, "matched_constraint": str}
    """
    if rego_path is None:
        rego_path = _find_rego_policy()
    if rego_path is None:
        raise FileNotFoundError("找不到 core/policy.rego")

    # 构造 OPA 输入
    opa_input = {
        "tool_name": tool_name,
        "tool_input": tool_input,
        "context": context or {},
    }

    # 写临时输入文件
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(opa_input, f)
        input_path = f.name

    try:
        # 调 opa eval
        result = subprocess.run(
            [
                "opa", "eval",
                "-d", str(rego_path),
                "-i", input_path,
                "-f", "json",
                "data.agentseed",
            ],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            raise RuntimeError(f"opa eval 失败: {result.stderr}")

        opa_output = json.loads(result.stdout)
        # 解析 OPA 返回
        result_set = opa_output.get("result", [])
        if not result_set:
            return {
                "deny": False, "require_approval": False,
                "warn": "OPA 返回空结果，放行",
                "reason": "", "matched_constraint": "",
            }
        bindings = result_set[0].get("expressions", [{}])[0].get("value", {})

        return {
            "deny": bool(bindings.get("deny", False)),
            "require_approval": bool(bindings.get("require_approval", False)),
            "warn": bindings.get("warn", ""),
            "reason": bindings.get("reason", ""),
            "matched_constraint": bindings.get("matched_constraint", ""),
        }
    finally:
        Path(input_path).unlink(missing_ok=True)


def decide(
    tool_name: str,
    tool_input: dict,
    context: dict | None = None,
) -> dict:
    """统一决策入口。
    优先用 OPA（若装了 + 找到 policy.rego），否则退化到 check.py。
    context 仅 OPA 用：包含 timestamp / session_failures 等状态。
    """
    # 1. 尝试 OPA
    if _opa_available() and _find_rego_policy():
        try:
            return decide_with_opa(tool_name, tool_input, context)
        except Exception as e:
            # OPA 失败时退化
            fallback_warn = f"OPA 决策失败，退化到 check.py: {e}"

            # 加载 check.py 继续
            import sys
            shared_dir = Path(__file__).resolve().parent.parent / "adapters" / "hooks" / "shared"
            if str(shared_dir) not in sys.path:
                sys.path.insert(0, str(shared_dir))
            from check import decide as check_decide
            result = check_decide(tool_name, tool_input)
            result["warn"] = (result.get("warn", "") + " | " + fallback_warn).strip(" |")
            return result

    # 2. 退化到 check.py
    import sys
    shared_dir = Path(__file__).resolve().parent.parent / "adapters" / "hooks" / "shared"
    if str(shared_dir) not in sys.path:
        sys.path.insert(0, str(shared_dir))
    from check import decide as check_decide
    return check_decide(tool_name, tool_input)


if __name__ == "__main__":
    # 自检
    print("=== policy_engine 自检 ===\n")
    print(f"OPA 可用: {_opa_available()}")
    print(f"policy.rego 路径: {_find_rego_policy()}")
    print()

    # 测试 1：硬编码密钥（应 deny）
    print("--- 测试 1: 硬编码密钥 ---")
    r = decide("Write", {"file_path": "app.py", "content": "key = 'sk-abc123def456ghi789jkl012mno345pqr789'"})
    print(f"deny={r['deny']}, reason={r['reason'][:80]}")
    print()

    # 测试 2：MCP 安装（应 deny）
    print("--- 测试 2: MCP 自安装 ---")
    r = decide("Bash", {"command": "npm install @modelcontextprotocol/server-filesystem"})
    print(f"deny={r['deny']}, reason={r['reason'][:80]}")
    print()

    # 测试 3：上下文感知（非工作时间 git push，仅 OPA 能判断）
    print("--- 测试 3: 非工作时间 git push（上下文感知）---")
    r = decide(
        "Bash", {"command": "git push origin main"},
        context={"timestamp": "2026-07-26T23:30:00Z", "session_failures": 0},
    )
    print(f"require_approval={r['require_approval']}, reason={r['reason'][:80]}")
    print()

    # 测试 4：失败熔断（stateful，仅 OPA 能判断）
    print("--- 测试 4: 失败熔断（session_failures=3）---")
    r = decide(
        "Bash", {"command": "ls -la"},
        context={"timestamp": "2026-07-26T10:00:00Z", "session_failures": 3},
    )
    print(f"deny={r['deny']}, reason={r['reason'][:80]}")
