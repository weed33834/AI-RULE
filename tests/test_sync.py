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
    list_profiles, TOOL_OUTPUT, TOOL_CHAR_LIMIT, parse_includes, parse_list_field,
)

PROFILES = ["coding", "conversation", "novel", "interactive-novel", "paper", "agent-builder"]


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
    """list_profiles 返回全部 6 个"""
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
    """全部工具均能生成"""
    rs = build_ruleset("conversation")
    for tool in TOOL_OUTPUT:
        out = write_tool_file(tool, "conversation", rs)
        assert out.exists(), f"{tool} 生成失败"
    print(f"[PASS] {len(TOOL_OUTPUT)} 个工具均能生成")


def test_cursor_frontmatter():
    """cursor .mdc 有 frontmatter"""
    rs = build_ruleset("novel")
    out = write_tool_file("cursor", "novel", rs)
    content = out.read_text(encoding="utf-8")
    assert content.startswith("---"), "cursor 缺 frontmatter"
    assert "alwaysApply: true" in content, "cursor 缺 alwaysApply"
    print("[PASS] cursor frontmatter 正确")


def test_agents_md_output():
    """AGENTS.md 跨工具标准输出正确"""
    rs = build_ruleset("coding")
    out = write_tool_file("agents-md", "coding", rs)
    content = out.read_text(encoding="utf-8")
    assert not content.startswith("---"), "AGENTS.md 不应有 frontmatter"
    assert "CORE LAYER" in content, "AGENTS.md 缺 CORE LAYER"
    assert out.name == "AGENTS.md", f"文件名应为 AGENTS.md，实际: {out.name}"
    print("[PASS] AGENTS.md 输出正确")


def test_comate_mdr_extension():
    """文心快码输出 .mdr 后缀文件"""
    rs = build_ruleset("coding")
    out = write_tool_file("comate", "coding", rs)
    assert out.suffix == ".mdr", f"comate 文件后缀应为 .mdr，实际: {out.suffix}"
    print("[PASS] comate .mdr 后缀正确")


def test_char_limit_warning():
    """字符超限平台会追加警告"""
    rs = build_ruleset("coding")  # coding profile 通常 >10K 字符
    for tool in TOOL_CHAR_LIMIT:
        limit = TOOL_CHAR_LIMIT[tool]
        out = write_tool_file(tool, "coding", rs)
        content = out.read_text(encoding="utf-8")
        if len(content) > limit:
            assert "WARNING" in content or "exceeds" in content, \
                f"{tool} 超限但未追加警告 (content={len(content)}, limit={limit})"
    print("[PASS] 字符超限警告正确")


def test_adapter_override():
    """adapters/<tool>.md 适配器覆盖层生效"""
    rs = build_ruleset("coding")
    # windsurf 有 adapters/windsurf.md
    out = write_tool_file("windsurf", "coding", rs)
    content = out.read_text(encoding="utf-8")
    assert "ADAPTER OVERRIDE" in content, "windsurf 未叠加 adapter 内容"
    assert "Windsurf" in content, "windsurf adapter 内容缺失"
    # lingma 有 adapters/lingma.md
    out = write_tool_file("lingma", "coding", rs)
    content = out.read_text(encoding="utf-8")
    assert "ADAPTER OVERRIDE" in content, "lingma 未叠加 adapter 内容"
    assert "通义灵码" in content, "lingma adapter 内容缺失"
    print("[PASS] adapter 覆盖层生效")


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
        test_agents_md_output,
        test_comate_mdr_extension,
        test_char_limit_warning,
        test_adapter_override,
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
    # 清理：用 coding profile 重新生成所有工具文件，恢复仓库初始状态
    rs = build_ruleset("coding")
    for tool in TOOL_OUTPUT:
        write_tool_file(tool, "coding", rs)
    print("[cleanup] 已用 coding profile 恢复所有生成文件")
    return True


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
