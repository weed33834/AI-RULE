"""
统一规则中枢同步脚本
从 AGENTS.md + selected profile + manifests 生成各 AI 工具的规则入口文件。
用法:
    python scripts/sync_rules.py --list
    python scripts/sync_rules.py --profile coding --tool claude-code
    python scripts/sync_rules.py --profile novel --tool all
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_DIR = REPO_ROOT / "manifests"
CORE_DIR = REPO_ROOT / "core"
ADAPTERS_DIR = REPO_ROOT / "adapters"

# 工具到生成路径的映射
TOOL_OUTPUT = {
    "claude-code": "CLAUDE.md",
    "gemini": "GEMINI.md",
    "cursor": ".cursor/rules/project.mdc",
    "copilot": ".github/copilot-instructions.md",
    "trae": ".trae/rules/project_rules.md",
}


def parse_manifest(profile_id: str) -> dict:
    """简单解析 manifest YAML，只处理本仓库使用的固定结构"""
    manifest_path = MANIFEST_DIR / f"{profile_id}.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest 不存在: {manifest_path}")
    text = manifest_path.read_text(encoding="utf-8")

    result = {"includes": [], "profile": {}, "enables_capabilities": []}
    current_section = None
    current_list = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        # key: value
        m = re.match(r"^(\w+):\s*(.*)$", stripped)
        if m and not line.startswith(" "):
            key, val = m.group(1), m.group(2)
            if val:
                result.setdefault("profile", {})[key] = val
            else:
                current_section = key
                current_list = []
                result["includes"] = result.get("includes", [])
        elif stripped.startswith("- ") and current_section is not None:
            item = stripped[2:].strip()
            current_list.append(item)
    # 重新解析 includes 块（core/profile/skills）
    result["includes"] = parse_includes(text)
    result["enables_capabilities"] = parse_list_field(text, "enables_capabilities")
    result["forbids_capabilities"] = parse_list_field(text, "forbids_capabilities")
    result["mutually_exclusive_with"] = parse_list_field(text, "mutually_exclusive_with")
    return result


def parse_includes(text: str) -> dict:
    """解析 includes 下的 core/profile/skills 列表"""
    includes = {"core": [], "profile": [], "skills": []}
    current = None
    in_includes = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "includes:":
            in_includes = True
            continue
        if not in_includes:
            continue
        # 顶格 key 表示已离开 includes 块
        if not line.startswith(" "):
            in_includes = False
            continue
        # 缩进 section key（如 core: profile: skills:）
        if re.match(r"^\w+:", stripped) and not stripped.startswith("-"):
            current = stripped[:-1]
            if current not in includes:
                includes[current] = []
        elif stripped.startswith("- ") and current:
            includes[current].append(stripped[2:].strip())
    return includes


def parse_list_field(text: str, field: str) -> list:
    """解析 enables_capabilities 等列表字段"""
    items = []
    in_field = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{field}:"):
            in_field = True
            continue
        if in_field:
            if stripped.startswith("- "):
                items.append(stripped[2:].strip())
            elif re.match(r"^\w+:", stripped) and not stripped.startswith("-"):
                in_field = False
    return items


def read_file(path: Path) -> str:
    p = REPO_ROOT / path if not path.is_absolute() else path
    if not p.exists():
        return f"> [missing] {path}\n"
    return p.read_text(encoding="utf-8")


def expand_refs(text: str, base_dir: Path = None) -> str:
    """展开 @path 引用为内联内容，按 base_dir 解析相对路径"""
    search_base = base_dir if base_dir else REPO_ROOT

    def resolve_ref(ref: str) -> Path:
        # 1. 按 base_dir 解析（profile 相对路径）
        p = search_base / ref
        if p.exists():
            return p
        # 2. 按 REPO_ROOT 解析（core 相对路径）
        p = REPO_ROOT / ref
        if p.exists():
            return p
        # 3. 按 base_dir 的父级逐级回溯
        for parent in search_base.parents:
            p = parent / ref
            if p.exists():
                return p
        return None

    def replacer(m):
        ref = m.group(1)
        p = resolve_ref(ref)
        if p:
            inner = p.read_text(encoding="utf-8")
            # 递归展开内嵌引用，保持 base_dir
            inner = expand_refs(inner, p.parent)
            return f"\n{inner}\n"
        return f"> [unresolved ref] {ref}\n"
    return re.sub(r"@([\w/.-]+\.md)", replacer, text)


def build_ruleset(profile_id: str) -> str:
    """装配 core + profile 的完整规则集"""
    manifest = parse_manifest(profile_id)
    parts = []

    # 生成头
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_hash = hashlib.sha256(f"{profile_id}".encode()).hexdigest()[:12]
    parts.append(f"<!-- 由 sync_rules.py 自动生成 | profile: {profile_id} | generated: {ts} | profile_hash: {src_hash} | 禁止手工编辑 -->\n")

    # core 层
    parts.append("# === CORE LAYER ===\n")
    for core_file in manifest["includes"].get("core", []):
        core_path = REPO_ROOT / core_file
        parts.append(f"\n## [core] {core_file}\n")
        parts.append(expand_refs(read_file(Path(core_file)), core_path.parent))

    # profile 层
    parts.append("\n# === PROFILE LAYER ===\n")
    for prof_file in manifest["includes"].get("profile", []):
        prof_path = REPO_ROOT / prof_file
        parts.append(f"\n## [profile] {prof_file}\n")
        parts.append(expand_refs(read_file(Path(prof_file)), prof_path.parent))

    # skills 层
    parts.append("\n# === SKILLS LAYER ===\n")
    for skill_file in manifest["includes"].get("skills", []):
        skill_path = REPO_ROOT / skill_file
        parts.append(f"\n## [skill] {skill_file}\n")
        parts.append(expand_refs(read_file(Path(skill_file)), skill_path.parent))

    # capabilities 层：加载本 Profile 白名单启用的能力包（核心机制，此前未落地）
    parts.append("\n# === CAPABILITIES LAYER ===\n")
    for cap in manifest.get("enables_capabilities", []):
        cap_path = REPO_ROOT / "capabilities" / f"{cap}.md"
        if not cap_path.exists():
            parts.append(f"> [missing capability] {cap}\n")
            continue
        parts.append(f"\n## [capability] {cap}\n")
        parts.append(expand_refs(cap_path.read_text(encoding="utf-8"), cap_path.parent))

    return "\n".join(parts)


def write_tool_file(tool: str, profile_id: str, ruleset: str) -> Path:
    """按工具格式写入目标文件，可选叠加 adapters/<tool> 片段，并记录 provenance"""
    out_rel = TOOL_OUTPUT[tool]
    out_path = REPO_ROOT / out_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)

    content = ruleset
    # 可选适配器追加层：adapters/<tool>.md 或 adapters/<tool>/append.md 存在则拼接到末尾
    for cand in (ADAPTERS_DIR / f"{tool}.md", ADAPTERS_DIR / tool / "append.md"):
        if cand.exists():
            content = content + f"\n\n# === ADAPTER OVERRIDE ({tool}) ===\n" + cand.read_text(encoding="utf-8")
            break

    # Cursor .mdc 需要额外 frontmatter
    if tool == "cursor":
        header = f"---\ndescription: {profile_id} profile rules\nalwaysApply: true\n---\n\n"
        out_path.write_text(header + content, encoding="utf-8")
    else:
        out_path.write_text(content, encoding="utf-8")

    write_provenance(tool, profile_id, content)
    return out_path


def write_provenance(tool: str, profile_id: str, content: str) -> None:
    """记录本次生成产物的溯源信息到 provenance/（生成产物，已在 .gitignore 忽略）"""
    PROV_DIR = REPO_ROOT / "provenance"
    PROV_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    rec = {
        "generated_at": ts,
        "profile": profile_id,
        "tool": tool,
        "output": TOOL_OUTPUT[tool],
        "hash": hashlib.sha256(content.encode("utf-8")).hexdigest()[:16],
        "size": len(content),
    }
    (PROV_DIR / f"{profile_id}-{tool}.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def list_profiles() -> list:
    return sorted(p.stem for p in MANIFEST_DIR.glob("*.yaml"))


def main():
    parser = argparse.ArgumentParser(description="统一规则中枢同步")
    parser.add_argument("--list", action="store_true", help="列出可用 profile")
    parser.add_argument("--profile", type=str, help="选择主 profile")
    parser.add_argument("--tool", type=str, default="claude-code",
                        choices=list(TOOL_OUTPUT.keys()) + ["all"],
                        help="目标工具")
    args = parser.parse_args()

    if args.list:
        print("可用 Profile:")
        for p in list_profiles():
            print(f"  - {p}")
        return

    if not args.profile:
        print("error: 必须指定 --profile，或用 --list 查看", file=sys.stderr)
        sys.exit(1)

    if args.profile not in list_profiles():
        print(f"error: 未知 profile '{args.profile}'，可用: {list_profiles()}", file=sys.stderr)
        sys.exit(1)

    ruleset = build_ruleset(args.profile)
    tools = list(TOOL_OUTPUT.keys()) if args.tool == "all" else [args.tool]

    print(f"装配 profile={args.profile}")
    print(f"规则集大小: {len(ruleset)} 字符")
    for tool in tools:
        out_path = write_tool_file(tool, args.profile, ruleset)
        print(f"  [{tool}] -> {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
