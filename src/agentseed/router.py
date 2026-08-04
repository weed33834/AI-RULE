"""
Persona Router: Profile selection engine for AgentSeed.

Implements the routing logic from core/persona-router.md:
  1. Explicit user/config override → absolute priority
  2. Directory anchor detection (only when not specified)
  3. Intent keyword matching
  4. Ambiguity → minimal clarification (single question)

Also exposes:
  - capability whitelist lookup (which capabilities a persona may stack)
  - mutual-exclusion checks (novel ↔ interactive-novel ↔ paper)
  - agent mode routing (default mode + reasoning depth per persona)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

# ─── Persona registry (mirrors core/persona-router.md §1) ───

PERSONAS: Dict[str, dict] = {
    "coding": {
        "name": "软件工程师",
        "mutually_exclusive_with": {"novel", "interactive-novel"},
        "anchors": ["pyproject.toml", "package.json", "go.mod", "Cargo.toml",
                    "requirements.txt"],
        "keywords": ["修复", "重构", "测试", "部署", "接口", "bug", "ci",
                     "代码", "重构", "debug", "refactor"],
        "default_mode": "project",
        "allowed_modes": ["task", "project", "autonomous"],
        "default_rt": "STANDARD",
        "capabilities": ["research", "testing", "review", "agent-governance", "dar"],
        "forbidden_capabilities": ["game-engine", "worldbuilding", "npc-simulation"],
    },
    "conversation": {
        "name": "通用助手",
        "mutually_exclusive_with": {"novel", "interactive-novel", "agent-builder"},
        "anchors": [],
        "keywords": ["查询", "对比", "分析", "调研", "总结", "介绍", "解释",
                     "search", "compare", "explain"],
        "default_mode": "task",
        "allowed_modes": ["task", "project"],
        "default_rt": "QUICK",
        "capabilities": ["research", "dar"],
        "forbidden_capabilities": ["engineering", "creative", "game-engine"],
    },
    "novel": {
        "name": "小说家",
        "mutually_exclusive_with": {"coding", "conversation", "interactive-novel",
                                    "agent-builder", "paper"},
        "anchors": [".ai-memory/creative-blueprint.md", "chapters", "outline.md"],
        "keywords": ["写一章", "续写", "人物", "伏笔", "文风", "世界观",
                     "小说", "chapter", "character"],
        "default_mode": "project",
        "allowed_modes": ["task", "project", "autonomous"],
        "default_rt": "STANDARD",
        "capabilities": ["research", "worldbuilding", "creative", "dar"],
        "forbidden_capabilities": ["game-engine", "state-machine"],
    },
    "interactive-novel": {
        "name": "互动叙事",
        "mutually_exclusive_with": {"coding", "conversation", "novel",
                                    "agent-builder", "paper"},
        "anchors": [".game-state", "game-state-machine.md", "save-slot-0.json"],
        "keywords": ["开始一局", "分支", "存档", "npc", "回合", "状态",
                     "互动", "game", "branch"],
        "default_mode": "task",
        "allowed_modes": ["task", "project"],
        "default_rt": "QUICK",
        "capabilities": ["creative", "research", "state-machine", "npc-simulation",
                         "adaptive-difficulty", "dar"],
        "forbidden_capabilities": ["novel-chapter-deliverable-mode", "engineering"],
    },
    "paper": {
        "name": "学术写手",
        "mutually_exclusive_with": {"novel", "interactive-novel"},
        "anchors": [".ai-memory/paper-blueprint.md", "manuscript", "references.bib"],
        "keywords": ["论文", "文献综述", "摘要", "引言", "方法", "结果",
                     "讨论", "引用", "投稿", "审稿", "paper", "citation"],
        "default_mode": "project",
        "allowed_modes": ["task", "project", "autonomous"],
        "default_rt": "STANDARD",
        "capabilities": ["research", "dar"],
        "forbidden_capabilities": ["game-engine", "state-machine", "npc-simulation",
                                   "novel-chapter-deliverable-mode"],
    },
    "agent-builder": {
        "name": "Agent 构建师",
        "mutually_exclusive_with": {"conversation", "novel", "interactive-novel"},
        "anchors": ["config.yaml", "tools.json", "test-cases.md"],
        "keywords": ["设计agent", "智能体配置", "工具权限", "评估",
                     "agent", "智能体", "persona"],
        "default_mode": "project",
        "allowed_modes": ["task", "project", "autonomous"],
        "default_rt": "STANDARD",
        "capabilities": ["research", "agent-governance", "engineering", "testing", "dar"],
        "forbidden_capabilities": ["novel-chapter-deliverable-mode", "game-engine"],
    },
}

# Capability package directory names (resolved under capabilities/)
CAPABILITY_DIRS = {
    "research": "research", "testing": "testing", "review": "review",
    "agent-governance": "agent-governance", "dar": "research/dar",
    "worldbuilding": "worldbuilding", "creative": "creative",
    "state-machine": "state-machine", "npc-simulation": "npc-simulation",
    "adaptive-difficulty": "adaptive-difficulty",
    "engineering": "engineering", "game-engine": "game-engine",
    "novel-chapter-deliverable-mode": "novel-chapter-deliverable-mode",
}


@dataclass
class RouteResult:
    """Result of a persona routing decision."""
    persona: str
    matched_anchors: List[str] = field(default_factory=list)
    matched_keywords: List[str] = field(default_factory=list)
    ambiguous: bool = False
    candidates: List[str] = field(default_factory=list)
    source: str = ""  # "explicit" | "anchor" | "keyword" | "fallback" | "ambiguous"

    @property
    def resolved(self) -> bool:
        return not self.ambiguous and bool(self.persona)


# ─── Anchor detection ───

def detect_anchors(cwd: Path) -> Dict[str, str]:
    """Scan directory (non-recursive) for persona anchor signals.

    Returns {anchor_name: persona_id}.
    """
    found: Dict[str, str] = {}
    for persona, info in PERSONAS.items():
        for anchor in info["anchors"]:
            p = cwd / anchor
            if p.exists():
                found[anchor] = persona
    return found


# ─── Intent keyword matching ───

def match_keywords(intent: str) -> List[str]:
    """Match user intent text against persona keyword tables.

    Returns list of persona ids, ordered by hit count.
    """
    if not intent:
        return []
    text = intent.lower()
    scores: Dict[str, int] = {}
    for persona, info in PERSONAS.items():
        hits = sum(1 for kw in info["keywords"] if kw.lower() in text)
        if hits:
            scores[persona] = hits
    # Sort by hit count desc, then registry order
    order = list(PERSONAS.keys())
    return sorted(scores, key=lambda p: (-scores[p], order.index(p)))


# ─── Main routing entry ───

def route(
    cwd: Optional[Path] = None,
    intent: str = "",
    explicit: Optional[str] = None,
) -> RouteResult:
    """Route to a persona using persona-router.md priority order.

    Priority:
      1. explicit override (user/config)
      2. directory anchors
      3. intent keywords
      4. fallback: conversation (no signal) or ambiguous (multiple signals)
    """
    cwd = cwd or Path.cwd()
    if explicit:
        if explicit not in PERSONAS:
            raise ValueError(f"未知 persona: {explicit}，可用: {list(PERSONAS)}")
        return RouteResult(persona=explicit, source="explicit")

    anchors = detect_anchors(cwd)
    anchor_personas = set(anchors.values())
    if len(anchor_personas) == 1:
        p = anchor_personas.pop()
        return RouteResult(persona=p, matched_anchors=list(anchors), source="anchor")
    if len(anchor_personas) > 1:
        return RouteResult(
            persona="", ambiguous=True,
            candidates=sorted(anchor_personas), source="ambiguous",
            matched_anchors=list(anchors),
        )

    keyword_matches = match_keywords(intent)
    if len(keyword_matches) == 1:
        p = keyword_matches[0]
        return RouteResult(persona=p, matched_keywords=keyword_matches, source="keyword")
    if len(keyword_matches) > 1:
        return RouteResult(
            persona="", ambiguous=True,
            candidates=keyword_matches, source="ambiguous",
            matched_keywords=keyword_matches,
        )

    return RouteResult(persona="conversation", source="fallback")


# ─── Capability checks ───

def allowed_capabilities(persona: str) -> List[str]:
    """Capabilities a persona may stack (whitelist)."""
    if persona not in PERSONAS:
        return []
    return list(PERSONAS[persona]["capabilities"])


def forbidden_capabilities(persona: str) -> List[str]:
    """Capabilities a persona must NOT auto-load."""
    if persona not in PERSONAS:
        return []
    return list(PERSONAS[persona]["forbidden_capabilities"])


def capability_dir(cap_id: str) -> str:
    """Resolve a capability id to its directory path (relative to capabilities/)."""
    return CAPABILITY_DIRS.get(cap_id, cap_id)


# ─── Mutual exclusion ───

def are_mutually_exclusive(p1: str, p2: str) -> bool:
    """Check if two personas are mutually exclusive (per persona-router.md §1)."""
    if p1 not in PERSONAS or p2 not in PERSONAS:
        return False
    return p2 in PERSONAS[p1]["mutually_exclusive_with"]


def conflict_check(active: str, requested: str) -> Optional[str]:
    """Check switching conflict. Returns a warning message or None.

    Per persona-router.md §7: novel ↔ interactive-novel switch must ask about
    shared material; paper ↔ novel/interactive-novel must clear all state.
    """
    if not are_mutually_exclusive(active, requested):
        return None
    pair = {active, requested}
    if pair == {"novel", "interactive-novel"}:
        return (f"切换 {active} → {requested}：是否保留共享素材（角色、世界观）？"
                f"（P0: 切换须清除前一 Profile 上下文状态标记）")
    if active in {"paper", "novel", "interactive-novel"}:
        return (f"切换 {active} → {requested} 为互斥画像，"
                f"必须清除前一 Profile 的全部创作状态。")
    return f"切换 {active} → {requested} 为互斥画像，请确认。"


# ─── Agent mode routing (§8) ───

def default_mode(persona: str) -> str:
    """Default agent mode for a persona (persona-router.md §8.2)."""
    if persona in PERSONAS:
        return PERSONAS[persona]["default_mode"]
    return "task"


def allowed_modes(persona: str) -> List[str]:
    if persona in PERSONAS:
        return list(PERSONAS[persona]["allowed_modes"])
    return ["task", "project"]


def default_rt(persona: str) -> str:
    """Default reasoning-depth marker for a persona."""
    if persona in PERSONAS:
        return PERSONAS[persona]["default_rt"]
    return "STANDARD"


# ─── Exports for CLI ───

def list_personas() -> List[str]:
    return list(PERSONAS.keys())


def persona_info(persona: str) -> dict:
    if persona not in PERSONAS:
        raise KeyError(persona)
    return dict(PERSONAS[persona])
