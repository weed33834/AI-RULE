"""
结构验证测试
验证 core、profiles、manifests 的完整性、引用一致性和互斥关系。
运行: python tests/test_structure.py
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from sync_rules import parse_manifest, list_profiles, TOOL_OUTPUT

CORE_FILES = ["governance.md", "interaction.md", "profile-router.md", "language-mediation.md"]
PROFILES = ["coding", "conversation", "novel", "interactive-novel", "paper", "agent-builder"]
MUTEX = {
    "coding": ["novel", "interactive-novel"],
    "conversation": ["novel", "interactive-novel", "agent-builder"],
    "novel": ["coding", "conversation", "interactive-novel", "agent-builder", "paper"],
    "interactive-novel": ["coding", "conversation", "novel", "agent-builder", "paper"],
    "paper": ["novel", "interactive-novel"],
    "agent-builder": ["conversation", "novel", "interactive-novel"],
}


def test_core_exists():
    """core 层文件齐全"""
    for f in CORE_FILES:
        p = REPO_ROOT / "core" / f
        assert p.exists(), f"core 文件缺失: {p}"
    print("[PASS] core 层文件齐全")


def test_profiles_exist():
    """每个 profile 有 AGENTS.md 和 docs/"""
    for pid in PROFILES:
        agents = REPO_ROOT / "profiles" / pid / "AGENTS.md"
        docs = REPO_ROOT / "profiles" / pid / "docs"
        assert agents.exists(), f"{pid}: AGENTS.md 缺失"
        assert docs.is_dir(), f"{pid}: docs/ 目录缺失"
        file_count = sum(1 for _ in docs.rglob("*") if _.is_file())
        assert file_count > 0, f"{pid}: docs/ 为空"
        print(f"  {pid}: AGENTS.md + docs/ ({file_count} 文件) OK")
    print("[PASS] 6 个 Profile 结构完整")


def test_manifests_exist():
    """每个 profile 有 manifest"""
    for pid in PROFILES:
        m = REPO_ROOT / "manifests" / f"{pid}.yaml"
        assert m.exists(), f"manifest 缺失: {pid}"
    print("[PASS] 5 个 manifest 齐全")


def test_manifest_references():
    """manifest 引用的文件都存在"""
    for pid in PROFILES:
        manifest = parse_manifest(pid)
        for section, files in manifest["includes"].items():
            for f in files:
                p = REPO_ROOT / f
                assert p.exists(), f"{pid} manifest 引用不存在: {section}/{f}"
        print(f"  {pid}: {sum(len(v) for v in manifest['includes'].values())} 个引用全部存在")
    print("[PASS] manifest 引用完整")


def test_mutex():
    """互斥关系对称且一致"""
    for pid, enemies in MUTEX.items():
        manifest = parse_manifest(pid)
        manifest_enemies = set(manifest.get("mutually_exclusive_with", []))
        expected = set(enemies)
        assert manifest_enemies == expected, f"{pid} 互斥不一致: {manifest_enemies} != {expected}"
    print("[PASS] 互斥关系一致")


def test_sync_all_profiles():
    """sync_rules 能为每个 profile 生成 claude-code 入口"""
    from sync_rules import build_ruleset, write_tool_file
    for pid in PROFILES:
        ruleset = build_ruleset(pid)
        assert len(ruleset) > 500, f"{pid}: 规则集过小 ({len(ruleset)} 字符)"
        assert "CORE LAYER" in ruleset, f"{pid}: 缺少 core 层"
        assert "PROFILE LAYER" in ruleset, f"{pid}: 缺少 profile 层"
        assert "[missing]" not in ruleset, f"{pid}: 存在缺失引用"
        out = write_tool_file("claude-code", pid, ruleset)
        assert out.exists(), f"{pid}: 写入失败"
        print(f"  {pid}: {len(ruleset)} 字符 -> {out.name}")
    print("[PASS] 6 个 Profile 均可同步生成")


def test_generated_drift():
    """生成文件带禁止编辑标记"""
    from sync_rules import build_ruleset
    ruleset = build_ruleset("coding")
    assert "禁止手工编辑" in ruleset, "缺少禁止编辑标记"
    assert "profile: coding" in ruleset, "缺少 profile 标识"
    print("[PASS] 生成文件标记完整")


def run_all():
    print("=" * 60)
    print("结构验证测试")
    print("=" * 60)
    tests = [
        test_core_exists,
        test_profiles_exist,
        test_manifests_exist,
        test_manifest_references,
        test_mutex,
        test_sync_all_profiles,
        test_generated_drift,
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
