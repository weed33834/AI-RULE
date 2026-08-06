#!/usr/bin/env python3
"""AgentSeed comate PreToolUse Hook 适配器。

Cline 基于 SDK 提供 hooks 接口，协议与 Claude Code 类似：
  - stdin: JSON {"tool_name": "execute_command", "tool_input": {"command": "..."}}
  - stdout: JSON {"deny": true, "reason": "..."} / {}

用户配置方式（项目根 .comate/hooks.json 或 ~/.comate/settings.json）：
{
  "preToolUse": [
    {"command": "python ./adapters/hooks/cline/pre_tool_use.py"}
  ]
}

Cline 工具名约定：
  execute_command / write_to_file / replace_in_file / read_file / search_files / list_files / ask_followup_question / attempt_completion
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

# Cline 工具名归一化映射
TOOL_NAME_MAP = {
    "execute_command": "bash",
    "write_to_file": "write_file",
    "replace_in_file": "edit",
    "create_file": "write_file",
    "read_file": None,
    "search_files": None,
    "list_files": None,
    "ask_followup_question": None,
    "attempt_completion": None,
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

    tool_name = req.get("tool_name") or req.get("toolName", "")
    tool_input = req.get("tool_input") or req.get("toolInput", {})

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
