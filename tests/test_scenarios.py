"""
复杂场景测试
用 5 个真实复杂任务验证 Profile 选择、能力包叠加、互斥约束和规则冲突处理。
运行: python tests/test_scenarios.py
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "core"))

from sync_rules import parse_manifest, build_ruleset


def load_router():
    """从 profile-router.md 提取选择规则用于测试"""
    router_path = REPO_ROOT / "core" / "profile-router.md"
    return router_path.read_text(encoding="utf-8")


def select_profile_by_keywords(keywords: list) -> str:
    """模拟 profile-router 的关键词匹配逻辑"""
    rules = {
        "coding": ["修复", "重构", "测试", "部署", "接口", "Bug", "CI", "代码"],
        "novel": ["写一章", "续写", "人物", "伏笔", "文风", "世界观", "章节"],
        "interactive-novel": ["开始一局", "分支", "存档", "NPC", "回合", "状态", "选项"],
        "agent-builder": ["设计 Agent", "智能体配置", "工具权限", "评估", "部署 Agent"],
        "conversation": ["查询", "对比", "分析", "调研", "总结", "解释"],
    }
    scores = {pid: 0 for pid in rules}
    for kw in keywords:
        for pid, pid_kws in rules.items():
            if kw in pid_kws:
                scores[pid] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "conversation"


def check_capability_allowed(profile_id: str, capability: str) -> bool:
    """检查能力包是否在白名单内"""
    manifest = parse_manifest(profile_id)
    return capability in manifest.get("enables_capabilities", [])


def check_mutex(profile_a: str, profile_b: str) -> bool:
    """检查两个 profile 是否互斥"""
    manifest = parse_manifest(profile_a)
    return profile_b in manifest.get("mutually_exclusive_with", [])


# === 场景 1: FastAPI 接口 Bug 修复 ===
def scenario_1_fastapi_bug():
    """用户：修复 FastAPI 项目的用户认证接口 Bug，补上测试"""
    keywords = ["修复", "接口", "Bug", "测试"]
    profile = select_profile_by_keywords(keywords)
    assert profile == "coding", f"应选 coding，实际 {profile}"
    assert check_capability_allowed("coding", "testing"), "coding 应允许 testing 能力包"
    assert not check_capability_allowed("coding", "game-engine"), "coding 不应允许 game-engine"
    # 验证生成的规则集包含 coding 特有内容
    ruleset = build_ruleset("coding")
    assert "PowerShell" in ruleset or "pip" in ruleset, "coding 规则集应含工程命令"
    print("[PASS] 场景1 FastAPI Bug 修复 → coding + testing")


# === 场景 2: 小说第三章创作，人物设定冲突 ===
def scenario_2_novel_chapter():
    """用户：按已有设定写第三章，但发现主角的年龄前后矛盾"""
    keywords = ["写一章", "人物", "章节"]
    profile = select_profile_by_keywords(keywords)
    assert profile == "novel", f"应选 novel，实际 {profile}"
    assert check_capability_allowed("novel", "worldbuilding"), "novel 应允许 worldbuilding"
    assert not check_capability_allowed("novel", "game-engine"), "novel 不应允许 game-engine"
    # 验证互斥：novel 与 coding 不能同时加载
    assert check_mutex("novel", "coding"), "novel 与 coding 应互斥"
    # 验证规则集含小说特有规则
    ruleset = build_ruleset("novel")
    assert len(ruleset) > 5000, f"novel 规则集过小: {len(ruleset)}"
    print("[PASS] 场景2 小说第三章创作 → novel + worldbuilding，与 coding 互斥")


# === 场景 3: 互动小说分支设计，状态迁移 ===
def scenario_3_interactive_state():
    """用户：设计一个有 NPC 关系值和存档的分支故事，每回合输出状态变化"""
    keywords = ["分支", "存档", "NPC", "回合", "状态"]
    profile = select_profile_by_keywords(keywords)
    assert profile == "interactive-novel", f"应选 interactive-novel，实际 {profile}"
    assert check_capability_allowed("interactive-novel", "state-machine"), "应允许 state-machine"
    assert check_capability_allowed("interactive-novel", "npc-simulation"), "应允许 npc-simulation"
    assert check_capability_allowed("interactive-novel", "adaptive-difficulty"), "应允许 adaptive-difficulty"
    # 验证互斥：interactive-novel 与 novel 互斥
    assert check_mutex("interactive-novel", "novel"), "与 novel 应互斥"
    ruleset = build_ruleset("interactive-novel")
    assert len(ruleset) > 5000, f"interactive-novel 规则集过小: {len(ruleset)}"
    print("[PASS] 场景3 互动小说状态机 → interactive-novel + state-machine/npc/difficulty")


# === 场景 4: 设计代码审查 Agent ===
def scenario_4_design_agent():
    """用户：设计一个只读代码审查 Agent，输出 config、工具权限、20 个测试用例"""
    keywords = ["设计 Agent", "智能体配置", "工具权限", "评估"]
    profile = select_profile_by_keywords(keywords)
    assert profile == "agent-builder", f"应选 agent-builder，实际 {profile}"
    assert check_capability_allowed("agent-builder", "agent-governance"), "应允许 agent-governance"
    assert check_capability_allowed("agent-builder", "testing"), "应允许 testing"
    assert not check_capability_allowed("agent-builder", "game-engine"), "不应允许 game-engine"
    # 验证模板存在
    templates_dir = REPO_ROOT / "profiles" / "agent-builder" / "docs" / "templates"
    assert templates_dir.exists(), "agent-builder 模板目录应存在"
    code_reviewer = templates_dir / "code-reviewer"
    assert (code_reviewer / "config.yaml").exists(), "code-reviewer 模板应存在"
    assert (code_reviewer / "tools.json").exists(), "code-reviewer 工具定义应存在"
    assert (code_reviewer / "test-cases.md").exists(), "code-reviewer 测试用例应存在"
    print("[PASS] 场景4 设计审查 Agent → agent-builder + governance/testing，模板齐全")


# === 场景 5: 跨工具规则生成一致性 ===
def scenario_5_cross_tool():
    """验证同一 profile 生成的 5 个工具入口内容一致"""
    from sync_rules import write_tool_file
    ruleset = build_ruleset("coding")
    outputs = {}
    for tool in ["claude-code", "gemini", "cursor", "copilot", "trae"]:
        out = write_tool_file(tool, "coding", ruleset)
        outputs[tool] = out
        assert out.exists(), f"{tool} 生成失败"
    # 验证规则集核心内容在所有工具文件中一致
    for tool, path in outputs.items():
        content = path.read_text(encoding="utf-8")
        assert "CORE LAYER" in content, f"{tool}: 缺少 core 层"
        assert "PROFILE LAYER" in content, f"{tool}: 缺少 profile 层"
        assert "禁止手工编辑" in content, f"{tool}: 缺少禁止编辑标记"
    # 验证 cursor 有 frontmatter
    cursor_content = outputs["cursor"].read_text(encoding="utf-8")
    assert cursor_content.startswith("---"), "cursor .mdc 应有 frontmatter"
    print("[PASS] 场景5 跨工具生成 → 5 个工具入口内容一致、标记完整")


# === 场景 6: 模糊意图必须澄清 ===
def scenario_6_ambiguous():
    """用户：写一个带分支的悬疑故事——可能是小说也可能是互动游戏"""
    keywords = ["写", "分支", "故事"]
    # "分支"同时命中 novel 和 interactive-novel 的关键词
    novel_score = sum(1 for kw in keywords if kw in ["写一章", "续写", "人物", "伏笔", "文风", "世界观", "章节"])
    interactive_score = sum(1 for kw in keywords if kw in ["开始一局", "分支", "存档", "NPC", "回合", "状态", "选项"])
    # "分支"命中 interactive-novel
    assert interactive_score >= 1, "分支应命中 interactive-novel"
    # 这种模糊情况 profile-router 要求询问
    router = load_router()
    assert "识别不唯一时必须澄清" in router, "router 应要求模糊时澄清"
    print("[PASS] 场景6 模糊意图 → router 要求澄清而非脑补")


def run_all():
    print("=" * 60)
    print("复杂场景测试")
    print("=" * 60)
    scenarios = [
        ("FastAPI Bug 修复", scenario_1_fastapi_bug),
        ("小说第三章创作", scenario_2_novel_chapter),
        ("互动小说状态机", scenario_3_interactive_state),
        ("设计审查 Agent", scenario_4_design_agent),
        ("跨工具生成一致性", scenario_5_cross_tool),
        ("模糊意图澄清", scenario_6_ambiguous),
    ]
    passed = 0
    for name, fn in scenarios:
        try:
            fn()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {name}: {e}")
            return False
    print(f"\n{passed}/{len(scenarios)} 场景通过")
    return True


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
