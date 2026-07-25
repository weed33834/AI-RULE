#!/usr/bin/env python
"""MCP: git_precommit_check — Git 提交前检查。

用法:
    python mcp/git_precommit_check.py [--repo <path>]

检查项:
    1. 未追踪的临时文件 (.tmp/.bak/.zip/.log)
    2. .git 目录嵌套
    3. 密钥泄露扫描
    4. 超过 5MB 的大文件
    5. 变更中的 .env 文件

输出: JSON
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# 临时文件模式
TEMP_PATTERNS = [r"\.tmp$", r"\.bak$", r"\.zip$", r"\.tar\.gz$", r"\.log$", r"__pycache__", r"\.pyc$", r"\.DS_Store$", r"Thumbs\.db$"]

# 密钥泄露模式
SECRET_KEY_PATTERNS = [
    r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
    r"(?i)(ghp_|sk-|xox[baprs]-)[a-zA-Z0-9_\-]{20,}",
    r"(?i)-----BEGIN (RSA |EC )?PRIVATE KEY-----",
]


def run_git(cmd: list[str], repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + cmd, cwd=str(repo), capture_output=True, text=True, timeout=30)


def check_temp_files(repo: Path) -> list[dict]:
    """检查未追踪的临时文件。"""
    issues = []
    # git status --short
    result = run_git(["status", "--short"], repo)
    for line in result.stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        # ?? = untracked, M = modified, A = added
        status = line[:2]
        filepath = line[3:].strip()
        for pattern in TEMP_PATTERNS:
            if re.search(pattern, filepath):
                issues.append({
                    "severity": "WARNING",
                    "file": filepath,
                    "issue": f"临时文件不应提交: {filepath}",
                })
                break
    return issues


def check_git_nested(repo: Path) -> list[dict]:
    """检查 .git 目录嵌套。"""
    issues = []
    for item in repo.rglob(".git"):
        if item.is_dir() and item.resolve() != (repo / ".git").resolve():
            issues.append({
                "severity": "BLOCKER",
                "file": str(item.parent.relative_to(repo)),
                "issue": "嵌套 .git 目录，可能是未清理的子仓库",
            })
    return issues


def check_secrets_in_diff(repo: Path) -> list[dict]:
    """检查变更中是否包含密钥。"""
    issues = []
    result = run_git(["diff", "--cached"], repo)
    for pattern in SECRET_KEY_PATTERNS:
        for match in re.finditer(pattern, result.stdout, re.MULTILINE):
            line_no = result.stdout[: match.start()].count("\n") + 1
            issues.append({
                "severity": "BLOCKER",
                "file": "git diff --cached",
                "line": line_no,
                "issue": f"变更中包含疑似密钥: {match.group(0)[:60]}",
            })
    return issues


def check_large_files(repo: Path) -> list[dict]:
    """检查超过 5MB 的文件。"""
    issues = []
    result = run_git(["diff", "--cached", "--stat"], repo)
    for line in result.stdout.split("\n"):
        if "|" not in line:
            continue
        parts = line.split("|")
        if len(parts) < 2:
            continue
        stat_part = parts[1].strip()
        # 查找 Bin 或 数字 + 单位
        size_match = re.search(r"Bin\s+(\d+)\s+bytes", stat_part)
        if size_match:
            size_bytes = int(size_match.group(1))
            if size_bytes > 5 * 1024 * 1024:
                issues.append({
                    "severity": "WARNING",
                    "file": parts[0].strip(),
                    "issue": f"文件过大 ({size_bytes / 1024 / 1024:.1f}MB)，超过 5MB 上限",
                })
    return issues


def check_env_files(repo: Path) -> list[dict]:
    """检查变更中的 .env 文件。"""
    issues = []
    result = run_git(["diff", "--cached", "--name-only"], repo)
    for line in result.stdout.split("\n"):
        line = line.strip()
        if line.endswith(".env") or ".env." in line:
            issues.append({
                "severity": "BLOCKER",
                "file": line,
                "issue": ".env 文件不应提交到仓库（应加入 .gitignore）",
            })
    return issues


def main():
    parser = argparse.ArgumentParser(description="Git 提交前检查")
    parser.add_argument("--repo", default=".", help="仓库路径")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()

    if not (repo / ".git").exists():
        print(json.dumps({"error": f"不是 Git 仓库: {repo}", "verdict": "SKIP"}, ensure_ascii=False, indent=2))
        sys.exit(0)

    all_issues = []
    all_issues.extend(check_temp_files(repo))
    all_issues.extend(check_git_nested(repo))
    all_issues.extend(check_secrets_in_diff(repo))
    all_issues.extend(check_large_files(repo))
    all_issues.extend(check_env_files(repo))

    blockers = [i for i in all_issues if i["severity"] == "BLOCKER"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]

    summary = {
        "repo": str(repo),
        "total_issues": len(all_issues),
        "blockers": len(blockers),
        "warnings": len(warnings),
        "verdict": "REJECT" if blockers else ("WARN" if warnings else "PASS"),
        "issues": all_issues,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.exit(0 if summary["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
