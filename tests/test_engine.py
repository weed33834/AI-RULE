"""
AgentSeed 核心引擎测试：evolution（自进化）/ forge（装配）/ market（市场）。
"""
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from agentseed.evolution import (
    GapFactors, GapType, RiskLevel, ActionType,
    compute_gap_score, decide_action, detect_gap,
    safety_gate, quality_gate, compatibility_gate, run_quality_gates,
)
from agentseed.forge import detect_environment, forge, CapabilityCheck, switch_persona
from agentseed.market import search_personas, install_persona, _validate_structure


# ─── evolution: GapScore ───

def test_compute_gap_score_weights():
    f = GapFactors(missing_tool=1.0, missing_knowledge=1.0, user_urgency=1.0,
                   alternatives_exhausted=1.0, action_risk=1.0)
    # 0.35 + 0.25 + 0.20 + 0.10 + 0.10 = 1.0
    assert compute_gap_score(f) == 1.0


def test_compute_gap_score_zero():
    f = GapFactors(missing_tool=0.0, missing_knowledge=0.0, user_urgency=0.0,
                   alternatives_exhausted=0.0, action_risk=0.0)
    assert compute_gap_score(f) == 0.0


def test_decide_action_thresholds():
    # 0.30 以下 → NONE
    assert decide_action(0.10, GapType.KNOWLEDGE, RiskLevel.LOW) == ActionType.NONE
    # 0.30-0.55 → RECOMMEND
    assert decide_action(0.40, GapType.KNOWLEDGE, RiskLevel.LOW) == ActionType.RECOMMEND
    # 0.55-0.75 → EXECUTE_LOW_RISK
    assert decide_action(0.60, GapType.KNOWLEDGE, RiskLevel.LOW) == ActionType.EXECUTE_LOW_RISK
    # > 0.75 → EXECUTE_FULL
    assert decide_action(0.90, GapType.KNOWLEDGE, RiskLevel.LOW) == ActionType.EXECUTE_FULL


def test_decide_action_mcp_never_auto():
    """P0: MCP 工具绝不自动安装"""
    assert decide_action(0.99, GapType.TOOL, RiskLevel.LOW) == ActionType.RECOMMEND


def test_decide_action_high_risk():
    """高风险动作（sudo/push/MCP install）一律降级为推荐"""
    assert decide_action(0.99, GapType.DEPENDENCY, RiskLevel.HIGH) == ActionType.RECOMMEND


def test_detect_gap_result():
    r = detect_gap(GapType.KNOWLEDGE, tool_available=0.0, knowledge_coverage=0.0,
                   urgency=1.0, alternatives_tried=1.0, risk=RiskLevel.LOW)
    assert r.score == 1.0
    assert r.action == ActionType.EXECUTE_FULL
    assert "不硬编码密钥" in " ".join(r.constraints)
    assert r.gap_type == GapType.KNOWLEDGE


def test_detect_gap_mcp_constraints():
    r = detect_gap(GapType.TOOL, tool_available=0.0, knowledge_coverage=0.0,
                   urgency=1.0, risk=RiskLevel.LOW)
    assert any("MCP" in c for c in r.constraints)


# ─── evolution: Quality Gate ───

def test_safety_gate_flags_secrets(tmp_path):
    p = tmp_path / "pack"
    p.mkdir()
    (p / "persona.yaml").write_text("id: test\n", encoding="utf-8")
    (p / "leak.md").write_text("api_key = \"sk-abcdefghijklmnop123456\"\n", encoding="utf-8")
    g = safety_gate(str(p))
    assert not g.passed
    assert "密钥" in g.reason or "key" in g.reason.lower()


def test_safety_gate_clean(tmp_path):
    p = tmp_path / "pack"
    p.mkdir()
    (p / "persona.yaml").write_text("id: test\n", encoding="utf-8")
    (p / "SOUL.md").write_text("# hello\n", encoding="utf-8")
    g = safety_gate(str(p))
    assert g.passed


def test_safety_gate_flags_gitdir(tmp_path):
    p = tmp_path / "pack"
    (p / ".git").mkdir(parents=True)
    (p / "persona.yaml").write_text("id: test\n", encoding="utf-8")
    g = safety_gate(str(p))
    assert not g.passed
    assert ".git" in g.reason


def test_quality_gate_missing_files(tmp_path):
    p = tmp_path / "pack"
    p.mkdir()
    (p / "persona.yaml").write_text("id: test\n", encoding="utf-8")
    g = quality_gate(str(p))
    assert g.passed  # 缺 SOUL.md 可接受（仅 1 项 issue）


