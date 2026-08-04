"""
AgentSeed 通用 Hook 拦截逻辑（适配所有支持 PreToolUse 的平台）。

设计原则：
- 单一职责：本模块只做"读 constraints.yaml + 给定工具调用 → 决策（deny/approve/warn）"
- 不耦合任何平台协议：平台特定 IO 由各适配器负责
- 无第三方依赖：纯 stdlib（避免给用户装 PyYAML）

平台适配器用法：
    from check import decide
    decision = decide(tool_name="Bash", tool_input={"command": "rm -rf /"}, ...)
    if decision["deny"]:
        return deny_to_platform(decision["message"])

约束源：core/constraints.yaml（与本文件同仓库分发）
"""
from __future__ import annotations
import fnmatch
import os
import re
import sys
from pathlib import Path
from typing import Any


def _path_match(pattern: str, path: str) -> bool:
    """路径模式匹配，支持 glob（**/*, tests/**, *.env）和正则。
    默认按 glob 处理；以 ^ 开头的视为正则。
    """
    if pattern.startswith("^"):
        try:
            return bool(re.match(pattern[1:], path))
        except re.error:
            return False
    # glob 模式：fnmatch 不支持 ** 递归，用 pathlib 的 match
    if "**" in pattern:
        # pathlib.PurePath.match 支持 ** 但行为有限
        try:
            from pathlib import PurePosixPath
            return PurePosixPath(path).match(pattern)
        except (ValueError, TypeError):
            pass
    return fnmatch.fnmatch(path, pattern)


# ─── 极简 YAML 解析（避免引入 PyYAML 依赖）─────────────
# 仅解析本仓库 constraints.yaml 用到的子集：
#   - 顶层 key: value
#   - 顶层 list of dict（constraints:）
#   - 嵌套 dict（match: / whitelist:）
#   - 嵌套 list（enforce_at: / intercept_tools:）

def _parse_scalar(val: str) -> Any:
    """解析标量：[1,2,3] / true / null / 引号字符串 / 普通字符串"""
    val = val.strip()
    if not val:
        return None
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(x.strip()) for x in inner.split(",")]
    if val in ("true", "True"):
        return True
    if val in ("false", "False"):
        return False
    if val in ("null", "None", "~"):
        return None
    # 数字
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    # 引号字符串
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    # 块字符串（>-）由上层处理
    return val


def _parse_block_string(lines: list[str], start_idx: int, indent: int) -> tuple[str, int]:
    """解析 >- 块字符串，返回 (拼接内容, 下一行索引)"""
    parts = []
    i = start_idx
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        # 必须缩进 >= parent_indent + 1
        if len(line) - len(line.lstrip()) < indent + 1:
            break
        parts.append(line.strip())
        i += 1
    return " ".join(parts), i


