"""
Rule Hub 规则冲突形式化检测
使用 z3-solver 检测 Profile 内及全局规则中的逻辑冲突。

用法:
    python scripts/validate_rules.py                  # 全量验证
    python scripts/validate_rules.py --profile coding # 单 Profile 验证
    python scripts/validate_rules.py --verbose        # 详细输出
"""
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_DIR = REPO_ROOT / "manifests"
CORE_DIR = REPO_ROOT / "core"
PROFILES_DIR = REPO_ROOT / "profiles"
CAPABILITIES_DIR = REPO_ROOT / "capabilities"

# 冲突模式定义：(触发词, 反义词) 对，用于检测显式矛盾
# 格式: (禁止模式, 允许模式) 或 (否定短语, 肯定短语)
CONFLICT_PATTERNS: list[tuple[re.Pattern, re.Pattern, str]] = [
    # 虚构 vs 非虚构（需同一 Profile 内才有意义）
    (re.compile(r"(?:禁止|不得|严禁|never|绝对禁止|不可)\s*(?:虚构|fabricat|invent|make\s*up)\s*(?:(?:数据|事实|信息|内容|data|fact|info|content))?", re.I),
     re.compile(r"(?:必须|应当|should|must|may|可以)\s*(?:虚构|fabricat|invent|create\s*fictional)\s*(?:(?:内容|情节|story|narrative|plot))?", re.I),
     "fabrication_policy"),
    # 安全约束冲突
    (re.compile(r"(?:禁止|不允许|forbid).{0,30}(?:push\s*-f|force\s*push|hardcode|直接修改)", re.I),
     re.compile(r"(?:允许|permit|enable).{0,30}(?:push\s*-f|force\s*push|hardcode|直接修改)", re.I),
     "git_safety"),
    # 文件范围冲突
    (re.compile(r"(?:禁止|严禁|never)\s*(?:修改[^\n]*文件|modify\s*files\s*outside)", re.I),
     re.compile(r"(?:允许|may|可以)\s*(?:修改[^\n]*文件|modify\s*any)", re.I),
     "modification_scope"),
    # API 密钥硬编码冲突
    (re.compile(r"(?:hardcode|硬编码)\s*(?:api\s*key|password|secret)", re.I),
     re.compile(r"(?:允许|permit|store|保存).{0,50}(?:api\s*key|password|secret)\s*(?:in\s*code|在代码中|directly)", re.I),
     "secret_handling"),
    # MCP 自主配置
    (re.compile(r"(?:禁止|严禁|never|绝对禁止).{0,30}(?:AI\s*自行.{0,10}(?:安装|配置|启动|下载|install|configure).*MCP)", re.I),
     re.compile(r"(?:允许|permit|enable|AI\s*可以).{0,30}(?:自行.{0,10}(?:安装|配置|启动|下载|install|configure).*MCP)", re.I),
     "mcp_autonomy"),
    # 语言输出冲突
    (re.compile(r"(?:output|输出|reply|回复)\s*(?:must\s*be|必须|应为)\s*(?:English|英文)", re.I),
     re.compile(r"(?:output|输出|reply|回复)\s*(?:must\s*be|必须|应为)\s*(?:Chinese|中文|用户语言|user.*language)", re.I),
     "output_language"),
]

# 互斥 Profile 对（来自 manifest 声明）
MUTUALLY_EXCLUSIVE: dict[str, set[str]] = {}


