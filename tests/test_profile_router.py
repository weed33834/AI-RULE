"""
Profile Router 测试
验证 profile-router.md 的选择逻辑、互斥关系和能力包白名单。
运行: python tests/test_profile_router.py
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from sync_rules import parse_manifest

PROFILES = ["coding", "conversation", "novel", "interactive-novel", "paper", "agent-builder"]

# profile-router.md 中声明的关键词映射
ROUTER_KEYWORDS = {
    "coding": ["修复", "重构", "测试", "部署", "接口", "Bug", "CI", "代码"],
    "novel": ["写一章", "续写", "人物", "伏笔", "文风", "世界观", "章节"],
    "interactive-novel": ["开始一局", "分支", "存档", "NPC", "回合", "状态", "选项"],
    "agent-builder": ["设计 Agent", "智能体配置", "工具权限", "评估", "部署 Agent"],
    "conversation": ["查询", "对比", "分析", "调研", "总结", "解释"],
}


def select_by_keywords(keywords: list) -> str:
    scores = {p: 0 for p in PROFILES}
    for kw in keywords:
        for pid, pid_kws in ROUTER_KEYWORDS.items():
            if kw in pid_kws:
                scores[pid] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "conversation"


def test_router_md_exists():
    p = REPO_ROOT / "core" / "profile-router.md"
    assert p.exists(), "profile-router.md 不存在"
    print("[PASS] profile-router.md 存在")


def test_single_profile_selection():
    """每个场景只选一个主 profile"""
    cases = [
        (["修复", "接口", "Bug"], "coding"),
        (["写一章", "人物", "章节"], "novel"),
        (["分支", "存档", "NPC", "回合"], "interactive-novel"),
        (["设计 Agent", "工具权限"], "agent-builder"),
        (["查询", "对比"], "conversation"),
    ]
    for kws, expected in cases:
        got = select_by_keywords(kws)
        assert got == expected, f"关键词 {kws} 应选 {expected}，实际 {got}"
        print(f"[PASS] {kws} -> {got}")


def test_mutex_pairwise():
    """互斥关系对称"""
    for pid in PROFILES:
        m = parse_manifest(pid)
        enemies = m.get("mutually_exclusive_with", [])
        for e in enemies:
            em = parse_manifest(e)
            assert pid in em.get("mutually_exclusive_with", []), f"{pid} <-> {e} 不对称"
    print("[PASS] 互斥关系全部对称")


def test_capability_whitelist():
    """forbids 不在 enables 中"""
    for pid in PROFILES:
        m = parse_manifest(pid)
        enables = set(m.get("enables_capabilities", []))
        forbids = set(m.get("forbids_capabilities", []))
        assert not (enables & forbids), f"{pid} enables 和 forbids 重叠: {enables & forbids}"
    print("[PASS] 能力包白名单无矛盾")


def test_router_clauses():
    """router 文档含关键条款"""
    router = (REPO_ROOT / "core" / "profile-router.md").read_text(encoding="utf-8")
    required = ["互斥", "澄清", "优先级", "novel", "interactive-novel", "agent-builder"]
    for kw in required:
        assert kw in router, f"profile-router.md 缺少关键条款: {kw}"
    print("[PASS] router 关键条款齐全")


def test_only_one_main_profile():
    """模拟同时选两个互斥 profile 应被拒绝"""
    pairs = [("novel", "interactive-novel"), ("coding", "novel"), ("agent-builder", "novel")]
    for a, b in pairs:
        m = parse_manifest(a)
        assert b in m.get("mutually_exclusive_with", []), f"{a} 与 {b} 应互斥"
    print("[PASS] 互斥组合不可同时加载")


def run_all():
    print("=" * 60)
    print("Profile Router 测试")
    print("=" * 60)
    tests = [
        test_router_md_exists,
        test_single_profile_selection,
        test_mutex_pairwise,
        test_capability_whitelist,
        test_router_clauses,
        test_only_one_main_profile,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
            return False
    print(f"\n{passed}/{len(tests)} 通过")
    return True


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