def _parse_yaml(text: str) -> dict:
    """极简 YAML 解析，仅支持本仓库 constraints.yaml 用到的子集"""
    lines = text.splitlines()
    result: dict = {}
    i = 0
    current_top_key = None
    current_constraint_list = None
    current_constraint: dict | None = None
    current_constraint_key = None  # 当前正在写的 constraint 内的 key
    in_constraints = False

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()

        # 跳过空行/注释
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue

        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # 顶层 key: value 或 key:
        if indent == 0:
            if ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip()
                if key == "constraints":
                    in_constraints = True
                    current_constraint_list = []
                    result["constraints"] = current_constraint_list
                    current_constraint = None
                elif val == "":
                    # 块开始，等下面解析
                    current_top_key = key
                    result[key] = {}
                    in_constraints = False
                else:
                    result[key] = _parse_scalar(val)
                    current_top_key = None
                    in_constraints = False
            i += 1
            continue

        # constraints: 列表项
        if in_constraints:
            # 列表项 - id: XXX
            if stripped.startswith("- "):
                # 解析列表项
                # 收集这个列表项的所有字段
                current_constraint = {}
                current_constraint_list.append(current_constraint)
                # 处理 - id: XXX 形式
                rest = stripped[2:].strip()
                if ":" in rest:
                    key, _, val = rest.partition(":")
                    if val.strip():
                        current_constraint[key.strip()] = _parse_scalar(val.strip())
                    else:
                        current_constraint_key = key.strip()
                        # 等下面缩进的内容
                else:
                    current_constraint[rest] = True
                i += 1
                continue

            # 列表项内的字段
            if current_constraint is not None and ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip()

                # 块字符串 >- 处理
                if val in (">-", ">", "|-", "|"):
                    block_text, next_i = _parse_block_string(lines, i + 1, indent)
                    current_constraint[key] = block_text
                    i = next_i
                    continue

                if val == "":
                    # 可能是 dict 或 list 子结构
                    # 简化处理：把后续缩进的同级 key 收集为 dict
                    sub_dict = {}
                    sub_indent = indent + 2
                    j = i + 1
                    while j < len(lines):
                        sub_raw = lines[j]
                        if not sub_raw.strip() or sub_raw.lstrip().startswith("#"):
                            j += 1
                            continue
                        sub_indent_actual = len(sub_raw) - len(sub_raw.lstrip())
                        if sub_indent_actual < sub_indent:
                            break
                        sub_line = sub_raw.strip()
                        if ":" in sub_line:
                            sk, _, sv = sub_line.partition(":")
                            sk = sk.strip()
                            sv = sv.strip()
                            # 块字符串 >- 处理（子 dict 内）
                            if sv in (">-", ">", "|-", "|"):
                                block_parts = []
                                k = j + 1
                                while k < len(lines):
                                    k_raw = lines[k]
                                    if not k_raw.strip():
                                        k += 1
                                        continue
                                    k_indent = len(k_raw) - len(k_raw.lstrip())
                                    if k_indent <= sub_indent_actual:
                                        break
                                    block_parts.append(k_raw.strip())
                                    k += 1
                                sub_dict[sk] = " ".join(block_parts) if sv in (">-", ">") else "\n".join(block_parts)
                                j = k
                                continue
                            sub_dict[sk] = _parse_scalar(sv)
                        j += 1
                    current_constraint[key] = sub_dict
                    i = j
                    continue
                else:
                    current_constraint[key] = _parse_scalar(val)
                    i += 1
                    continue

        # meta: 块
        if isinstance(result.get("meta"), dict) or (current_top_key == "meta" and isinstance(result.get("meta"), dict)):
            pass  # 简化处理，meta 段不深解析

        i += 1

    return result


# ─── 核心：决策函数 ───────────────────────────────────

def load_constraints(yaml_path: Path | None = None) -> list[dict]:
    """加载 constraints.yaml，返回 constraints 列表。
    若未提供路径，按以下顺序查找：
      1. 环境变量 AGENTSEED_REPO 指向的目录下的 core/constraints.yaml
      2. ~/.cache/agentseed/core/constraints.yaml（pip 包默认安装路径）
      3. 当前工作目录的 core/constraints.yaml
    """
    if yaml_path is None:
        candidates = []
        env_repo = os.environ.get("AGENTSEED_REPO")
        if env_repo:
            candidates.append(Path(env_repo) / "core" / "constraints.yaml")
        candidates.append(Path.home() / ".cache" / "agentseed" / "core" / "constraints.yaml")
        candidates.append(Path.cwd() / "core" / "constraints.yaml")
        candidates.append(Path.cwd() / "agentseed" / "core" / "constraints.yaml")
        for c in candidates:
            if c.exists():
                yaml_path = c
                break
        if yaml_path is None:
            raise FileNotFoundError("找不到 core/constraints.yaml，请设置 AGENTSEED_REPO 环境变量")

    text = yaml_path.read_text(encoding="utf-8")
    parsed = _parse_yaml(text)
    return parsed.get("constraints", [])


