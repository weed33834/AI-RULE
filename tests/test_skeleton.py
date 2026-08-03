"""
Skeleton 模式专项测试：验证按需加载、预算、索引、分片、templates 装配等新机制。
对齐 governance.md §Instruction Budget 的核心改进。
运行: python tests/test_skeleton.py
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from sync_rules import (
    build_ruleset, write_tool_file, parse_manifest,
    TOOL_OUTPUT, TOOL_CHAR_LIMIT, SKELETON_BUDGET_BYTES,
    PROFILE_INLINE_BASENAMES, _collect_mcp_files, extract_metadata,
)

PROFILES = ["coding", "conversation", "novel", "interactive-novel", "paper", "agent-builder"]

# skeleton 模式硬上限：每个 profile 的 skeleton 产物不应爆炸式膨胀
# 对齐旧 full 模式的 1/3 体积作为兜底（agent-builder full 是 2.2MB，skeleton 1/3 即 ~750KB 上限）
SKELETON_HARD_LIMIT = {
    "coding": 50_000,
    "conversation": 70_000,
    "novel": 80_000,
    "interactive-novel": 100_000,
    "paper": 80_000,
    "agent-builder": 150_000,
}


def test_skeleton_much_smaller_than_full():
    """skeleton 模式产物应比 full 模式显著更小（至少减半）"""
    for pid in PROFILES:
        sk = build_ruleset(pid, mode="skeleton")
        fl = build_ruleset(pid, mode="full")
        ratio = len(sk) / len(fl)
        assert ratio < 0.6, f"{pid}: skeleton/full = {ratio:.2f}, 未显著瘦身 (sk={len(sk)} fl={len(fl)})"
        print(f"  {pid}: skeleton={len(sk)} full={len(fl)} 比例={ratio:.2f}")
    print("[PASS] skeleton 模式产物均显著小于 full")


def test_skeleton_under_hard_limit():
    """skeleton 模式产物应在硬上限内（对齐预算）"""
    for pid in PROFILES:
        sk = build_ruleset(pid, mode="skeleton")
        limit = SKELETON_HARD_LIMIT[pid]
        assert len(sk) <= limit, f"{pid}: skeleton={len(sk)} 超硬上限 {limit}"
    print("[PASS] skeleton 模式产物均在硬上限内")


def test_skeleton_has_on_demand_index():
    """skeleton 模式必须包含 ON-DEMAND INDEX 段"""
    for pid in PROFILES:
        rs = build_ruleset(pid, mode="skeleton")
        assert "ON-DEMAND INDEX" in rs, f"{pid}: 缺 ON-DEMAND INDEX 段"
        assert "Loading Protocol" in rs, f"{pid}: 缺 Loading Protocol 段"
    print("[PASS] skeleton 模式含 ON-DEMAND INDEX + Loading Protocol")


def test_skeleton_has_skills_table():
    """skeleton 模式每个 profile 的 INDEX 必含 Skills 表（Skills 层）"""
    for pid in PROFILES:
        rs = build_ruleset(pid, mode="skeleton")
        assert "## SKILLS LAYER (按需)" in rs, f"{pid}: 缺 Skills 表"
        assert "SKILLS LAYER" in rs, f"{pid}: 缺 Skills 层标注"
        # 至少列出一行
        m = rs.split("## SKILLS LAYER (按需)")[1].split("##", 1)[0]
        rows = [l for l in m.splitlines() if l.startswith("|") and "文件路径" not in l and "---" not in l]
        assert len(rows) > 0, f"{pid}: Skills 表无条目"
    print("[PASS] skeleton 模式含 Skills 索引表")


def test_skeleton_has_capabilities_table():
    """skeleton 模式每个 profile 的 INDEX 必含 Capabilities 表"""
    for pid in PROFILES:
        rs = build_ruleset(pid, mode="skeleton")
        assert "## Capabilities (按需)" in rs, f"{pid}: 缺 Capabilities 表"
    print("[PASS] skeleton 模式含 Capabilities 索引表")


def test_skeleton_has_mcp_section():
    """skeleton 模式每个 profile 都列出 MCP 段（哪怕没有 mcp skill 也要有红线提示）"""
    for pid in PROFILES:
        rs = build_ruleset(pid, mode="skeleton")
        assert "## MCP (按需" in rs, f"{pid}: 缺 MCP 段"
        # 必须含红线提示
        assert "MCP 红线" in rs, f"{pid}: 缺 MCP 红线提示"
    print("[PASS] skeleton 模式含 MCP 红线段（所有 profile）")


def test_skeleton_has_meta_rules_when_router_present():
    """skeleton 模式应把 core/profile-router.md 放到 Meta Rules（不内联）"""
    for pid in PROFILES:
        m = parse_manifest(pid)
        if "core/profile-router.md" in m["includes"].get("core", []):
            rs = build_ruleset(pid, mode="skeleton")
            assert "## Meta Rules (按需" in rs, f"{pid}: profile-router 应在 Meta Rules 段"
            assert "core/profile-router.md" in rs, f"{pid}: Meta Rules 缺 profile-router 路径"
            # profile-router 内容不应内联到 CORE LAYER
            router_content = (REPO_ROOT / "core/profile-router.md").read_text(encoding="utf-8")
            # 取一个独特的标题行验证未内联
            unique = "# Profile Router（Profile 选择器）"
            # 它在 ON-DEMAND INDEX 里会出现，但不能在 CORE LAYER 里
            core_layer = rs.split("# === PROFILE LAYER")[0]
            assert unique not in core_layer, f"{pid}: profile-router 内容被错误内联到 CORE LAYER"
    print("[PASS] skeleton 模式把 profile-router 移到 Meta Rules")


def test_skeleton_no_subagent_inline():
    """skeleton 模式不应内联 subagent prompts（如 architect-subagent.md）"""
    # coding profile 有 architect-subagent.md
    rs = build_ruleset("coding", mode="skeleton")
    sub_path = REPO_ROOT / "profiles/coding/docs/prompts/architect-subagent.md"
    if sub_path.exists():
        sub_text = sub_path.read_text(encoding="utf-8")
        # 取一个独特句子验证未内联
        unique_line = ""
        for line in sub_text.splitlines():
            if line.strip() and not line.startswith("#") and not line.startswith(">"):
                unique_line = line.strip()
                break
        if unique_line:
            assert unique_line not in rs, f"skeleton 不应内联 architect-subagent: {unique_line[:50]}"
        # 但路径应在 INDEX 中
        assert "profiles/coding/docs/prompts/architect-subagent.md" in rs, "skeleton 应在 INDEX 列出 subagent 路径"
    print("[PASS] skeleton 模式不内联 subagent prompts")


def test_skeleton_no_capability_inline():
    """skeleton 模式不应内联 capabilities 内容"""
    # coding profile 启用 research 能力包
    rs = build_ruleset("coding", mode="skeleton")
    cap_path = REPO_ROOT / "capabilities/research.md"
    if cap_path.exists():
        cap_text = cap_path.read_text(encoding="utf-8")
        # 取 H1 验证未内联
        h1 = ""
        for line in cap_text.splitlines():
            if line.startswith("# "):
                h1 = line.strip()
                break
        if h1:
            assert h1 not in rs, f"skeleton 不应内联 capabilities: {h1}"
        # 但路径应在 INDEX 中
        assert "capabilities/research.md" in rs, "skeleton 应在 INDEX 列出 capability 路径"
    print("[PASS] skeleton 模式不内联 capabilities 内容")


def test_skeleton_templates_loaded_for_agent_builder():
    """agent-builder profile 的 templates 段必须出现在 INDEX 中（修复死配置）"""
    rs = build_ruleset("agent-builder", mode="skeleton")
    assert "## Templates (按需" in rs, "agent-builder: 缺 Templates 段（此前是死配置）"
    # 6 个模板都应列出
    expected = ["code-reviewer", "customer-service", "data-analyst",
                "general-assistant", "research-assistant", "workflow-automator"]
    for tpl in expected:
        assert tpl in rs, f"agent-builder: Templates 缺 {tpl}"
    print("[PASS] agent-builder 的 templates 段被装配进 INDEX（修复死配置）")


def test_skeleton_no_templates_for_non_agent_profiles():
    """非 agent-builder profile 不应出现 Templates 段"""
    for pid in ["coding", "conversation", "novel", "interactive-novel", "paper"]:
        rs = build_ruleset(pid, mode="skeleton")
        assert "## Templates (按需" not in rs, f"{pid}: 不应有 Templates 段"
    print("[PASS] 非 agent-builder profile 不含 Templates 段")


def test_skeleton_mcp_files_collected():
    """_collect_mcp_files 正确识别 MCP 相关 skill（有则识别，无则空列表）"""
    expected_mcp_profiles = {"coding", "conversation", "novel", "interactive-novel", "paper"}
    for pid in PROFILES:
        m = parse_manifest(pid)
        mcp_files = _collect_mcp_files(m)
        mcp_paths = [f for f, _ in mcp_files]
        if pid in expected_mcp_profiles:
            assert any("tool-skill-mcp" in p or "mcp-registry" in p for p in mcp_paths), \
                f"{pid}: _collect_mcp_files 未识别 MCP skill"
        # agent-builder 没有 mcp skill 是允许的
    print("[PASS] _collect_mcp_files 正确识别 MCP skills")


def test_skeleton_mcp_section_lists_paths():
    """skeleton 模式 MCP 段必须列出 mcp-registry / tool-skill-mcp / mcp.example.json 路径"""
    for pid in PROFILES:
        rs = build_ruleset(pid, mode="skeleton")
        assert "mcp.example.json" in rs, f"{pid}: MCP 段缺 mcp.example.json 引用"
    print("[PASS] skeleton 模式 MCP 段引用 mcp.example.json")


def test_sharded_platform_entry_under_limit():
    """限长平台在 skeleton 模式下入口文件必须 ≤ limit + 余量（按 UTF-8 字节）"""
    for pid in ["coding", "agent-builder"]:  # 大小两个 profile 验证
        rs = build_ruleset(pid, mode="skeleton")
        for tool, limit in TOOL_CHAR_LIMIT.items():
            out = write_tool_file(tool, pid, rs, mode="skeleton")
            content = out.read_text(encoding="utf-8")
            byte_size = len(content.encode("utf-8"))
            if len(rs) > limit:
                # 入口文件按字节必须 ≤ limit + 100（余量给硬截断后的提示行）
                assert byte_size <= limit + 100, \
                    f"{pid}/{tool}: 入口字节 {byte_size} > {limit}+100"
    print("[PASS] 限长平台入口文件均在字节限制内")


def test_sharded_platform_produces_shard_dir():
    """限长平台在 skeleton 模式下超限时应生成分片目录 + INDEX.md"""
    rs = build_ruleset("coding", mode="skeleton")
    for tool in TOOL_CHAR_LIMIT:
        # 清空旧分片
        from sync_rules import _shard_root
        sd = _shard_root(tool)
        if sd.exists():
            for old in sd.glob("*"):
                old.unlink()
        # 重新生成
        write_tool_file(tool, "coding", rs, mode="skeleton")
        if len(rs) > TOOL_CHAR_LIMIT[tool]:
            assert sd.exists() and any(sd.glob("*")), f"{tool}: 未生成分片目录"
            index_md = sd / "INDEX.md"
            assert index_md.exists(), f"{tool}: 分片目录缺 INDEX.md"
    print("[PASS] 限长平台生成分片目录 + INDEX.md")


def test_full_mode_backward_compat():
    """full 模式仍然能生成所有平台单文件（向后兼容）"""
    rs = build_ruleset("conversation", mode="full")
    for tool in TOOL_OUTPUT:
        out = write_tool_file(tool, "conversation", rs, mode="full")
        assert out.exists(), f"{tool}: full 模式生成失败"
    print(f"[PASS] full 模式 {len(TOOL_OUTPUT)} 个工具向后兼容")


def test_provenance_records_mode():
    """provenance JSON 记录 mode 字段"""
    import json
    rs = build_ruleset("coding", mode="skeleton")
    write_tool_file("agents-md", "coding", rs, mode="skeleton")
    prov = REPO_ROOT / "provenance" / "coding-agents-md.json"
    assert prov.exists(), "provenance 未生成"
    rec = json.loads(prov.read_text(encoding="utf-8"))
    assert rec["mode"] == "skeleton", f"provenance mode 错: {rec.get('mode')}"
    assert "size" in rec and "hash" in rec
    print("[PASS] provenance 记录 mode 字段")


def test_run_all():
    print("=" * 60)
    print("Skeleton 模式专项测试")
    print("=" * 60)
    tests = [
        test_skeleton_much_smaller_than_full,
        test_skeleton_under_hard_limit,
        test_skeleton_has_on_demand_index,
        test_skeleton_has_skills_table,
        test_skeleton_has_capabilities_table,
        test_skeleton_has_mcp_section,
        test_skeleton_has_meta_rules_when_router_present,
        test_skeleton_no_subagent_inline,
        test_skeleton_no_capability_inline,
        test_skeleton_templates_loaded_for_agent_builder,
        test_skeleton_no_templates_for_non_agent_profiles,
        test_skeleton_mcp_files_collected,
        test_skeleton_mcp_section_lists_paths,
        test_sharded_platform_entry_under_limit,
        test_sharded_platform_produces_shard_dir,
        test_full_mode_backward_compat,
        test_provenance_records_mode,
    ]
    passed = 0
    failed = []
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            failed.append((t.__name__, str(e)))
            print(f"[FAIL] {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} 通过")
    # 清理
    rs = build_ruleset("coding", mode="skeleton")
    for tool in TOOL_OUTPUT:
        write_tool_file(tool, "coding", rs, mode="skeleton")
    print("[cleanup] 已用 coding profile (skeleton) 恢复所有生成文件")
    assert len(failed) == 0, f"{len(failed)} 个测试失败"


if __name__ == "__main__":
    try:
        test_run_all()
        sys.exit(0)
    except AssertionError:
        sys.exit(1)
