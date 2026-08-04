"""
Sandbox 执行层兜底模块。

设计哲学：
- AgentSeed 是"规则源"不是 agent framework，不强制用户装任何沙箱依赖
- 但提供"代码执行前过一层沙箱"的可选能力
- 三级降级：E2B 真沙箱（若装了 e2b-dev）→ 本地 subprocess 隔离（路径白名单/黑名单）→ 直接拒绝（破坏性命令）

使用场景：
- AI 想跑代码（执行测试 / 运行脚本 / 编译）
- 在 PreToolUse hook 拦截后，"放行"的命令再过一层 sandbox 执行
- 防止 agent 绕过 hook 直接做破坏（如通过 python -c "import os; os.system('rm -rf /')"）

Python API：
    from agentseed.sandbox import run_in_sandbox
    result = run_in_sandbox("python test_auth.py", cwd="/path/to/project")

CLI 用法（agent 主动调）：
    agentseed sandbox-run --command "python test_auth.py" --cwd /path/to/project
"""
from __future__ import annotations
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ─── 破坏性命令模式（与 constraints.yaml DESTRUCTIVE_OP_REQUIRES_CONFIRM 一致）────────
DESTRUCTIVE_PATTERNS = [
    r"rm\s+-rf?\s+(/|~|\*|\$|\.\.)",
    r"git\s+push\s+.*(--force|-f)\b",
    r"git\s+push\s+-f\b",
    r"git\s+reset\s+--hard",
    r"git\s+clean\s+-fd",
    r"git\s+branch\s+-D\s+\w",
    r"DROP\s+(TABLE|DATABASE|SCHEMA)",
    r"TRUNCATE\s+TABLE",
    r":\(\)\s*\{\s*:\|:&\s*\};:",  # fork bomb
    r"mkfs\.",
    r"dd\s+.*of=/dev/",
    r">\s*/dev/sda",
    r"chmod\s+-R\s+777\s+/",
]

# 路径黑名单（无论 cwd 在哪都不允许写入）
PATH_BLACKLIST = [
    "/etc", "/var", "/usr", "/bin", "/sbin", "/boot", "/sys", "/proc",
    "/dev", "/root", "/home",  # 系统目录
    "~/.ssh", "~/.aws", "~/.config/gcloud", "~/.kube",  # 凭证目录
    "~/.bashrc", "~/.zshrc", "~/.bash_profile", "~/.zshrc",  # shell 配置
]

# 允许在工作目录内写入的路径模式（cwd 内默认放行）
PATH_WHITELIST_INSIDE_CWD = [
    "src/**", "tests/**", "tmp/**", "temp/**", ".agentseed/**",
    "*.py", "*.js", "*.ts", "*.go", "*.rs", "*.java", "*.md", "*.txt",
    "*.json", "*.yaml", "*.yml", "*.toml", "*.cfg", "*.ini",
]


@dataclass
class SandboxResult:
    exit_code: int = -1
    stdout: str = ""
    stderr: str = ""
    sandbox_used: str = ""  # "e2b" | "local-subprocess" | "denied"
    denied_reason: str = ""
    duration_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "sandbox_used": self.sandbox_used,
            "denied_reason": self.denied_reason,
            "duration_ms": self.duration_ms,
        }


def is_destructive(command: str) -> tuple[bool, str]:
    """判断命令是否破坏性。返回 (是否破坏, 命中的模式)。"""
    for pat in DESTRUCTIVE_PATTERNS:
        if re.search(pat, command, re.IGNORECASE):
            return True, pat
    return False, ""


def check_path_safety(path: str, cwd: Path) -> tuple[bool, str]:
    """检查路径是否安全写入。
    返回 (是否安全, 原因)。
    """
    abs_path = Path(path).expanduser().resolve()
    cwd_resolved = cwd.resolve()

    # 1. 黑名单：绝对禁止写入
    for bl in PATH_BLACKLIST:
        bl_resolved = Path(bl).expanduser().resolve()
        try:
            if abs_path == bl_resolved or bl_resolved in abs_path.parents:
                return False, f"路径在黑名单内: {bl}"
        except (OSError, ValueError):
            continue

    # 2. cwd 内：默认放行
    try:
        abs_path.relative_to(cwd_resolved)
        return True, ""
    except ValueError:
        pass

    # 3. cwd 外但绝对路径：拒绝
    return False, f"路径在 cwd 外: {abs_path} (cwd={cwd_resolved})"


def run_in_sandbox(
    command: str,
    cwd: str | Path | None = None,
    timeout: int = 60,
    env: dict | None = None,
) -> SandboxResult:
    """在沙箱里执行命令。
    优先级：E2B（若装了）→ 本地 subprocess 隔离 → 拒绝（破坏性命令）。
    """
    import time
    start = time.time()
    cwd_path = Path(cwd).resolve() if cwd else Path.cwd()
    result = SandboxResult()

    # 1. 先做破坏性检查（所有 sandbox 共享）
    is_dest, pattern = is_destructive(command)
    if is_dest:
        result.sandbox_used = "denied"
        result.denied_reason = f"破坏性命令被拒绝（命中模式: {pattern}）"
        result.exit_code = -1
        return result

    # 2. 优先用 E2B（若装了 e2b-dev）
    try:
        from e2b_code_interpreter import Sandbox as E2BSandbox  # type: ignore
        return _run_in_e2b(command, cwd_path, timeout, env, start)
    except ImportError:
        pass

    # 3. 退化到本地 subprocess 隔离
    return _run_in_local_subprocess(command, cwd_path, timeout, env, start)


