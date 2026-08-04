"""
Forge Engine: One-command assembly of Persona Packs into a fully-equipped Agent.

`agentseed forge` → detects environment → selects Persona Pack →
generates platform entry files → agent is ready.

This module wires together:
  - router.py         (persona selection: anchors / intent / explicit)
  - sync_rules.py     (ruleset building + platform file generation)
  - evolution.py      (capability gap analysis on the result)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set

from . import sync_rules as _sr
from .router import (
    detect_anchors, route, allowed_capabilities,
    forbidden_capabilities, default_mode, default_rt,
    are_mutually_exclusive, conflict_check,
)
from .evolution import GapType, RiskLevel, detect_gap

# Platform anchor files (mirrors sync_rules platform detection)
PLATFORM_DETECTION = {
    ".claude": "claude-code",
    ".cursor": "cursor",
    ".github/copilot-instructions.md": "copilot",
    ".trae": "trae",
    ".gemini": "gemini",
    ".windsurfrules": "windsurf",
    ".clinerules": "cline",
    ".continue": "continue",
    ".amazonq": "amazon-q",
}


@dataclass
class ForgeContext:
    """What the forge engine detected about the environment."""
    cwd: Path
    anchors_found: Set[str] = field(default_factory=set)
    suggested_persona: str = ""
    platforms_detected: Set[str] = field(default_factory=set)
    existing_rules: Set[Path] = field(default_factory=set)


@dataclass
class ForgeResult:
    """Result of a forge assembly operation."""
    persona_selected: str
    files_generated: List[Path] = field(default_factory=list)
    files_updated: List[Path] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    capabilities_loaded: List[str] = field(default_factory=list)
    gap_analysis: Optional[dict] = None
    mode: str = "skeleton"
    tool: str = ""


def detect_environment(start_dir: Optional[Path] = None) -> ForgeContext:
    """Scan cwd (or start_dir) for project anchors and existing platforms."""
    cwd = start_dir or Path.cwd()
    ctx = ForgeContext(cwd=cwd)

    # Persona anchors via router
    anchors = detect_anchors(cwd)
    ctx.anchors_found = set(anchors.keys())
    if anchors:
        ctx.suggested_persona = next(iter(set(anchors.values())))

    # Scan for existing platform configs
    for plat_path, plat_name in PLATFORM_DETECTION.items():
        if (cwd / plat_path).exists():
            ctx.platforms_detected.add(plat_name)

    # Generated entry files (CLAUDE.md / GEMINI.md / AGENTS.md / etc.)
    for name in ["CLAUDE.md", "GEMINI.md", "AGENTS.md", "best_practices.md"]:
        p = cwd / name
        if p.exists():
            ctx.platforms_detected.add("agents-md")
            ctx.existing_rules.add(p)

    return ctx


def forge(
    cwd: Optional[Path] = None,
    persona: Optional[str] = None,
    intent: str = "",
    tool: Optional[str] = None,
    mode: str = "skeleton",
    output_dir: Optional[Path] = None,
    emit_hooks: bool = True,
    dry_run: bool = False,
) -> ForgeResult:
    """Main forge entry: detect → route → build → write → analyze gaps.

    Mirrors the architecture doc §3.3 画像装配:
      agentseed forge                    → auto-detect + generate
      agentseed forge --profile coding   → explicit persona
      agentseed forge --interactive      → (CLI layer prompts, then passes persona)
      agentseed forge --dry-run          → preview without writing
    """
    cwd = cwd or Path.cwd()
    _sr.refresh_resources_root()

    # 1. Route to persona
    route_result = route(cwd=cwd, intent=intent, explicit=persona)
    if route_result.ambiguous:
        raise ValueError(
            f"画像选择不明确（候选: {route_result.candidates}）。"
            f"请用 --profile 显式指定，或使用 --interactive 交互选择。"
        )
    selected = route_result.persona

    # 2. Resolve tool
    if tool is None:
        tool = _sr.detect_tool_from_cwd()
    if tool not in _sr.TOOL_OUTPUT and tool != "all":
        tool = "agents-md"  # safe fallback

    # 3. Build ruleset
    ruleset = _sr.build_ruleset(selected, mode=mode)

    # 4. Capability summary (what this persona stacks)
    caps = allowed_capabilities(selected)
    forbids = forbidden_capabilities(selected)

    # 5. Gap analysis for the selected persona
    ctx = detect_environment(cwd)
    gap = _analyze_gaps(selected, caps, ctx)

    # 6. Write files (skip on dry-run)
    files_generated: List[Path] = []
    files_updated: List[Path] = []
    warnings: List[str] = []

    if not dry_run:
        out = output_dir or cwd
        out.mkdir(parents=True, exist_ok=True)
        _sr.set_output_root(out)
        try:
            if tool == "all":
                tools = list(_sr.TOOL_OUTPUT.keys())
            else:
                tools = [tool]
            for t in tools:
                path = _sr.write_tool_file(t, selected, ruleset, mode=mode)
                rel = path.relative_to(out) if path.is_relative_to(out) else path
                if any(p == path for p in ctx.existing_rules):
                    files_updated.append(rel)
                else:
                    files_generated.append(rel)
                # hooks (PreToolUse platforms only)
                if emit_hooks and t in _sr.HOOK_PLATFORMS:
                    try:
                        _sr.emit_constraints(t)
                    except Exception as e:
                        warnings.append(f"[{t}] hook 分发失败: {e}")
        finally:
            _sr.reset_output_root()

    return ForgeResult(
        persona_selected=selected,
        files_generated=files_generated,
        files_updated=files_updated,
        warnings=warnings,
        capabilities_loaded=caps,
        gap_analysis=gap,
        mode=mode,
        tool=tool,
    )


def _analyze_gaps(persona: str, caps: List[str], ctx: ForgeContext) -> dict:
    """Run capability gap analysis on the selected persona."""
    has_skills = (ctx.cwd / "skills").exists() or bool(caps)
    has_mcp = (ctx.cwd / ".mcp.json").exists()
    has_knowledge = len(caps) > 0

    tool_avail = 0.8 if has_mcp else (0.3 if has_skills else 0.0)
    knowledge_cov = 1.0 if has_knowledge else 0.2
    urgency = 0.5

    gap = detect_gap(
        gap_type=GapType.KNOWLEDGE,
        tool_available=tool_avail,
        knowledge_coverage=knowledge_cov,
        urgency=urgency,
        risk=RiskLevel.LOW,
    )
    return {
        "persona": persona,
        "gap_score": gap.score,
        "action": gap.action.value,
        "recommendation": gap.recommendation,
    }


def switch_persona(target: str, cwd: Optional[Path] = None) -> dict:
    """Switch active persona (persona-router.md §7).

    Validates mutual exclusion, returns warnings about state clearing.
    """
    cwd = cwd or Path.cwd()
    active = _current_persona(cwd)

    if active and active != target:
        warn = conflict_check(active, target)
        if warn:
            return {"ok": True, "from": active, "to": target, "warning": warn}
    return {"ok": True, "from": active, "to": target, "warning": None}


def _current_persona(cwd: Path) -> str:
    """Best-effort: detect current persona from cwd anchors."""
    anchors = detect_anchors(cwd)
    if anchors:
        return next(iter(set(anchors.values())))
    return ""


# ─── Capability check (used by CLI status) ───

@dataclass
class CapabilityCheck:
    """Check whether a persona can handle a given task."""
    persona: str
    task_domain: str
    has_skills: bool
    has_mcp: bool
    has_knowledge: bool

    def analyze(self) -> dict:
        tool_avail = 0.8 if self.has_mcp else (0.3 if self.has_skills else 0.0)
        knowledge_cov = 1.0 if self.has_knowledge else 0.2
        urgency = 0.8 if (not self.has_mcp and not self.has_skills and not self.has_knowledge) else 0.5

        gap = detect_gap(
            gap_type=GapType.KNOWLEDGE,
            tool_available=tool_avail,
            knowledge_coverage=knowledge_cov,
            urgency=urgency,
            risk=RiskLevel.LOW,
        )
        return {
            "persona": self.persona,
            "domain": self.task_domain,
            "gap_score": gap.score,
            "action": gap.action.value,
            "recommendation": gap.recommendation,
            "constraints": gap.constraints,
        }
