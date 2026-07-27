#!/usr/bin/env python3
"""Claude Code PreToolUse Hook 适配器。

Claude Code 官方 hook 协议：
  - 通过 stdin 接收 JSON：{"tool_name": "Bash", "tool_input": {...}, "session_id": "..."}
  - 通过 stdout 返回 JSON：
      {"deny": true, "reason": "..."} → 阻止工具调用
      {"require_approval": true, "reason": "..."} → 需要用户确认
      {"warn": "..."} → 警告但放行
      {} 或 stdout 为空 → 放行
  - 退出码 0：决策被采纳
  - 退出码 2：阻断（Claude Code 看到非零退出码会停止工具调用）

用户配置方式（在 ~/.claude/settings.json 里）：
{
  "hooks": {
    "PreToolUse": [
      {"command": "python /path/to/adapters/hooks/claude-code/pre_tool_use.py", "type": "command"}
    ]
  }
}

或项目级配置 .claude/settings.json（在项目根目录）。
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

# 把 adapters/hooks/shared/ 加到 sys.path 让 check 模块可被 import
_THIS_DIR = Path(__file__).resolve().parent
_SHARED_DIR = _THIS_DIR.parent / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from check import decide, load_constraints  # noqa: E402


# 工具名归一化映射：Claude Code 用 PascalCase，我们的 constraints.yaml 用小写
TOOL_NAME_MAP = {
    "Bash": "bash",
    "Terminal": "bash",     # 别名
    "Write": "write_file",  # Claude Code 的 Write 写整个文件
    "Edit": "edit",         # Claude Code 的 Edit 做行级替换
    "Read": None,           # 读文件不拦截（白名单）
    "Glob": None,
    "Grep": None,
    "SearchCodebase": None,
    "WebFetch": None,
    "WebSearch": None,
    "AskUserQuestion": None,
    "TodoWrite": None,
    "Task": None,           # 子 agent 任务（内部会触发新 hook）
}


def main():
    """读 stdin → 决策 → 写 stdout"""
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({}))  # 空 stdin，放行
            return 0
        request = json.loads(raw_input)
    except (json.JSONDecodeError, ValueError) as e:
        # 输入无效，记录到 stderr 但放行（避免 hook 失败阻塞 agent）
        print(f"[Rule Hub hook] 输入解析失败：{e}", file=sys.stderr)
        print(json.dumps({}))
        return 0

    tool_name = request.get("tool_name", "")
    tool_input = request.get("tool_input", {})

    # 工具名归一化
    mapped_tool = TOOL_NAME_MAP.get(tool_name, tool_name.lower())
    if mapped_tool is None:
        # 白名单工具直接放行
        print(json.dumps({}))
        return 0

    # 调通用决策函数
    try:
        result = decide(mapped_tool, tool_input)
    except Exception as e:
        # 决策失败时降级为放行（避免 hook 异常阻塞 agent）
        print(f"[Rule Hub hook] 决策异常：{e}", file=sys.stderr)
        print(json.dumps({}))
        return 0

    # 转换为 Claude Code 响应格式
    if result["deny"]:
        response = {
            "deny": True,
            "reason": result["reason"] or f"[{result['matched_constraint']}] 拦截",
        }
        # 同时输出到 stderr 让用户能看到
        print(f"\n🚫 [Rule Hub Hook] DENY: {response['reason']}\n", file=sys.stderr)
        print(json.dumps(response, ensure_ascii=False))
        return 0

    if result["require_approval"]:
        response = {
            "require_approval": True,
            "reason": result["reason"] or f"[{result['matched_constraint']}] 需用户确认",
        }
        print(f"\n⚠️ [Rule Hub Hook] REQUIRES APPROVAL: {response['reason']}\n", file=sys.stderr)
        print(json.dumps(response, ensure_ascii=False))
        return 0

    if result["warn"]:
        # 警告但不阻止
        print(f"\n⚠️ [Rule Hub Hook] WARNING: {result['warn']}\n", file=sys.stderr)
        print(json.dumps({"warn": result["warn"]}, ensure_ascii=False))
        return 0

    # 放行
    print(json.dumps({}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
