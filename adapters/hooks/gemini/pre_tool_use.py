#!/usr/bin/env python3
"""Gemini CLI PreToolUse Hook 适配器。

Gemini CLI（2026 版）支持 12 个生命周期事件，PreToolUse 与 Claude Code 协议基本一致：
  - stdin: JSON {"toolName": "Bash", "toolInput": {"command": "..."}, "eventName": "PreToolUse"}
  - stdout: JSON {"deny": true, "reason": "..."} / {"requireApproval": true} / {}

用户配置方式（项目根 .gemini/hooks.json 或 ~/.gemini/settings.json）：
{
  "PreToolUse": [
    {"command": "python ./adapters/hooks/gemini/pre_tool_use.py"}
  ]
}
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

# Gemini CLI 工具名归一化映射
TOOL_NAME_MAP = {
    "bash": "bash",
    "shell": "bash",
    "write_file": "write_file",
    "edit_file": "edit",
    "read_file": None,
    "list_directory": None,
    "search_file_content": None,
    "web_search": None,
    "web_fetch": None,
    "ask_user": None,
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

    tool_name = req.get("toolName") or req.get("tool_name", "")
    tool_input = req.get("toolInput") or req.get("tool_input", {})

    mapped = TOOL_NAME_MAP.get(tool_name.lower(), tool_name.lower())
    if mapped is None:
        print(json.dumps({}))
        return 0

    try:
        result = decide(mapped, tool_input)
    except Exception as e:
        print(f"[Rule Hub hook] 决策异常：{e}", file=sys.stderr)
        print(json.dumps({}))
        return 0

    if result["deny"]:
        print(f"\n🚫 [Rule Hub] DENY: {result['reason']}\n", file=sys.stderr)
        print(json.dumps({"deny": True, "reason": result["reason"]}, ensure_ascii=False))
        return 0

    if result["require_approval"]:
        print(f"\n⚠️ [Rule Hub] APPROVAL: {result['reason']}\n", file=sys.stderr)
        print(json.dumps({"requireApproval": True, "reason": result["reason"]}, ensure_ascii=False))
        return 0

    if result["warn"]:
        print(f"\n⚠️ [Rule Hub] WARN: {result['warn']}\n", file=sys.stderr)
        print(json.dumps({"warn": result["warn"]}, ensure_ascii=False))
        return 0

    print(json.dumps({}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
