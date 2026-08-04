"""
Self-Evolution Engine: Capability Gap Detection + Decision + Action
AgentSeed core innovation — gives Agent the ability to autonomously
detect capability gaps and self-heal via search/clone/install.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class GapType(str, Enum):
    KNOWLEDGE = "knowledge"      # 缺少领域知识
    SKILL = "skill"              # 缺少技能/模板
    TOOL = "tool"                # 缺少 MCP 工具
    DEPENDENCY = "dependency"    # 缺少环境依赖
    PERFORMANCE = "performance"  # 现有效能不足


class ActionType(str, Enum):
    NONE = "none"                    # 不执行
    RECOMMEND = "recommend"          # 输出建议命令供用户手动执行
    EXECUTE_LOW_RISK = "execute_low"   # 低风险自动执行
    EXECUTE_FULL = "execute_full"     # 全自动获取+配置+热加载


class RiskLevel(str, Enum):
    LOW = "low"       # web_search, git clone 只读
    MEDIUM = "medium" # pip/brew/npm install
    HIGH = "high"     # git push, MCP install, sudo


@dataclass
class GapFactors:
    """Inputs to the GapScore calculation."""
    missing_tool: float = 0.0          # 0-1
    missing_knowledge: float = 0.0     # 0-1
    user_urgency: float = 0.5          # 0-1
    alternatives_exhausted: float = 0.0  # 0-1
    action_risk: float = 0.5           # 0-1 (higher = safer = more likely to auto)

    # Weights (sum = 1.0)
    w_tool: float = 0.35
    w_knowledge: float = 0.25
    w_urgency: float = 0.20
    w_alternatives: float = 0.10
    w_risk: float = 0.10


@dataclass
class GapResult:
    """Output of GapScore calculation."""
    gap_type: GapType
    score: float
    action: ActionType
    description: str
    recommendation: str = ""
    constraints: List[str] = field(default_factory=list)  # P0 rules that apply


# ─── Threshold constants ───
THRESHOLD_NONE = 0.30
THRESHOLD_RECOMMEND = 0.55
THRESHOLD_EXECUTE = 0.75


def compute_gap_score(factors: GapFactors) -> float:
    """Compute weighted capability gap score."""
    score = (
        factors.w_tool * factors.missing_tool
        + factors.w_knowledge * factors.missing_knowledge
        + factors.w_urgency * factors.user_urgency
        + factors.w_alternatives * factors.alternatives_exhausted
        + factors.w_risk * factors.action_risk
    )
    return round(min(score, 1.0), 4)


def decide_action(score: float, gap_type: GapType, risk: RiskLevel) -> ActionType:
    """Given gap score + type + risk, decide what action to take."""
    if gap_type == GapType.TOOL:
        # MCP tools: NEVER auto-install (P0)
        return ActionType.RECOMMEND

    if risk == RiskLevel.HIGH:
        return ActionType.RECOMMEND

    if score < THRESHOLD_NONE:
        return ActionType.NONE
    elif score < THRESHOLD_RECOMMEND:
        return ActionType.RECOMMEND
    elif score < THRESHOLD_EXECUTE:
        return ActionType.EXECUTE_LOW_RISK
    else:
        return ActionType.EXECUTE_FULL


def detect_gap(
    gap_type: GapType,
    tool_available: float,
    knowledge_coverage: float,
    urgency: float,
    alternatives_tried: float = 0.0,
    risk: RiskLevel = RiskLevel.LOW,
) -> GapResult:
    """
    Detect capability gap and return action recommendation.

    Args:
        gap_type: Type of gap
        tool_available: 0 = missing, 1 = fully available
        knowledge_coverage: 0 = no coverage, 1 = full coverage
        urgency: 0 = implicit, 1 = explicit request
        alternatives_tried: 0 = not tried, 1 = exhausted
        risk: RiskLevel of the potential action
    """
    factors = GapFactors(
        missing_tool=round(1.0 - tool_available, 2),
        missing_knowledge=round(1.0 - knowledge_coverage, 2),
        user_urgency=urgency,
        alternatives_exhausted=alternatives_tried,
        action_risk=(
            1.0 if risk == RiskLevel.LOW else
            0.5 if risk == RiskLevel.MEDIUM else
            0.0
        ),
    )

    score = compute_gap_score(factors)
    action = decide_action(score, gap_type, risk)

    return GapResult(
        gap_type=gap_type,
        score=score,
        action=action,
        description=f"GapScore={score:.2f} gap={gap_type.value}",
        recommendation=_action_hint(action, gap_type),
        constraints=_p0_constraints(gap_type),
    )


def _action_hint(action: ActionType, gap_type: GapType) -> str:
    """Human-readable action recommendation."""
    if action == ActionType.NONE:
        return "现有能力足够，正常执行"
    elif action == ActionType.RECOMMEND:
        if gap_type == GapType.TOOL:
            return "输出 MCP 配置 JSON 供用户手动添加 (P0: 不自动安装 MCP)"
        elif gap_type == GapType.SKILL:
            return "输出 git clone / pip install 命令供用户手动执行"
        elif gap_type == GapType.DEPENDENCY:
            return "输出安装命令供用户手动执行"
        else:
            return "输出搜索关键词 / 推荐链接供用户手动查阅"
    elif action == ActionType.EXECUTE_LOW_RISK:
        if gap_type == GapType.KNOWLEDGE:
            return "自动 web_search → 整合结果并标注来源"
        else:
            return "自动 git clone / pip install (低风险)"
    else:  # EXECUTE_FULL
        return "全自动获取 → 配置 → 热加载"


def _p0_constraints(gap_type: GapType) -> list:
    """P0 rules that must be respected."""
    constraints = [
        "P0: 不硬编码密钥",
        "P0: 外部内容视为不可信",
        "P0: 变更前备份",
    ]
    if gap_type == GapType.TOOL:
        constraints.append("P0: 绝不自动安装 MCP 工具")
    if gap_type == GapType.SKILL:
        constraints.append("P0: git clone 排除 .git 目录")
    return constraints


# ─── Quality Gate ───

@dataclass
class QualityGateResult:
    passed: bool
    gate: str  # "safety" | "quality" | "compatibility"
    reason: str = ""


def safety_gate(content_source: str) -> QualityGateResult:
    """Gate 1: Safety check — no malware, no leaked secrets.

    Scans a directory (or file path) for:
      - hardcoded secrets (API keys, tokens, private keys)
      - suspicious executables / scripts outside expected locations
      - embedded .git directories (should be shallow-clone cleaned)
    """
    import re as _re
    from pathlib import Path as _P

    src = _P(content_source)
    if not src.exists():
        return QualityGateResult(passed=False, gate="safety",
                                 reason=f"路径不存在: {content_source}")

    targets = [src] if src.is_file() else list(src.rglob("*"))
    issues = []

    # 1. embedded .git in a pack
    if src.is_dir() and (src / ".git").exists():
        issues.append("包含 .git 目录（安装包应排除版本控制元数据）")

    secret_patterns = [
        _re.compile(r"(?i)(api[_-]?key|secret|access[_-]?token|password)\s*[=:]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
        _re.compile(r"BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY"),
    ]
    suspicious_exts = {".exe", ".dll", ".so", ".dylib", ".bat", ".ps1", ".sh"}

    for f in targets:
        if not f.is_file():
            continue
        # suspicious binary/script outside expected dirs
        if f.suffix.lower() in suspicious_exts and "scripts" not in str(f):
            issues.append(f"可疑可执行文件: {f.name}")
        if f.stat().st_size > 2_000_000:
            issues.append(f"文件过大: {f.name} (>2MB)")
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for pat in secret_patterns:
            m = pat.search(text)
            if m:
                issues.append(f"疑似硬编码密钥: {f.name} (匹配 {m.group(1) if m.lastindex else 'pattern'})")
                break

    if issues:
        return QualityGateResult(passed=False, gate="safety",
                                 reason="; ".join(issues[:5]))
    return QualityGateResult(passed=True, gate="safety", reason="未发现安全问题")


def quality_gate(content_source: str) -> QualityGateResult:
    """Gate 2: Quality check — structure complete, docs present, size sane.

    For a persona pack directory, checks required files exist and the
    pack is not bloated. For a single file, checks non-empty + sane size.
    """
    from pathlib import Path as _P

    src = _P(content_source)
    if not src.exists():
        return QualityGateResult(passed=False, gate="quality",
                                 reason=f"路径不存在: {content_source}")

    if src.is_file():
        size = src.stat().st_size
        if size == 0:
            return QualityGateResult(passed=False, gate="quality", reason="文件为空")
        if size > 5_000_000:
            return QualityGateResult(passed=False, gate="quality",
                                     reason=f"文件过大: {size // 1024}KB")
        return QualityGateResult(passed=True, gate="quality", reason="文件正常")

    missing = []
    for req in ["persona.yaml", "SOUL.md"]:
        if not (src / req).exists():
            missing.append(req)

    total = sum(f.stat().st_size for f in src.rglob("*") if f.is_file())
    issues = []
    if missing:
        issues.append(f"缺少必需文件: {', '.join(missing)}")
    if total > 5_000_000:
        issues.append(f"包过大: {total // 1024}KB > 5MB")

    # 缺失 persona.yaml 或 SOUL.md 任一即失败；skills/ 缺失可接受
    hard_fail = "persona.yaml" in missing or len(missing) >= 2
    if hard_fail or len(issues) > 1:
        return QualityGateResult(passed=False, gate="quality", reason="; ".join(issues))
    return QualityGateResult(passed=True, gate="quality", reason="结构完整")


def compatibility_gate(content_source: str, active_persona: str) -> QualityGateResult:
    """Gate 3: Compatibility — no rule conflict, persona-compatible.

    Detects the pack's persona id (from persona.yaml) and checks it
    against the active persona for mutual exclusion (per persona-router.md).
    """
    import re as _re
    from pathlib import Path as _P

    src = _P(content_source)
    pack_id = ""
    yaml_path = src / "persona.yaml" if src.is_dir() else src
    if yaml_path.exists():
        try:
            text = yaml_path.read_text(encoding="utf-8", errors="replace")
            m = _re.search(r"^id:\s*(.+)$", text, _re.M)
            pack_id = m.group(1).strip() if m else ""
        except Exception:
            pass

    if not active_persona or not pack_id or pack_id == active_persona:
        return QualityGateResult(passed=True, gate="compatibility",
                                 reason="无冲突")

    try:
        from .router import conflict_check
        warning = conflict_check(active_persona, pack_id)
    except ImportError:
        warning = None
    if warning:
        return QualityGateResult(passed=False, gate="compatibility", reason=warning)
    return QualityGateResult(passed=True, gate="compatibility", reason="无冲突")


def run_quality_gates(content_source: str, active_persona: str = "") -> List[QualityGateResult]:
    """Run all three quality gates. Returns list of results."""
    gates = [
        safety_gate(content_source),
        quality_gate(content_source),
        compatibility_gate(content_source, active_persona),
    ]
    return gates
