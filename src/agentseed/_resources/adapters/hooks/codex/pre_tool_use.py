#!/usr/bin/env python3
"""Codex CLI PreToolUse Hook 适配器。

Codex CLI（OpenAI 官方）支持 .codex/hooks.json 配置：
  - stdin: JSON {"tool": "shell", "input": {"command": "..."}}
  - stdout: JSON {"deny": true, "reason": "..."} / {}

用户配置方式（项目根 .codex/hooks.json 或 ~/.codex/config.json）：
{
  "PreToolUse": [
    {"command": "python ./adapters/hooks/codex/pre_tool_use.py"}
  ]
}

Codex 工具名约定：
  shell / write / edit / read / grep / glob / ...
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

# Codex 工具名归一化映射
TOOL_NAME_MAP = {
    "shell": "bash",
    "bash": "bash",
    "terminal": "bash",
    "write": "write_file",
    "edit": "edit",
    "create_file": "write_file",
    "read": None,
    "grep": None,
    "glob": None,
    "search": None,
    "ask": None,
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

    # Codex 字段名比 Claude Code/Cursor 略不同
    tool_name = req.get("tool") or req.get("tool_name", "")
    tool_input = req.get("input") or req.get("tool_input", {})

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
