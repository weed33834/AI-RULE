#!/usr/bin/env python
"""规则注入脚本 — 按 Profile + Mode 装配规则摘要，注入到 Sub Agent task 上下文。

用法:
    python scripts/inject_rules.py --profile coding --mode project
    python scripts/inject_rules.py --profile coding --mode autonomous --output task_rules.md

设计依据:
    - core/governance.md: Instruction Budget (P0 ≤5, P1 ≤7, total ≤12)
    - core/agent-modes.md: mode constraints
    - core/attention-budget.md: ABA:FA/HP/CP 标记
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── 规则源 ────────────────────────────────────────────
SOURCE_FILES = {
    "governance": ROOT / "core" / "governance.md",
    "interaction": ROOT / "core" / "interaction.md",
    "agent_modes": ROOT / "core" / "agent-modes.md",
    "profile": None,  # 运行时填充
    "skills": None,   # 运行时填充
}

# ── MCP 工具注册表 ──
MCP_TOOLS = {
    "validate_codebase": {
        "path": str(ROOT / "mcp" / "validate_codebase.py"),
        "description": "按编码标准（ruff/mypy/pytest）校验代码库",
        "side_effect": "read-only",
        "usage": "python mcp/validate_codebase.py --path <dir> [--checks ruff,mypy,pytest]",
    },
    "review_code": {
        "path": str(ROOT / "mcp" / "review_code.py"),
        "description": "按五子角色 Critics 标准审查代码",
        "side_effect": "read-only",
        "usage": "python mcp/review_code.py --path <file|dir>",
    },
    "git_precommit_check": {
        "path": str(ROOT / "mcp" / "git_precommit_check.py"),
        "description": "Git 提交前检查（敏感文件/密钥/大文件）",
        "side_effect": "read-only",
        "usage": "python mcp/git_precommit_check.py",
    },
    "generate_tests": {
        "path": str(ROOT / "mcp" / "generate_tests.py"),
        "description": "为 Python 代码生成 pytest 测试骨架",
        "side_effect": "file-write",
        "usage": "python mcp/generate_tests.py --path <file.py> --framework pytest",
    },
}


def extract_anchor_block(text: str, label: str) -> str:
    """提取 <!-- LABEL:ANCHOR-START --> ... <!-- /LABEL:ANCHOR-END --> 块。"""
    import re

    pattern = rf"<!--\s*{label}:ANCHOR-START\s*-->(.*?)<!--\s*/{label}:ANCHOR-END\s*-->"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_rules_from_markdown(text: str) -> list[dict[str, str]]:
    """从 Markdown 文本中提取规则列表。"""
    rules = []
    lines = text.split("\n")
    current_rule = None

    for line in lines:
        line = line.strip()
        # 识别规则行（- 开头或数字. 开头或 // Rationale 注释）
        if line.startswith("- ") and len(line) > 3:
            content = line[2:].strip()
            # 跳过纯注释行
            if content.startswith("//") or content.startswith("Rationale"):
                continue
            current_rule = {"text": content, "rationale": "", "level": "P2"}
            rules.append(current_rule)
        elif line.startswith("// Rationale:") and current_rule:
            current_rule["rationale"] = line[len("// Rationale:") :].strip()

    return rules


def assemble_rules(profile: str, mode: str) -> str:
    """按优先级装配规则片段。"""
    profile_agents = ROOT / "personas" / profile / "AGENTS.md"

    if not profile_agents.exists():
        return f"<!-- ERROR: Profile {profile} not found -->"

    # 读取源文件
    governance_text = SOURCE_FILES["governance"].read_text(encoding="utf-8")
    interaction_text = SOURCE_FILES["interaction"].read_text(encoding="utf-8")
    agent_modes_text = SOURCE_FILES["agent_modes"].read_text(encoding="utf-8")
    profile_text = profile_agents.read_text(encoding="utf-8")

    # 提取 P0/P1 锚定块
    p0_block = extract_anchor_block(governance_text, "P0")
    p1_block = extract_anchor_block(interaction_text, "P1")

    # 提取 P0 规则（精简到 ≤5 条）
    p0_rules = parse_rules_from_markdown(p0_block)

    # 手动精炼为 5 条核心 P0
    p0_core = [
        "**禁止硬编码密钥**：API Keys / Token / 密码必须用环境变量或 .env，绝不写入源码",
        "**禁止编造事实**：不确定时问用户，不猜测；标注来源 URL + 日期",
        "**最小变更**：只改用户指定的文件，禁止顺手优化无关代码",
        "**失败熔断**：同一 Bug 连续失败 2 次立刻停止，输出故障报告并请求接管",
        "**MCP 红线**：MCP 安装/配置由用户手动完成，AI 只输出命令和 JSON 供审阅",
    ]

    # P1 规则（精炼到 ≤5 条）
    p1_core = [
        "**意图归一化**：先解析用户指令为 {动作+目标+约束+范围}，歧义时先澄清再动手",
        "**去套话**：禁止'好的、没问题、我将为您'等开场/结尾，直接输出结论",
        "**输出语言**：用用户语言回复；代码注释写'为什么'不写'什么'",
        "**多轮连贯**：10 轮前确认的信息不重复问；纠正过的错误不重犯",
        "**主动边界**：主动做错误预警/风险提示/信息补充；禁止修改未指定文件/替用户做决定",
    ]

    # P2 Profile 规则（coding 专用，≤5 条）
    p2_rules = [
        "**五子角色**：Architect→Engineer→Critic→Verifier→Final，逐角色执行不可跳过",
        "**技能获取五层**：标准库→pip/npm→注册表→厂商官方仓库→受限搜索",
        "**编码标准**：Python 3.12+ async/await + type hints；httpx > requests；ruff > flake8",
        "**Git SOP**：提交前 git status + git diff；git add 具体文件禁止 -A；Conventional Commits",
        "**联网优先**：涉及新框架/新 API/版本变更时，先搜索最新文档再编码",
    ]

    # Mode 约束（来自 agent-modes.md）
    mode_constraints = {
        "task": [
            "不生成计划文档，不拆分子任务",
            "一次性给出最终结果",
            "执行失败 1 次即报告，不重试",
        ],
        "project": [
            "执行前输出结构化计划（目标→子任务→产出物→检查点）",
            "每个检查点等待用户确认后继续",
            "同一子任务失败重试上限 2 次",
        ],
        "autonomous": [
            "执行前输出完整计划，用户一次确认后全自动执行",
            "每 10 步输出进度摘要",
            "同一子任务失败重试上限 3 次，达到后降级为 project 模式",
        ],
    }

    mode_rules = mode_constraints.get(mode, mode_constraints["task"])

    # MCP 工具摘要
    mcp_summary = "\n".join(
        f"- **{name}**: {info['description']} (`{info['usage']}`)"
        for name, info in MCP_TOOLS.items()
    )

    # ── 装配输出 ──
    output = f"""<!--
  规则注入上下文 — AgentSeed v2.0
  Profile: {profile} | Mode: {mode}
  生成时间: {Path('.').resolve()}
  以下规则已注入上下文，请在执行时严格遵守。
  来源: core/governance.md + core/interaction.md + personas/{profile}/AGENTS.md