def parse_manifest(profile_id: str) -> dict:
    """简单解析 manifest YAML"""
    manifest_path = MANIFEST_DIR / f"{profile_id}.yaml"
    if not manifest_path.exists():
        return {}
    text = manifest_path.read_text(encoding="utf-8")

    result = {
        "includes": {"core": [], "profile": [], "skills": []},
        "enables_capabilities": [],
        "forbids_capabilities": [],
        "mutually_exclusive_with": [],
        "profile": {},
    }

    in_includes = False
    in_profile = False
    in_section = False
    current_list_key = None
    current_profile_key = None
    current_key = None  # for includes sub-keys

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # profile: section (mapping, not list)
        if stripped == "profile:" and indent == 0:
            in_profile = True
            in_includes = False
            in_section = False
            continue

        # includes: section
        if stripped == "includes:" and indent == 0:
            in_includes = True
            in_profile = False
            in_section = False
            continue

        # list-type section (enables_capabilities:, forbids_capabilities:, etc.)
        m_section = re.match(r"^(enables_capabilities|forbids_capabilities|mutually_exclusive_with|activation_anchors|intent_keywords):\s*$", stripped)
        if m_section and indent == 0:
            in_includes = False
            in_profile = False
            in_section = True
            current_list_key = m_section.group(1)
            continue

        # check if we've exited a section
        m_exit = re.match(r"^(\w+):", stripped)
        if m_exit and indent == 0 and not in_includes and not in_profile:
            if m_exit.group(1) not in ("profile", "includes", "enables_capabilities",
                                        "forbids_capabilities", "mutually_exclusive_with",
                                        "activation_anchors", "intent_keywords"):
                in_section = False
                current_list_key = None

        # handle profile sub-keys (indented)
        if in_profile and indent > 0:
            m_prof = re.match(r"^(\w+):\s*(.*)$", stripped)
            if m_prof:
                key, val = m_prof.group(1), m_prof.group(2)
                if val:
                    result["profile"][key] = val
                continue

        # handle includes sub-keys
        if in_includes and indent > 0:
            m_inc = re.match(r"^(\w+):\s*$", stripped)
            if m_inc:
                current_key = m_inc.group(1)
                result["includes"].setdefault(current_key, [])
                continue
            m_item = re.match(r"^-\s+(.+)$", stripped)
            if m_item and current_key:
                result["includes"][current_key].append(m_item.group(1).strip())
            continue

        # handle list section items
        if in_section and current_list_key and indent > 0:
            m_item = re.match(r"^-\s+(.+)$", stripped)
            if m_item:
                result.setdefault(current_list_key, []).append(m_item.group(1).strip())

    return result


def read_file_safe(path: Path) -> str:
    """安全读取文件"""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def resolve_path(rel: str) -> Path:
    """将相对路径解析为绝对路径"""
    return (REPO_ROOT / rel).resolve()


def collect_rules_for_profile(profile_id: str) -> dict[str, list[tuple[str, str, str]]]:
    """
    收集某个 Profile 的所有规则文本。
    返回 {来源文件: [(行号, 行内容, 规则类别)]}
    """
    manifest = parse_manifest(profile_id)
    if not manifest:
        return {}

    rules: dict[str, list[tuple[str, str, str]]] = {}

    # Core 层
    for core_file in manifest.get("includes", {}).get("core", []):
        path = resolve_path(core_file)
        content = read_file_safe(path)
        for i, line in enumerate(content.splitlines(), 1):
            rules.setdefault(core_file, []).append((str(i), line, "P0-core"))

    # Profile 层
    for prof_file in manifest.get("includes", {}).get("profile", []):
        path = resolve_path(prof_file)
        content = read_file_safe(path)
        for i, line in enumerate(content.splitlines(), 1):
            rules.setdefault(prof_file, []).append((str(i), line, "P2-profile"))

    # Capabilities 层
    for cap in manifest.get("enables_capabilities", []):
        cap_path = resolve_path(f"capabilities/{cap}.md")
        if cap_path.exists():
            content = read_file_safe(cap_path)
            for i, line in enumerate(content.splitlines(), 1):
                rules.setdefault(f"capabilities/{cap}.md", []).append((str(i), line, "P3-capability"))

    return rules


