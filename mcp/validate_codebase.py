#!/usr/bin/env python
"""MCP: validate_codebase — 按编码标准校验代码库。

用法:
    python mcp/validate_codebase.py --path <dir> [--checks ruff,mypy,pytest]
    python mcp/validate_codebase.py --path . --checks ruff,mypy --timeout 60

输出: JSON (severity: blocker|warning|info)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_check(name: str, cmd: list[str], cwd: Path, timeout: int = 60) -> dict[str, Any]:
    """运行单个检查，返回结构化结果。"""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        issues = []
        for line in result.stdout.split("\n"):
            line = line.strip()
            if not line:
                continue
            # ruff 格式: file:line:col: CODE message
            # mypy 格式: file:line: error: message
            # pytest 格式: FAILED file::test_name - message
            severity = "warning"
            if "error" in line.lower() or "E" in line[:10]:
                severity = "blocker"
            elif "warning" in line.lower() or "W" in line[:10]:
                severity = "warning"
            else:
                severity = "info"

            issues.append({
                "severity": severity,
                "message": line,
            })

        return {
            "check": name,
            "command": " ".join(cmd),
            "exit_code": result.returncode,
            "issues_count": len(issues),
            "issues": issues,
            "stderr": result.stderr[:500] if result.stderr else "",
            "status": "PASS" if result.returncode == 0 else "FAIL",
        }

    except subprocess.TimeoutExpired:
        return {
            "check": name,
            "command": " ".join(cmd),
            "exit_code": -1,
            "issues_count": 1,
            "issues": [{"severity": "blocker", "message": f"检查超时 (>{timeout}s)"}],
            "stderr": "",
            "status": "TIMEOUT",
        }
    except FileNotFoundError:
        return {
            "check": name,
            "command": " ".join(cmd),
            "exit_code": -1,
            "issues_count": 1,
            "issues": [{"severity": "info", "message": f"工具未安装: {cmd[0]}"}],
            "stderr": "",
            "status": "SKIPPED",
        }


def main():
    parser = argparse.ArgumentParser(description="代码库校验工具")
    parser.add_argument("--path", required=True, help="目标代码目录绝对路径")
    parser.add_argument("--checks", default="ruff,mypy,pytest", help="逗号分隔的检查项")
    parser.add_argument("--timeout", type=int, default=60, help="每个检查超时秒数")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        print(json.dumps({"error": f"路径不存在: {target}"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    checks = [c.strip() for c in args.checks.split(",")]
    results = []

    check_commands = {
        "ruff": ["ruff", "check", "."],
        "mypy": ["mypy", "--ignore-missing-imports", "."],
        "pytest": ["pytest", "--tb=short", "-q"],
    }

    for check_name in checks:
        if check_name in check_commands:
            cmd = check_commands[check_name]
        else:
            results.append({
                "check": check_name,
                "status": "SKIPPED",
                "issues_count": 1,
                "issues": [{"severity": "info", "message": f"未知检查项: {check_name}"}],
            })
            continue

        result = run_check(check_name, cmd, target, args.timeout)
        results.append(result)

    summary = {
        "target": str(target),
        "total_checks": len(results),
        "passed": sum(1 for r in results if r.get("status") == "PASS"),
        "failed": sum(1 for r in results if r.get("status") == "FAIL"),
        "skipped": sum(1 for r in results if r.get("status") in ("SKIPPED", "TIMEOUT")),
        "results": results,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