def _match_constraint(
    constraint: dict,
    tool_name: str,
    tool_input: dict,
    *,
    file_path: str | None = None,
    command: str | None = None,
    content: str | None = None,
) -> tuple[bool, str]:
    """判断一个 constraint 是否命中当前工具调用。
    返回 (命中, 拒绝原因)。命中且 action=deny/require_approval 时返回 True。
    """
    # 1. 工具名匹配
    intercept_tools = constraint.get("intercept_tools", [])
    if intercept_tools and tool_name not in intercept_tools:
        return False, ""

    match = constraint.get("match", {})
    if not isinstance(match, dict):
        return False, ""

    # 2. 命令正则匹配（bash/terminal/git）
    cmd_regex = match.get("command_regex")
    if cmd_regex:
        if command is None:
            command = tool_input.get("command", "") or tool_input.get("cmd", "")
        if command and re.search(cmd_regex, command, re.IGNORECASE):
            return True, constraint.get("message", f"[{constraint.get('id')}] 命中")
        # 有 command_regex 但未命中，说明这条 constraint 不适用
        return False, ""

    # 3. 内容正则匹配（write_file/edit/write）
    content_regex = match.get("content_regex")
    if content_regex:
        if content is None:
            content = (tool_input.get("content", "") or
                       tool_input.get("new_string", "") or
                       tool_input.get("text", ""))
        if content and re.search(content_regex, content, re.IGNORECASE | re.DOTALL):
            # 检查白名单
            whitelist = constraint.get("whitelist") or {}
            if isinstance(whitelist, dict):
                wl_patterns = whitelist.get("content_patterns") or []
                if isinstance(wl_patterns, str):
                    wl_patterns = [wl_patterns]
                for wl_pat in wl_patterns:
                    try:
                        if re.search(wl_pat, content):
                            return False, ""  # 白名单命中，放行
                    except re.error:
                        continue
            return True, constraint.get("message", f"[{constraint.get('id')}] 命中")
        return False, ""

    # 4. 文件路径匹配（write_file/edit）
    path_patterns = match.get("file_path_patterns") or match.get("require_user_approval_for_paths")
    if path_patterns:
        if file_path is None:
            file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
        if file_path:
            for pat in path_patterns:
                if _path_match(pat, file_path):
                    # 路径命中，再看 header marker（针对生成文件）
                    header_marker = constraint.get("match_header_marker")
                    if header_marker:
                        # 检查文件头是否含"禁止手工编辑"标记
                        try:
                            head = Path(file_path).read_text(encoding="utf-8")[:500]
                            if header_marker in head:
                                return True, constraint.get("message", f"[{constraint.get('id')}] 命中")
                            else:
                                return False, ""  # 文件不是生成的，不拦截
                        except (OSError, UnicodeDecodeError):
                            return False, ""
                    # require_approval 类型
                    if constraint.get("action") == "require_approval":
                        # 检查白名单（session 允许的文件）
                        whitelist = constraint.get("whitelist") or {}
                        if isinstance(whitelist, dict):
                            wl_patterns = whitelist.get("path_patterns") or []
                            if isinstance(wl_patterns, str):
                                wl_patterns = [wl_patterns]
                            for wl_pat in wl_patterns:
                                if _path_match(wl_pat, file_path):
                                    return False, ""
                            session_file = whitelist.get("session_allowed_file")
                            if session_file and Path(session_file).exists():
                                allowed = Path(session_file).read_text(encoding="utf-8").splitlines()
                                if file_path in [l.strip() for l in allowed if l.strip() and not l.startswith("#")]:
                                    return False, ""
                        return True, constraint.get("message", f"[{constraint.get('id')}] 命中")
                    return True, constraint.get("message", f"[{constraint.get('id')}] 命中")
            return False, ""

    # 5. 大文件检测（NO_LARGE_FILE_REWRITE）
    if "file_min_lines" in match or "new_content_exceeds_ratio" in match:
        if file_path is None:
            file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
        min_lines = match.get("file_min_lines", 0)
        ratio = match.get("new_content_exceeds_ratio", 1.0)
        try:
            orig = Path(file_path).read_text(encoding="utf-8")
            orig_lines = len(orig.splitlines())
            if orig_lines < min_lines:
                return False, ""
            new_content = content or tool_input.get("content", "")
            new_lines = len(new_content.splitlines())
            if new_lines / max(orig_lines, 1) >= ratio:
                return True, constraint.get("message", f"[{constraint.get('id')}] 命中")
        except (OSError, UnicodeDecodeError):
            return False, ""
        return False, ""

    return False, ""


