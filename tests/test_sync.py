"""
Sync 脚本测试
验证 sync_rules.py 的解析、引用展开、生成和漂移检测。
运行: python tests/test_sync.py
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from sync_rules import (
    parse_manifest, build_ruleset, write_tool_file,
    list_profiles, TOOL_OUTPUT, parse_includes, parse_list_field,
)

PROFILES = ["coding", "conversation", "novel", "interactive-novel", "agent-builder"]


def test_parse_manifest_structure():
    """parse_manifest 返回正确结构"""
    for pid in PROFILES:
        m = parse_manifest(pid)
        assert "includes" in m
        assert "core" in m["includes"]
        assert "profile" in m["includes"]
        assert len(m["includes"]["core"]) > 0
        assert len(m["includes"]["profile"]) > 0
    print("[PASS] manifest 解析结构正确")


def test_list_profiles():
    """list_profiles 返回全部 5 个"""
    profiles = list_profiles()
    assert set(profiles) == set(PROFILES), f"profile 列表不匹配: {profiles}"
    print(f"[PASS] list_profiles: {profiles}")


def test_expand_refs_no_unresolved():
    """生成的规则集无未解析引用"""
    for pid in PROFILES:
        ruleset = build_ruleset(pid)
        assert "[unresolved ref]" not in ruleset, f"{pid}: 存在未解析引用"
        assert "[missing]" not in ruleset, f"{pid}: 存在缺失引用"
    print("[PASS] 无未解析/缺失引用")


def test_three_layers_present():
    """规则集含 core/profile/skills 三层"""
    for pid in PROFILES:
        rs = build_ruleset(pid)
        assert "CORE LAYER" in rs, f"{pid}: 缺 core 层"
        assert "PROFILE LAYER" in rs, f"{pid}: 缺 profile 层"
        assert "SKILLS LAYER" in rs, f"{pid}: 缺 skills 层"
    print("[PASS] 三层结构完整")


def test_header_present():
    """生成文件含禁止编辑标记"""
    rs = build_ruleset("coding")
    assert "禁止手工编辑" in rs
    assert "profile: coding" in rs
    assert "generated:" in rs
    print("[PASS] 生成头标记完整")


def test_all_tools_output():
    """5 个工具均能生成"""
    rs = build_ruleset("conversation")
    for tool in TOOL_OUTPUT:
        out = write_tool_file(tool, "conversation", rs)
        assert out.exists(), f"{tool} 生成失败"
    print("[PASS] 5 个工具均能生成")


def test_cursor_frontmatter():
    """cursor .mdc 有 frontmatter"""
    rs = build_ruleset("novel")
    out = write_tool_file("cursor", "novel", rs)
    content = out.read_text(encoding="utf-8")
    assert content.startswith("---"), "cursor 缺 frontmatter"
    assert "alwaysApply: true" in content, "cursor 缺 alwaysApply"
    print("[PASS] cursor frontmatter 正确")


def test_drift_overwritten():
    """手改会被重新生成覆盖"""
    rs = build_ruleset("coding")
    out = write_tool_file("claude-code", "coding", rs)
    original = out.read_text(encoding="utf-8")
    out.write_text(original + "<!-- TAMPER -->", encoding="utf-8")
    rs2 = build_ruleset("coding")
    write_tool_file("claude-code", "coding", rs2)
    after = out.read_text(encoding="utf-8")
    assert "TAMPER" not in after, "手改未被覆盖"
    print("[PASS] 漂移被覆盖")


def test_parse_list_field():
    """parse_list_field 解析正确"""
    text = """
enables_capabilities:
  - research
  - testing
forbids_capabilities:
  - game-engine
"""
    enables = parse_list_field(text, "enables_capabilities")
    forbids = parse_list_field(text, "forbids_capabilities")
    assert enables == ["research", "testing"], f"enables 解析错: {enables}"
    assert forbids == ["game-engine"], f"forbids 解析错: {forbids}"
    print("[PASS] parse_list_field 正确")


def test_parse_includes():
    """parse_includes 解析正确"""
    text = """
includes:
  core:
    - core/governance.md
  profile:
    - profiles/coding/AGENTS.md
enables_capabilities:
  - research
"""
    inc = parse_includes(text)
    assert inc["core"] == ["core/governance.md"], f"core 解析错: {inc['core']}"
    assert inc["profile"] == ["profiles/coding/AGENTS.md"], f"profile 解析错: {inc['profile']}"
    print("[PASS] parse_includes 正确")


def run_all():
    print("=" * 60)
    print("Sync 脚本测试")
    print("=" * 60)
    tests = [
        test_parse_manifest_structure,
        test_list_profiles,
        test_expand_refs_no_unresolved,
        test_three_layers_present,
        test_header_present,
        test_all_tools_output,
        test_cursor_frontmatter,
        test_drift_overwritten,
        test_parse_list_field,
        test_parse_includes,
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