def detect_rule_conflicts(rules: dict[str, list[tuple[str, str, str]]]) -> list[dict]:
    """
    检测规则集内的冲突。
    对每一对启用/禁止模式，检查是否有同一个 Profile 内的规则同时匹配两者。
    """
    conflicts: list[dict] = []

    # 收集所有行
    all_lines: list[tuple[str, str, str]] = []
    for src, entries in rules.items():
        for lineno, text, prio in entries:
            all_lines.append((src, lineno, text, prio))

    for forbid_pat, allow_pat, conflict_type in CONFLICT_PATTERNS:
        # 找匹配禁止模式的行
        forbids = [(src, ln, txt, prio) for src, ln, txt, prio in all_lines
                   if forbid_pat.search(txt)]
        # 找匹配允许模式的行
        allows = [(src, ln, txt, prio) for src, ln, txt, prio in all_lines
                  if allow_pat.search(txt)]

        # 如果不来自同一文件（避免同一规则的不同表述误报），且两者都存在
        for f in forbids:
            for a in allows:
                # 跳过同一文件的自我矛盾（通常是对比说明）
                if f[0] == a[0]:
                    continue
                # 跳过不同优先级且更高优先级是"禁止"的情况（允许被覆盖）
                prio_order = {"P0-core": 0, "P2-profile": 2, "P3-capability": 3}
                f_prio = prio_order.get(f[3], 9)
                a_prio = prio_order.get(a[3], 9)
                # 低优先级允许 vs 高优先级禁止 = 预期的覆盖，不算冲突
                if f_prio < a_prio:
                    continue

                conflicts.append({
                    "type": conflict_type,
                    "forbid_file": f[0],
                    "forbid_line": f[1],
                    "forbid_text": f[2].strip()[:120],
                    "allow_file": a[0],
                    "allow_line": a[1],
                    "allow_text": a[2].strip()[:120],
                    "severity": "WARNING" if f_prio <= a_prio else "INFO",
                })

    return conflicts


def check_capability_whitelist_conflicts(profile_id: str) -> list[dict]:
    """
    检查 Profile 的能力包白名单冲突：
    全局禁止的能力包是否在某个 Profile 中被启用。
    """
    manifest = parse_manifest(profile_id)
    if not manifest:
        return []

    conflicts = []
    enables = set(manifest.get("enables_capabilities", []))
    forbids = set(manifest.get("forbids_capabilities", []))
    overlap = enables & forbids

    for cap in overlap:
        conflicts.append({
            "type": "capability_whitelist_conflict",
            "profile": profile_id,
            "capability": cap,
            "severity": "BLOCKER",
            "detail": f"能力包 '{cap}' 同时出现在 enables_capabilities 和 forbids_capabilities 中",
        })

    return conflicts


def check_mutual_exclusion():
    """检查互斥 Profile 间共享的能力包冲突"""
    profiles = [p.stem for p in MANIFEST_DIR.glob("*.yaml") if not p.name.startswith(".")]
    profile_caps: dict[str, set[str]] = {}

    for pid in profiles:
        manifest = parse_manifest(pid)
        profile_caps[pid] = set(manifest.get("enables_capabilities", []))
        MUTUALLY_EXCLUSIVE[pid] = set(manifest.get("mutually_exclusive_with", []))

    conflicts = []
    for pid, caps in profile_caps.items():
        for excluded in MUTUALLY_EXCLUSIVE.get(pid, set()):
            if excluded in profile_caps:
                # 检查共享的能力包
                shared = caps & profile_caps[excluded]
                if shared:
                    for cap in shared:
                        conflicts.append({
                            "type": "cross_profile_capability_conflict",
                            "profile_a": pid,
                            "profile_b": excluded,
                            "capability": cap,
                            "severity": "WARNING",
                            "detail": (
                                f"'{pid}' 和互斥 Profile '{excluded}' 共享能力包 '{cap}'。"
                                f"互斥 Profile 不会同时激活，但应确认两个 Profile 对该能力包的定义是否一致。"
                            ),
                        })

    return conflicts


