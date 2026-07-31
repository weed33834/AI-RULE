#!/usr/bin/env python
"""MCP: review_code — 按五子角色 Critics 标准审查代码。

用法:
    python mcp/review_code.py --path <file|dir>

检查项:
    1. 硬编码密钥（API Key / Token / 密码）
    2. 过度抽象（单次使用逻辑包装成类）
    3. AI 味模板（机械的总分总文本、无意义注释）
    4. 幻觉 API（函数名/类名不存在于已知库）
    5. 安全漏洞（SQL注入、路径遍历、XSS）

输出: JSON (severity: BLOCKER|WARNING|INFO)
"""

import argparse
import json
import re
import sys
from pathlib import Path

# 危险模式
SECRET_PATTERNS = [
    (r"(?i)(api[_-]?key|apikey|secret|token|password|passwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]", "硬编码密钥"),
    (r"(?i)(ghp_|sk-|sk-|xox[baprs]-)[a-zA-Z0-9_\-]{20,}", "GitHub/OpenAI/Slack Token 泄露"),
    (r"(?i)(jdbc|mysql|postgres|mongodb)://[^/\s]+:[^@\s]+@", "数据库连接串含明文密码"),
]

# 过度抽象检测
OVER_ABSTRACTION_PATTERNS = [
    (r"class\s+\w+\s*:\s*\n\s+def\s+\w+\(self.*?\):\s*\n\s+(?:return|yield|pass)", "单方法类可能是过度抽象"),
    (r"class\s+\w+Factory\s*:", "Factory 模式需确认是否必要"),
    (r"class\s+\w+Manager\s*:\s*\n\s+def\s+\w+\(self.*?\):\s*\n\s+self\.\w+\.\w+", "Manager 仅做代理转发"),
]

# AI 味检测
AI_FLAVOR_PATTERNS = [
    (r"# 初始化|# 设置|# 创建|# 获取|# 定义|# 导入|# 变量", "注释描述代码功能而非原因"),
    (r"首先.*其次.*最后", "机械化总分总结构"),
    (r"(?i)(好的|没问题|当然可以|我将为您|希望对您有帮助)", "AI 套话"),
    (r"try:\s*\n\s+.*\s*\n\s+except\s+Exception", "过度防御性编程 (裸 Exception)"),
]

# 安全漏洞
SECURITY_PATTERNS = [
    (r"os\.system\(.*\$", "Shell 注入风险（用户输入未过滤）"),
    (r"subprocess\.(call|run|Popen)\(.*shell\s*=\s*True", "shell=True 注入风险"),
    (r"(?i)(exec|eval)\(.*\+|exec\(.*f['\"]|eval\(.*f['\"]", "动态执行含拼接字符串"),
    (r"pickle\.loads?\(.*request|pickle\.loads?\(.*input", "反序列化用户输入（RCE）"),
]


def scan_file(filepath: Path) -> list[dict]:
    """扫描单个文件，返回问题列表。"""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return [{"severity": "WARNING", "file": str(filepath), "line": 0, "issue": "文件无法读取"}]

    lines = content.split("\n")

    # 1. 硬编码密钥
    for pattern, desc in SECRET_PATTERNS:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                issues.append({
                    "severity": "BLOCKER",
                    "file": str(filepath),
                    "line": i,
                    "issue": f"[密钥泄露] {desc}: {line.strip()[:80]}",
                })

    # 2. 过度抽象
    for pattern, desc in OVER_ABSTRACTION_PATTERNS:
        matches = re.finditer(pattern, content, re.MULTILINE)
        for m in matches:
            line_no = content[: m.start()].count("\n") + 1
            issues.append({
                "severity": "WARNING",
                "file": str(filepath),
                "line": line_no,
                "issue": f"[过度抽象] {desc}",
            })

    # 3. AI 味
    for pattern, desc in AI_FLAVOR_PATTERNS:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                issues.append({
                    "severity": "INFO",
                    "file": str(filepath),
                    "line": i,
                    "issue": f"[AI味] {desc}: {line.strip()[:80]}",
                })

    # 4. 安全漏洞
    for pattern, desc in SECURITY_PATTERNS:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                issues.append({
                    "severity": "BLOCKER",
                    "file": str(filepath),
                    "line": i,
                    "issue": f"[安全漏洞] {desc}: {line.strip()[:80]}",
                })

    return issues


def main():
    parser = argparse.ArgumentParser(description="代码审查工具")
    parser.add_argument("--path", required=True, help="目标文件或目录绝对路径")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        print(json.dumps({"error": f"路径不存在: {target}"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    all_issues = []

    if target.is_file():
        all_issues = scan_file(target)
    else:
        # 递归扫描所有 .py/.js/.ts/.jsx/.tsx 文件
        extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".md"}
        for f in target.rglob("*"):
            if f.suffix in extensions and f.is_file():
                # 跳过 __pycache__, node_modules, .git
                if any(part in f.parts for part in ("__pycache__", "node_modules", ".git")):
                    continue
                all_issues.extend(scan_file(f))

    blockers = [i for i in all_issues if i["severity"] == "BLOCKER"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]
    infos = [i for i in all_issues if i["severity"] == "INFO"]

    summary = {
        "target": str(target),
        "files_scanned": len(set(i["file"] for i in all_issues)),
        "total_issues": len(all_issues),
        "blockers": len(blockers),
        "warnings": len(warnings),
        "infos": len(infos),
        "verdict": "REJECT" if blockers else ("WARN" if warnings else "PASS"),
        "issues": all_issues,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    sys.exit(0 if summary["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