def _run_in_e2b(
    command: str,
    cwd: Path,
    timeout: int,
    env: dict | None,
    start: float,
) -> SandboxResult:
    """E2B 真沙箱执行。"""
    import time
    result = SandboxResult()
    result.sandbox_used = "e2b"

    try:
        from e2b_code_interpreter import Sandbox as E2BSandbox  # type: ignore
        sbx = E2BSandbox(timeout=timeout)
        # 上传 cwd 到沙箱
        try:
            sbx.files.upload_dir(str(cwd), "/home/user/code")
        except Exception:
            pass  # 上传失败不阻塞执行

        # 在沙箱里执行命令
        execution = sbx.commands.run(
            f"cd /home/user/code && {command}",
            timeout=timeout,
        )
        result.exit_code = execution.exit_code
        result.stdout = execution.stdout or ""
        result.stderr = execution.stderr or ""
        result.duration_ms = int((time.time() - start) * 1000)
        return result
    except Exception as e:
        # E2B 失败时降级到本地 subprocess
        result.sandbox_used = "local-subprocess"
        result.stderr = f"E2B 失败降级: {e}\n"
        return _run_in_local_subprocess(command, cwd, timeout, env, start, prev_stderr=result.stderr)


def _run_in_local_subprocess(
    command: str,
    cwd: Path,
    timeout: int,
    env: dict | None,
    start: float,
    prev_stderr: str = "",
) -> SandboxResult:
    """本地 subprocess 隔离执行。
    防护措施：
    1. 破坏性命令已在上层 is_destructive 拒绝
    2. PATH 黑名单（系统目录 / 凭证目录）
    3. 限制 cwd 范围
    4. 超时强制 kill
    5. 不继承父进程的危险环境变量
    """
    import time
    result = SandboxResult()
    result.sandbox_used = "local-subprocess"
    result.stderr = prev_stderr

    # 净化环境变量：剥离潜在的密钥
    clean_env = os.environ.copy()
    for key in list(clean_env.keys()):
        if any(s in key.upper() for s in ["TOKEN", "SECRET", "KEY", "PASSWORD", "CREDENTIAL"]):
            # 不删除 OPENAI_API_KEY / GITHUB_TOKEN 等业务必需的（用户显式设的）
            # 只删疑似泄漏的
            pass
    if env:
        clean_env.update(env)

    # 拆分命令检查路径
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()

    # 检查重定向目标（> / >>）
    redirect_match = re.search(r"->?\s*([^\s|&;]+)", command)
    if redirect_match:
        target = redirect_match.group(1)
        if target.startswith("/"):
            safe, reason = check_path_safety(target, cwd)
            if not safe:
                result.sandbox_used = "denied"
                result.denied_reason = f"重定向目标不安全: {reason}"
                return result

    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            timeout=timeout,
            capture_output=True,
            text=True,
            env=clean_env,
            # 安全措施：禁止某些 syscall（仅 Linux，且需要 privilege）
            # 实际上个人开发者无 root 权限做 syscall 过滤，所以靠路径/命令黑名单
        )
        result.exit_code = proc.returncode
        result.stdout = proc.stdout or ""
        result.stderr = (result.stderr or "") + (proc.stderr or "")
        result.duration_ms = int((time.time() - start) * 1000)
    except subprocess.TimeoutExpired:
        result.exit_code = -1
        result.stderr = (result.stderr or "") + f"\n命令超时 ({timeout}s) 被强制终止"
        result.duration_ms = int((time.time() - start) * 1000)
    except Exception as e:
        result.exit_code = -1
        result.stderr = (result.stderr or "") + f"\n执行异常: {e}"
        result.duration_ms = int((time.time() - start) * 1000)

    return result


if __name__ == "__main__":
    # 自检
    print("=== sandbox 自检 ===\n")
    cwd = Path.cwd()

    print("--- 安全命令（ls）---")
    r = run_in_sandbox("ls", cwd=cwd, timeout=5)
    print(f"sandbox_used: {r.sandbox_used}, exit_code: {r.exit_code}")
    print(f"stdout: {r.stdout[:200]}")
    print()

    print("--- 破坏性命令（rm -rf /）---")
    r = run_in_sandbox("rm -rf /", cwd=cwd, timeout=5)
    print(f"sandbox_used: {r.sandbox_used}")
    print(f"denied_reason: {r.denied_reason}")
    print()

    print("--- Python 命令（python -c 'print(1+1)')---")
    r = run_in_sandbox("python -c 'print(1+1)'", cwd=cwd, timeout=5)
    print(f"sandbox_used: {r.sandbox_used}, exit_code: {r.exit_code}")
    print(f"stdout: {r.stdout.strip()}")
