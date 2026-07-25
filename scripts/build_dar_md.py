"""B1: 聚合 dar-*.yaml → capabilities/dar.md"""
import yaml
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent  # scripts/../ = AI-RULE/
DAR_DIR = REPO / "capabilities" / "dar"

PROFILE_NAMES = {
    "coding": "软件开发",
    "conversation": "通用对话",
    "novel": "小说创作",
    "interactive-novel": "互动小说",
    "paper": "论文写作",
    "agent-builder": "智能体构建",
}

def load_dar(domain: str) -> dict:
    p = DAR_DIR / f"dar-{domain}.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def gen_source_table(registry: dict) -> str:
    if not registry:
        return ""
    rows = []
    for tier_key in sorted(registry.keys()):
        tier = registry[tier_key]
        if isinstance(tier, list):
            for s in tier:
                name = s.get("name", "")
                url = s.get("url", "-")
                stype = s.get("type", "")
                url_str = f"[{name}]({url})" if url and url != "-" else name
                rows.append(f"| {tier_key} | {url_str} | {stype} |")
    if not rows:
        return ""
    return "| Tier | 源 | 类型 |\n|---|---|---|\n" + "\n".join(rows)

def gen_routing(domain: str, rules: list) -> str:
    if not rules:
        return ""
    rows = []
    for r in rules:
        triggers = ", ".join(r.get("trigger", []))
        priority = ", ".join(r.get("priority_sources", []))
        fallback = ", ".join(r.get("fallback", []))
        action = r.get("action", "")
        rows.append(f"| [{domain}] {triggers} | {action} | {priority} | {fallback} |")
    return "\n".join(rows)

def gen_freshness(domain: str, table: list) -> str:
    if not table:
        return ""
    rows = []
    for r in table:
        rows.append(f"| [{domain}] {r.get('type','')} | {r.get('valid_period','')} | {r.get('decay_factor','')} | {r.get('notes','')} |")
    return "\n".join(rows)

def build_dar_md() -> str:
    domains = ["coding", "conversation", "novel", "interactive-novel", "paper", "agent-builder"]
    parts = []
    parts.append("# DAR — Domain-Aware Retrieval")
    parts.append("")
    parts.append("> 本文件由 `scripts/build_dar_md.py` 自动生成，聚合 6 域配置。禁止手工编辑。")
    parts.append("> 加载后，在 enable_capabilities: [dar] 的 Profile 中生效，提供域感知源路由与打分策略。")
    parts.append("")

    # ─── §1 源注册表 ───
    parts.append("## §1 源注册表")
    parts.append("")
    for d in domains:
        data = load_dar(d)
        registry = data.get("source_registry", {})
        if not registry:
            continue
        name = PROFILE_NAMES.get(d, d)
        parts.append(f"### 1.{domains.index(d)+1} {name} ({d})")
        parts.append("")
        parts.append(gen_source_table(registry))
        parts.append("")

    # ─── §2 打分协议 ───
    parts.append("## §2 打分协议")
    parts.append("")
    parts.append("| 领域 | R(相关性) | C(可信度) | F(时效) | S(共识) | 说明 |")
    parts.append("|---|---|---|---|---|---|")
    for d in domains:
        data = load_dar(d)
        sp = data.get("scoring_protocol", {})
        w = sp.get("weights", {})
        if not w:
            continue
        parts.append(f"| {PROFILE_NAMES.get(d,d)} | {w.get('relevance','')} | {w.get('credibility','')} | {w.get('freshness','')} | {w.get('consensus','')} | {sp.get('notes','')} |")
    parts.append("")

    # ─── §3 时效表 ───
    parts.append("## §3 时效表")
    parts.append("")
    parts.append("| 域/类型 | 有效周期 | 衰减因子 | 备注 |")
    parts.append("|---|---|---|---|")
    for d in domains:
        data = load_dar(d)
        ft = data.get("freshness_table", [])
        parts.append(gen_freshness(d, ft))
    parts.append("")

    # ─── §4 路由规则 ───
    parts.append("## §4 路由规则")
    parts.append("")
    parts.append("| 域/触发器 | 动作 | 优先源 | 回退源 |")
    parts.append("|---|---|---|---|")
    for d in domains:
        data = load_dar(d)
        rr = data.get("routing_rules", [])
        parts.append(gen_routing(d, rr))
    parts.append("")

    # ─── §5 领域知识 ───
    parts.append("## §5 领域知识")
    parts.append("")
    for d in domains:
        data = load_dar(d)
        dk = data.get("domain_knowledge", {})
        if not dk:
            continue
        name = PROFILE_NAMES.get(d, d)
        parts.append(f"### 5.{domains.index(d)+1} {name} ({d})")
        parts.append("")
        terms = dk.get("terminology", [])
        if terms:
            parts.append("**术语**：")
            parts.append("")
            for t in terms:
                parts.append(f"- {t}")
            parts.append("")
        pitfalls = dk.get("common_pitfalls", [])
        if pitfalls:
            parts.append("**常见陷阱**：")
            parts.append("")
            for p in pitfalls:
                parts.append(f"- {p}")
            parts.append("")

    # ─── §6 Prefix Templates ───
    parts.append("## §6 Adaptive Prefix Templates (v4)")
    parts.append("")
    for d in domains:
        data = load_dar(d)
        pt = data.get("prefix_templates", {})
        if not pt:
            continue
        name = PROFILE_NAMES.get(d, d)
        parts.append(f"### 6.{domains.index(d)+1} {name} ({d})")
        parts.append("")
        std = pt.get("standard", "")
        if std:
            parts.append(f"**Standard**：`{std.strip()}`")
            parts.append("")
        ext = pt.get("extended", "")
        if ext:
            parts.append(f"**Extended**：`{ext.strip()}`")
            parts.append("")

    return "\n".join(parts)

if __name__ == "__main__":
    md = build_dar_md()
    out = REPO / "capabilities" / "dar.md"
    out.write_text(md, encoding="utf-8")
    print(f"Generated: {out} ({len(md)} chars)")
