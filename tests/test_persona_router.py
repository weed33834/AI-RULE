"""
Persona Router 测试
验证 src/agentseed/router.py 的路由逻辑（对应 core/persona-router.md）：
选择优先级、锚点检测、意图关键词、互斥关系、能力包白名单、模式路由。
运行: python -m pytest tests/test_persona_router.py -v
"""
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from agentseed.router import (
    PERSONAS, route, detect_anchors, match_keywords,
    allowed_capabilities, forbidden_capabilities,
    are_mutually_exclusive, conflict_check,
    default_mode, default_rt, list_personas, capability_dir,
)

PROFILES = ["coding", "conversation", "novel", "interactive-novel", "paper", "agent-builder"]


def test_router_md_exists():
    p = REPO_ROOT / "core" / "persona-router.md"
    assert p.exists(), "persona-router.md 不存在"


def test_all_personas_registered():
    """router.PERSONAS 注册表覆盖全部 6 个画像"""
    assert set(PERSONAS.keys()) == set(PROFILES)


def test_explicit_override():
    """显式指定优先级最高"""
    r = route(explicit="novel", intent="修复bug")
    assert r.persona == "novel" and r.source == "explicit"
    assert r.resolved


def test_explicit_unknown_raises():
    import pytest
    with pytest.raises(ValueError):
        route(explicit="unknown-persona")


def test_anchor_detection():
    """目录锚点自动识别（仅无显式指定时）"""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "pyproject.toml").touch()
        r = route(cwd=d)
        assert r.persona == "coding" and r.source == "anchor"

        (d / "chapters").mkdir()
        r2 = route(cwd=d)
        assert r2.ambiguous, "多锚点应触发澄清"
        assert "coding" in r2.candidates and "novel" in r2.candidates


def test_anchor_beats_intent():
    """锚点优先于意图关键词（persona-router.md §2）"""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "references.bib").touch()
        r = route(cwd=d, intent="帮我写小说")
        assert r.persona == "paper", "paper 锚点应压过 novel 意图"


def test_intent_keywords():
    """意图关键词匹配"""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        cases = [
            ("帮我写小说续写人物", "novel"),
            ("修复这个bug然后重构", "coding"),
            ("写一篇论文摘要", "paper"),
            ("开始一局互动游戏", "interactive-novel"),
            ("查询对比分析", "conversation"),
            ("设计一个智能体", "agent-builder"),
        ]
        for intent, expected in cases:
            r = route(cwd=d, intent=intent)
            assert r.persona == expected, f"intent={intent!r} -> {r.persona}, 期望 {expected}"
            assert r.source == "keyword"


def test_fallback_conversation():
    """无信号时 fallback 到 conversation"""
    with tempfile.TemporaryDirectory() as td:
        r = route(cwd=Path(td))
        assert r.persona == "conversation" and r.source == "fallback"


def test_mutex_symmetry():
    """互斥关系对称"""
    for pid in PROFILES:
        for e in PERSONAS[pid]["mutually_exclusive_with"]:
            assert pid in PERSONAS[e]["mutually_exclusive_with"], f"{pid} <-> {e} 不对称"


def test_mutex_pairs():
    for a, b in [("novel", "interactive-novel"), ("coding", "novel"), ("agent-builder", "novel")]:
        assert are_mutually_exclusive(a, b), f"{a} 与 {b} 应互斥"


def test_conflict_messages():
    """互斥切换应给出状态清理提示"""
    assert conflict_check("novel", "paper") is not None
    assert "共享素材" in conflict_check("novel", "interactive-novel")
    assert conflict_check("coding", "paper") is None  # 不互斥 → 无警告


def test_capability_whitelist():
    """forbids 不在 enables 中；每个画像可叠加 dar"""
    for pid in PROFILES:
        enables = set(allowed_capabilities(pid))
        forbids = set(forbidden_capabilities(pid))
        assert not (enables & forbids), f"{pid} enables/forbids 重叠: {enables & forbids}"
        assert "dar" in enables, f"{pid} 应默认可叠加 dar"


def test_capability_dir_mapping():
    assert capability_dir("dar") == "research/dar"
    assert capability_dir("research") == "research"
    assert capability_dir("unknown-cap") == "unknown-cap"  # 未登记原样返回


def test_default_modes():
    """persona-router.md §8.2 默认模式表"""
    expected = {
        "coding": "project", "conversation": "task", "novel": "project",
        "interactive-novel": "task", "paper": "project", "agent-builder": "project",
    }
    for pid, mode in expected.items():
        assert default_mode(pid) == mode, f"{pid} 默认模式应为 {mode}"


def test_default_rt():
    assert default_rt("coding") == "STANDARD"
    assert default_rt("conversation") == "QUICK"
    assert default_rt("paper") == "STANDARD"


def test_list_personas():
    assert list_personas() == PROFILES