def decide(
    tool_name: str,
    tool_input: dict,
    *,
    constraints: list[dict] | None = None,
    yaml_path: Path | None = None,
) -> dict:
    """对一个工具调用做决策。
    返回 dict:
      {
        "deny": bool,            # 是否拒绝
        "require_approval": bool,  # 是否需要用户确认
        "warn": str,             # 警告信息（不阻止）
        "reason": str,           # 拦截原因
        "matched_constraint": str # 命中的 constraint id
      }
    """
    if constraints is None:
        try:
            constraints = load_constraints(yaml_path)
        except FileNotFoundError as e:
            return {
                "deny": False,
                "require_approval": False,
                "warn": f"[AgentSeed] {e}（hook 降级为放行）",
                "reason": "",
                "matched_constraint": "",
            }

    # 抽取工具调用相关字段
    tool_name_norm = (tool_name or "").lower()
    # Claude Code 用 PascalCase（Bash/Write/Edit），Cursor 用 camelCase（bash/write/edit）
    # 统一 lowercase 比较
    file_path = tool_input.get("file_path") or tool_input.get("path") or ""
    command = tool_input.get("command") or tool_input.get("cmd") or ""
    content = (tool_input.get("content") or
               tool_input.get("new_string") or
               tool_input.get("text") or "")

    result = {
        "deny": False,
        "require_approval": False,
        "warn": "",
        "reason": "",
        "matched_constraint": "",
    }

    for c in constraints:
        # 只看 enforce_at 含 pre_tool_use 的（runtime 类不在此处理）
        enforce_at = c.get("enforce_at", [])
        if isinstance(enforce_at, str):
            enforce_at = [enforce_at]
        if "pre_tool_use" not in enforce_at and "PreToolUse" not in enforce_at:
            continue

        matched, msg = _match_constraint(
            c, tool_name_norm, tool_input,
            file_path=file_path, command=command, content=content,
        )
        if not matched:
            continue

        action = c.get("action", "warn")
        result["matched_constraint"] = c.get("id", "")
        result["reason"] = msg
        if action == "deny":
            result["deny"] = True
            return result
        elif action == "require_approval":
            result["require_approval"] = True
            return result
        elif action == "warn":
            result["warn"] = msg
            # 继续检查其他 constraint（warn 不阻止后续检查）

    return result


# ─── 自检（直接运行此文件可看测试输出）─────────────────

if __name__ == "__main__":
    # 自检：构造典型违规场景，看 decide 是否正确拦截
    test_cases = [
        ("硬编码密钥", "Write", {"file_path": "app.py", "content": "api_key = 'sk-abc123def456ghi789jkl012mno345pqr789'"}),
        ("自行安装 MCP", "Bash", {"command": "npm install @modelcontextprotocol/server-filesystem"}),
        ("git push 未确认", "Bash", {"command": "git push origin main"}),
        ("rm -rf /", "Bash", {"command": "rm -rf /"}),
        ("提交 .env", "Bash", {"command": "git add .env && git commit -m 'add env'"}),
        ("正常 ls 命令", "Bash", {"command": "ls -la"}),
        ("正常 Write 文件", "Write", {"file_path": "newfile.txt", "content": "hello world"}),
    ]
    constraints = load_constraints()
    print(f"已加载 {len(constraints)} 条 constraint\n")
    for name, tool, inp in test_cases:
        r = decide(tool, inp, constraints=constraints)
        status = "🚫 DENY" if r["deny"] else ("⚠ APPROVAL" if r["require_approval"] else ("⚠ WARN" if r["warn"] else "✅ PASS"))
        print(f"{name:20s} → {status}")
        if r["deny"] or r["require_approval"] or r["warn"]:
            print(f"  matched: {r['matched_constraint']}")
            print(f"  reason: {r['reason'][:120]}")
        print()
