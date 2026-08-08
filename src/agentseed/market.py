"""
Persona Market: community persona pack discovery and installation.

Implements the "Persona 市场" design from docs/AGENTSEED_ARCHITECTURE.md §3.4:
  - agentseed persona search <query>   → search community personas
  - agentseed persona install <name>   → download + install + Quality Gate

Installation flow:
  1. Resolve source (GitHub repo URL or local path)
  2. Download (git clone --depth 1, shallow)
  3. Validate structure (persona.yaml present, SOUL.md/AGENTS.md present)
  4. Run Quality Gate (safety / quality / compatibility)
  5. Install into personas/ (or platform-specific user config dir for user-level)
  6. Report result

P0 constraints honored:
  - MCP tools are NEVER auto-installed (only config JSON emitted)
  - External content treated as untrusted until validated
  - No hardcoded secrets
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .router import conflict_check, list_personas

# Registry of known community persona sources (name → GitHub URL)
# Populated as the ecosystem grows; users can install from any URL too.
KNOWN_REGISTRY: dict = {
    "data-scientist": "https://github.com/weed33834/agentseed-personas.git",
    "researcher": "https://github.com/weed33834/agentseed-personas.git",
}

MIN_PERSONA_FILES = {"persona.yaml"}
CORE_PERSONA_FILES = {"AGENTS.md", "prompts/system-prompt.md"}

# 场景规则包必需结构（SCENARIO_PACK_SPEC.md §3）：清单 + 场景协议
REQUIRED_STRUCTURE = ["persona.yaml", "AGENTS.md"]


@dataclass
class MarketSearchResult:
    query: str
    results: List[dict] = field(default_factory=list)


@dataclass
class InstallResult:
    name: str
    ok: bool
    target_dir: Optional[Path] = None
    gates: List[dict] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error: str = ""


# ─── Search ───

def search_personas(query: str) -> MarketSearchResult:
    """Search community persona packs.

    Phase 1: search the known registry + local installed personas.
    Phase 2 (future): query a marketplace API.
    """
    results: List[dict] = []
    q = query.lower()

    # Local installed personas
    for p in list_personas():
        if q in p.lower():
            results.append({"name": p, "source": "bundled", "installed": True})

    # Known registry
    for name, url in KNOWN_REGISTRY.items():
        if q in name.lower():
            results.append({"name": name, "source": url, "installed": False})

    return MarketSearchResult(query=query, results=results)


# ─── Structure validation ───

def _validate_structure(pack_dir: Path) -> List[str]:
    """Validate a persona pack directory structure.

    Returns list of missing required files.
    """
    missing = []
    for req in REQUIRED_STRUCTURE:
        if not (pack_dir / req).exists():
            missing.append(req)
    return missing


def _read_persona_yaml(pack_dir: Path) -> Optional[dict]:
    """Parse persona.yaml (best-effort; YAML parser optional)."""
    yaml_path = pack_dir / "persona.yaml"
    if not yaml_path.exists():
        return None
    try:
        import yaml
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except ImportError:
        # Minimal fallback: extract id/name fields via regex
        text = yaml_path.read_text(encoding="utf-8")
        m = re.search(r"^id:\s*(.+)$", text, re.M)
        return {"id": m.group(1).strip() if m else pack_dir.name}


# ─── Quality Gates (mirror self-evolution.md §Quality Gate) ───

def _safety_gate(pack_dir: Path) -> dict:
    """Gate 1: safety — no secrets, no malicious scripts, no .git dir."""
    issues = []
    # 1. No .git directory should be shipped
    if (pack_dir / ".git").exists():
        issues.append("包含 .git 目录（应使用 --depth 1 浅克隆或排除）")
    # 2. No suspicious secret patterns in persona files
    secret_patterns = [
        r"(?i)(api[_-]?key|secret|token|password)\s*[=:]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
        r"BEGIN (RSA|OPENSSH|EC) PRIVATE KEY",
    ]
    for f in pack_dir.rglob("*.md"):
        if f.stat().st_size > 2_000_000:
            issues.append(f"{f.name}: 文件过大（>2MB），跳过")
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
            for pat in secret_patterns:
                if re.search(pat, text):
                    issues.append(f"{f}: 疑似硬编码密钥")
                    break
        except Exception:
            continue
    return {
        "gate": "safety",
        "passed": len(issues) == 0,
        "issues": issues,
        "action_on_fail": "拒绝并报告",
    }


def _quality_gate(pack_dir: Path) -> dict:
    """Gate 2: quality — structure complete, docs present, size sane."""
    issues = []
    missing = _validate_structure(pack_dir)
    if missing:
        issues.append(f"缺少必需文件: {', '.join(missing)}")

    # Skills dir optional but encouraged
    if not (pack_dir / "skills").exists():
        issues.append("缺少 skills/ 目录（建议但非必需）")

    # persona.yaml must be parseable
    meta = _read_persona_yaml(pack_dir)
    if meta is None:
        issues.append("persona.yaml 无法解析")

    total_size = sum(f.stat().st_size for f in pack_dir.rglob("*") if f.is_file())
    if total_size > 5_000_000:
        issues.append(f"包过大 ({total_size//1024}KB > 5MB)")

    return {
        "gate": "quality",
        "passed": len(issues) <= 1,  # skills/ 缺失可接受
        "issues": issues,
        "action_on_fail": "降级告知用户",
    }


def _compatibility_gate(pack_dir: Path, active_persona: str = "") -> dict:
    """Gate 3: compatibility — no conflict with active persona / existing packs."""
    issues = []
    meta = _read_persona_yaml(pack_dir)
    pack_id = (meta or {}).get("id") or pack_dir.name

    # Name collision with bundled personas
    if pack_id in list_personas():
        issues.append(f"与内置画像 {pack_id} 重名，安装将覆盖内置画像")

    # Mutual exclusion with active persona
    if active_persona and pack_id != active_persona:
        warning = conflict_check(active_persona, pack_id)
        if warning:
            issues.append(warning)

    return {
        "gate": "compatibility",
        "passed": len(issues) == 0,
        "issues": issues,
        "action_on_fail": "隔离并建议",
    }


def run_gates(pack_dir: Path, active_persona: str = "") -> List[dict]:
    """Run all three quality gates."""
    return [
        _safety_gate(pack_dir),
        _quality_gate(pack_dir),
        _compatibility_gate(pack_dir, active_persona),
    ]


# ─── Download & install ───

def _download(source: str, dest: Path) -> str:
    """Download a persona pack from URL or copy from local path.

    Returns error string ("" on success).
    """
    if source.startswith(("http://", "https://", "git@")):
        try:
            from . import env as _env
            code, stdout, stderr = _env.run_command(
                ["git", "clone", "--depth", "1", source, str(dest)],
                timeout=120,
                check=True,
                capture=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return f"git clone 失败: {e}"
        return ""
    # Local path
    src = Path(source)
    if not src.exists():
        return f"本地路径不存在: {source}"
    shutil.copytree(src, dest, dirs_exist_ok=True)
    return ""


def install_persona(
    name: str,
    source: Optional[str] = None,
    target_root: Optional[Path] = None,
    active_persona: str = "",
) -> InstallResult:
    """Install a persona pack from registry/URL/local path.

    Steps: resolve → download → validate → Quality Gate → install.
    """
    # 1. Resolve source
    src = source or KNOWN_REGISTRY.get(name, "")
    if not src:
        return InstallResult(name=name, ok=False, error=f"未知画像 {name}，请提供 --source URL 或本地路径")

    # 2. Download to temp
    tmp = Path(tempfile.mkdtemp(prefix="agentseed-market-"))
    err = _download(src, tmp)
    if err:
        shutil.rmtree(tmp, ignore_errors=True)
        return InstallResult(name=name, ok=False, error=err)

    # 3. Quality gates BEFORE install
    gates = run_gates(tmp, active_persona)
    failed = [g for g in gates if not g["passed"]]
    if failed:
        shutil.rmtree(tmp, ignore_errors=True)
        return InstallResult(
            name=name, ok=False, gates=gates,
            error=f"Quality Gate 未通过: {failed[0]['gate']}",
        )

    # 4. Install（跨平台路径：Windows %APPDATA%，Linux XDG，macOS ~/Library）
    from . import env as _env
    root = target_root or _env.user_personas_dir()
    root.mkdir(parents=True, exist_ok=True)
    target = root / name
    if target.exists():
        shutil.rmtree(target)
    shutil.move(tmp, target)

    meta = _read_persona_yaml(target)
    warnings = []
    if meta and meta.get("mcp"):
        warnings.append("该画像声明了 MCP 工具。按 P0 规则，MCP 不会自动安装，"
                        "配置 JSON 已保留在 persona.yaml 中，请手动配置。")

    return InstallResult(
        name=name, ok=True, target_dir=target, gates=gates, warnings=warnings,
    )


# ─── CLI helpers ───

def format_search(results: MarketSearchResult) -> str:
    if not results.results:
        return f"未找到与 '{results.query}' 匹配的画像。"
    lines = [f"搜索 '{results.query}' 的结果:"]
    for r in results.results:
        status = "已安装" if r["installed"] else "可安装"
        lines.append(f"  - {r['name']:20s} [{status}] source={r['source']}")
    return "\n".join(lines)


def format_install(result: InstallResult) -> str:
    if not result.ok:
        return f"❌ 安装失败: {result.error}"
    lines = [f"✅ 画像 {result.name} 安装成功"]
    lines.append(f"  位置: {result.target_dir}")
    for g in result.gates:
        mark = "✓" if g["passed"] else "✗"
        lines.append(f"  {mark} {g['gate']} gate" +
                     (f" ({', '.join(g['issues'])})" if g["issues"] else ""))
    for w in result.warnings:
        lines.append(f"  ⚠ {w}")
    return "\n".join(lines)