def test_quality_gate_empty_dir(tmp_path):
    p = tmp_path / "pack"
    p.mkdir()
    g = quality_gate(str(p))
    assert not g.passed  # 缺 persona.yaml + SOUL.md = 2 项 → 失败


def test_compatibility_gate_conflict(tmp_path):
    p = tmp_path / "pack"
    p.mkdir()
    (p / "persona.yaml").write_text("id: novel\n", encoding="utf-8")
    g = compatibility_gate(str(p), active_persona="paper")
    assert not g.passed


def test_compatibility_gate_ok(tmp_path):
    p = tmp_path / "pack"
    p.mkdir()
    (p / "persona.yaml").write_text("id: novel\n", encoding="utf-8")
    g = compatibility_gate(str(p), active_persona="coding")
    assert not g.passed  # coding 与 novel 互斥 → 正确拒绝
    # 不互斥时通过
    p2 = tmp_path / "pack2"
    p2.mkdir()
    (p2 / "persona.yaml").write_text("id: coding\n", encoding="utf-8")
    g2 = compatibility_gate(str(p2), active_persona="novel")
    assert not g2.passed
    p3 = tmp_path / "pack3"
    p3.mkdir()
    (p3 / "persona.yaml").write_text("id: paper\n", encoding="utf-8")
    g3 = compatibility_gate(str(p3), active_persona="coding")
    assert g3.passed  # paper 与 coding 不互斥 → 通过


def test_run_quality_gates(tmp_path):
    p = tmp_path / "pack"
    p.mkdir()
    (p / "persona.yaml").write_text("id: coding\n", encoding="utf-8")
    (p / "SOUL.md").write_text("# ok\n", encoding="utf-8")
    results = run_quality_gates(str(p), active_persona="novel")
    assert len(results) == 3
    # coding 与 novel 互斥 → compatibility 不通过
    assert any(not r.passed for r in results)


# ─── forge: 环境检测 ───

def test_detect_environment_anchors(tmp_path):
    (tmp_path / "pyproject.toml").touch()
    ctx = detect_environment(tmp_path)
    assert "pyproject.toml" in ctx.anchors_found
    assert ctx.suggested_persona == "coding"


def test_detect_environment_platforms(tmp_path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / "CLAUDE.md").touch()
    ctx = detect_environment(tmp_path)
    assert "claude-code" in ctx.platforms_detected
    assert any(p.name == "CLAUDE.md" for p in ctx.existing_rules)


def test_forge_dry_run(tmp_path):
    """dry-run 不写文件"""
    (tmp_path / "pyproject.toml").touch()
    result = forge(cwd=tmp_path, persona="coding", tool="claude-code", dry_run=True)
    assert result.persona_selected == "coding"
    assert result.files_generated == []
    assert "dar" in result.capabilities_loaded


def test_forge_ambiguous_raises(tmp_path):
    """多锚点不明确 → 抛 ValueError 要求显式指定"""
    import pytest
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "chapters").mkdir()
    with pytest.raises(ValueError):
        forge(cwd=tmp_path, dry_run=True)


def test_switch_persona_mutex_warning(tmp_path):
    (tmp_path / "chapters").mkdir()  # novel 锚点
    result = switch_persona("paper", cwd=tmp_path)
    assert result["ok"]
    assert result["warning"] is not None  # novel → paper 互斥警告


def test_capability_check():
    c = CapabilityCheck(persona="coding", task_domain="web", has_skills=True,
                        has_mcp=False, has_knowledge=True)
    result = c.analyze()
    assert result["persona"] == "coding"
    assert "gap_score" in result and "recommendation" in result


# ─── market: 搜索/安装 ───

def test_search_personas_local():
    r = search_personas("coding")
    assert any(x["name"] == "coding" and x["installed"] for x in r.results)


def test_search_personas_registry():
    r = search_personas("data")
    assert any(x["name"] == "data-scientist" for x in r.results)


def test_validate_structure(tmp_path):
    p = tmp_path / "pack"
    p.mkdir()
    (p / "persona.yaml").write_text("id: x\n", encoding="utf-8")
    missing = _validate_structure(p)
    assert missing == ["SOUL.md"]
    (p / "SOUL.md").write_text("# x\n", encoding="utf-8")
    assert _validate_structure(p) == []


def test_install_unknown_persona():
    result = install_persona("no-such-persona-xyz")
    assert not result.ok
    assert "未知画像" in result.error