-->

## P0 安全规则（FA — 不可压缩）

{chr(10).join(f"{i+1}. {r}" for i, r in enumerate(p0_core))}

## P1 交互规则（HP — 核心约束）

{chr(10).join(f"{i+1}. {r}" for i, r in enumerate(p1_core))}

## P2 Profile 规则（HP — {profile} 专用）

{chr(10).join(f"{i+1}. {r}" for i, r in enumerate(p2_rules))}

## 模式约束（{mode} 模式）

{chr(10).join(f"{i+1}. {r}" for i, r in enumerate(mode_rules))}

## 可用 MCP 工具

{mcp_summary}

## Agent 可执行指令

- ABA 压缩: 上下文窗口 >70% 时，压缩 P2 示例保留核心约束，P0/P1 绝不压缩
- RT 推理: {mode} 模式默认推理深度为 {"DEEP" if mode == "autonomous" else "STANDARD" if mode == "project" else "QUICK"}
- 模式切换: 用户可显式切换 switch mode to <task|project|autonomous>，降级不可逆
"""

    return output


def main():
    parser = argparse.ArgumentParser(description="AgentSeed 规则注入脚本")
    parser.add_argument("--profile", default="coding", help="Profile ID (coding/conversation/...)")
    parser.add_argument("--mode", default="project", choices=["task", "project", "autonomous"], help="Agent 模式")
    parser.add_argument("--output", default=None, help="输出文件路径（默认输出到 stdout）")
    args = parser.parse_args()

    rules_text = assemble_rules(args.profile, args.mode)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(rules_text, encoding="utf-8")
        print(f"规则摘要已写入: {output_path} ({len(rules_text.splitlines())} 行)")
    else:
        print(rules_text)


if __name__ == "__main__":
    main()