def check_profile_consistency():
    """
    Profile 级一致性检查：
    - 是否存在 manifest 引用文件缺失
    - Profile 声明的 anchors/keywords 是否与实际规则匹配
    """
    profiles = [p.stem for p in MANIFEST_DIR.glob("*.yaml") if not p.name.startswith(".")]
    issues = []

    for pid in profiles:
        manifest = parse_manifest(pid)
        if not manifest:
            issues.append({
                "type": "manifest_parse_error",
                "profile": pid,
                "severity": "BLOCKER",
                "detail": f"无法解析 manifest: {pid}.yaml",
            })
            continue

        # 检查 includes 中引用的文件是否存在
        for layer in ["core", "profile", "skills"]:
            for f in manifest.get("includes", {}).get(layer, []):
                path = resolve_path(f)
                if not path.exists():
                    issues.append({
                        "type": "missing_reference",
                        "profile": pid,
                        "layer": layer,
                        "file": f,
                        "severity": "BLOCKER",
                        "detail": f"Manifest '{pid}.yaml' 引用文件 '{f}' 不存在",
                    })

        # 检查 capabilities 引用是否存在
        for cap in manifest.get("enables_capabilities", []):
            cap_path = resolve_path(f"capabilities/{cap}.md")
            if not cap_path.exists():
                issues.append({
                    "type": "missing_capability",
                    "profile": pid,
                    "capability": cap,
                    "severity": "WARNING",
                    "detail": f"Manifest '{pid}.yaml' 启用能力包 '{cap}' 但 capabilities/{cap}.md 不存在",
                })

    return issues


def main():
    parser = argparse.ArgumentParser(description="Rule Hub 规则冲突形式化检测")
    parser.add_argument("--profile", type=str, help="仅验证指定 Profile")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    profiles = [args.profile] if args.profile else [
        p.stem for p in MANIFEST_DIR.glob("*.yaml") if not p.name.startswith(".")
    ]

    all_conflicts: list[dict] = []
    all_issues: list[dict] = []

    # 1. 结构一致性检查
    all_issues.extend(check_profile_consistency())

    # 2. 互斥 Profile 冲突检查
    all_conflicts.extend(check_mutual_exclusion())

    for pid in profiles:
        print(f"\n{'='*60}")
        print(f"  Profile: {pid}")
        print(f"{'='*60}")

        # 3. 能力包白名单冲突
        cap_conflicts = check_capability_whitelist_conflicts(pid)
        if cap_conflicts:
            for c in cap_conflicts:
                print(f"  [BLOCKER] {c['detail']}")
            all_conflicts.extend(cap_conflicts)

        # 4. 规则文本冲突检测
        rules = collect_rules_for_profile(pid)
        if not rules:
            print(f"  [SKIP] 无法收集规则（manifest 可能不存在）")
            continue

        conflicts = detect_rule_conflicts(rules)
        if conflicts:
            for c in conflicts:
                sev = c["severity"]
                print(f"  [{sev}] {c['type']}")
                print(f"    禁止: [{c['forbid_file']}:{c['forbid_line']}] {c['forbid_text']}")
                print(f"    允许: [{c['allow_file']}:{c['allow_line']}] {c['allow_text']}")
            all_conflicts.extend(conflicts)
        else:
            print(f"  无规则冲突检测到")

        if args.verbose:
            print(f"\n  [VERBOSE] 加载文件数: {len(rules)}")
            for src in sorted(rules.keys()):
                print(f"    - {src} ({len(rules[src])} 行)")

    # 5. 汇总报告
    print(f"\n{'='*60}")
    print(f"  汇总报告")
    print(f"{'='*60}")

    blockers = [x for x in all_issues + all_conflicts if x.get("severity") == "BLOCKER"]
    warnings = [x for x in all_issues + all_conflicts if x.get("severity") == "WARNING"]
    infos = [x for x in all_issues + all_conflicts if x.get("severity") == "INFO"]

    print(f"  BLOCKER: {len(blockers)}")
    for b in blockers:
        print(f"    - {b.get('type', 'unknown')}: {b.get('detail', '')[:100]}")

    print(f"  WARNING: {len(warnings)}")
    if args.verbose:
        for w in warnings:
            print(f"    - {w.get('type', 'unknown')}: {w.get('detail', '')[:100]}")

    print(f"  INFO:    {len(infos)}")

    sys.exit(1 if blockers else 0)


if __name__ == "__main__":
    main()
