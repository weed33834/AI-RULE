#!/usr/bin/env python3
"""Cursor PreToolUse Hook 适配器。

Cursor 官方 hook 协议（与 Claude Code 极相似）：
  - stdin: JSON {"toolName": "bash", "toolInput": {"command": "..."}, ...}
  - stdout: JSON {"deny": true, "reason": "..."} / {"requireApproval": true, "reason": "..."} / {}
  - exit 0: 决策生效
  - exit 非 0：hook 错误（Cursor 默认放行）

用户配置方式（项目根 .cursor/hooks.json）：
{
  "preToolUse": [
    {"command": "python ./adapters/hooks/cursor/pre_tool_use.py"}
  ]
}

Cursor 工具名约定（camelCase）：
  bash / write / edit / read_file / grep / glob / search_codebase / ask_user_question / ...
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_SHARED_DIR = _THIS_DIR.parent / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from check import decide  # noqa: E402

# Cursor 工具名归一化映射
TOOL_NAME_MAP = {
    "bash": "bash",
    "terminal": "bash",
    "write": "write_file",
    "edit": "edit",
    "create_file": "write_file",
    "read_file": None,
    "grep": None,
    "glob": None,
    "search_codebase": None,
    "ask_user_question": None,
    "todo_write": None,
    "task": None,
}


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps({}))
            return 0
        req = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        print(json.dumps({}))
        return 0

    # Cursor 支持 toolName（camelCase）和 tool_name（snake_case）两种格式
    tool_name = req.get("toolName") or req.get("tool_name", "")
    tool_input = req.get("toolInput") or req.get("tool_input", {})

    mapped = TOOL_NAME_MAP.get(tool_name.lower(), tool_name.lower())
    if mapped is None:
        print(json.dumps({}))
        return 0

    try:
        result = decide(mapped, tool_input)
    except Exception as e:
        print(f"[AgentSeed hook] 决策异常：{e}", file=sys.stderr)
        print(json.dumps({}))
        return 0

    if result["deny"]:
        print(f"\n🚫 [AgentSeed] DENY: {result['reason']}\n", file=sys.stderr)
        print(json.dumps({"deny": True, "reason": result["reason"]}, ensure_ascii=False))
        return 0

    if result["require_approval"]:
        print(f"\n⚠️ [AgentSeed] APPROVAL: {result['reason']}\n", file=sys.stderr)
        print(json.dumps({"requireApproval": True, "reason": result["reason"]}, ensure_ascii=False))
        return 0

    if result["warn"]:
        print(f"\n⚠️ [AgentSeed] WARN: {result['warn']}\n", file=sys.stderr)
        print(json.dumps({"warn": result["warn"]}, ensure_ascii=False))
        return 0

    print(json.dumps({}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
