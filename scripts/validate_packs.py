"""validate_packs.py — 场景规则包（Scenario Pack）清单校验器。

依据 docs/SCENARIO_PACK_SPEC.md 校验全部 personas/<id>/ 包：
  - manifest 结构（id/name/source_repo/mutex/agent_mode）
  - includes.core / profile / skills 引用文件存在且非空
  - enables/forbids 能力 id 存在于 capabilities/<id>/
  - 互斥关系对称性（A 列 B ⇒ B 列 A）

用法：
  python scripts/validate_packs.py           # 全部校验，失败退出码 1
  python scripts/validate_packs.py --json    # JSON 报告（供脚本消费）

这是"forge 产物出现 [missing] / 跑不通"的 CI 防线：任何引用漂移都会被拦下。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PERSONAS_DIR = REPO_ROOT / "personas"
CAPABILITIES_DIR = REPO_ROOT / "capabilities"

VALID_MODES = {"task", "project", "autonomous"}


def _load_manifest(path: Path):
    """加载 manifest。优先 PyYAML；缺失时回退最小解析器（保证零依赖可用）。"""
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        pass
    # 最小 fallback：只解析本校验需要的顶层键（够用即可，正常环境走 PyYAML）
    text = path.read_text(encoding="utf-8")
    data = {"profile": {}}
    current = None
    list_key = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("profile:") and not stripped.startswith("profile_") and current is None:
            current = "profile"
            continue
        if current == "profile":
            for key in ("id:", "name:", "source_repo:", "mutually_exclusive_with:"):
                if stripped.startswith(key):
                    data["profile"][key[:-1]] = stripped.split(":", 1)[1].strip()
                    break
            if stripped.startswith("- ") and list_key:
                data["profile"].setdefault(list_key, []).append(stripped[2:].strip())
            if stripped.startswith("mutually_exclusive_with:"):
                list_key = "mutually_exclusive_with"
    return data


def _capability_exists(cap: str) -> bool:
    """能力 id 存在性：capabilities/<cap>/ 或嵌套 capabilities/*/<cap>/（如 dar → research/dar）。"""
    if (CAPABILITIES_DIR / cap).is_dir():
        return True
    for sub in CAPABILITIES_DIR.iterdir():
        if sub.is_dir() and (sub / cap).is_dir():
            return True
    return False


def _referenced_files(pack_dir: Path, manifest: dict) -> list:
    files = []
    includes = manifest.get("includes", {})
    for section in ("core", "profile", "skills"):
        for rel in includes.get(section, []) or []:
            files.append((section, rel, REPO_ROOT / rel))
    return files


def validate_pack(pack_id: str) -> dict:
    pack_dir = PERSONAS_DIR / pack_id
    errors, warnings = [], []
    manifest_path = pack_dir / "persona.yaml"
    manifest = _load_manifest(manifest_path)
    profile = manifest.get("profile", {})

    # 1) 基本结构
    if manifest_path.exists() is False:
        return {"id": pack_id, "ok": False, "errors": ["persona.yaml 缺失"], "warnings": []}
    pid = profile.get("id", "")
    if pid != pack_id:
        errors.append(f"profile.id '{pid}' != 目录名 '{pack_id}'")
    if not profile.get("name"):
        errors.append("profile.name 缺失")
    if not profile.get("source_repo"):
        errors.append("profile.source_repo 缺失")

    # 2) agent_mode
    mode = profile.get("agent_mode", {})
    if mode.get("default") not in VALID_MODES:
        errors.append(f"agent_mode.default 非法: {mode.get('default')!r}")
    allowed = mode.get("allowed", [])
    if not allowed:
        errors.append("agent_mode.allowed 为空")
    elif mode.get("default") not in allowed:
        errors.append("agent_mode.default 不在 allowed 中")

    # 3) includes 引用存在且非空
    includes = manifest.get("includes", {})
    if not includes.get("core"):
        errors.append("includes.core 为空")
    if not includes.get("profile"):
        errors.append("includes.profile 为空")
    for section, rel, path in _referenced_files(pack_dir, manifest):
        if not path.exists():
            errors.append(f"includes.{section} 引用不存在: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"includes.{section} 引用为空文件: {rel}")

    # 4) 能力 id 有效性
    for section in ("enables_capabilities", "forbids_capabilities"):
        for cap in profile.get(section, []) or []:
            if not _capability_exists(cap):
                errors.append(f"{section} 引用不存在的能力: {cap}")

    # 5) 互斥对称性（跨包检查由 validate_all 做，这里只报本包声明格式）
    mutex = profile.get("mutually_exclusive_with", []) or []
    if not mutex:
        warnings.append("mutually_exclusive_with 为空（无法参与互斥校验）")
    for other in mutex:
        if not (PERSONAS_DIR / other / "persona.yaml").exists():
            errors.append(f"mutually_exclusive_with 引用不存在包: {other}")

    return {"id": pack_id, "ok": not errors, "errors": errors, "warnings": warnings}


def _check_mutex_symmetry() -> list:
    """跨包互斥对称性：A 列 B ⇒ B 列 A。"""
    problems = []
    declared = {}
    for pack_dir in sorted(PERSONAS_DIR.iterdir()):
        if not pack_dir.is_dir() or pack_dir.name.startswith("_"):
            continue
        manifest = _load_manifest(pack_dir / "persona.yaml")
        declared[pack_dir.name] = set(manifest.get("profile", {}).get("mutually_exclusive_with", []) or [])
    for a, bs in declared.items():
        for b in bs:
            if b in declared and a not in declared[b]:
                problems.append(f"互斥不对称: {a} 列了 {b}，但 {b} 未列 {a}")
    return problems


def validate_all() -> dict:
    packs = []
    for pack_dir in sorted(PERSONAS_DIR.iterdir()):
        if not pack_dir.is_dir() or pack_dir.name.startswith("_"):
            continue
        packs.append(validate_pack(pack_dir.name))
    symmetry = _check_mutex_symmetry()
    for prob in symmetry:
        packs.append({"id": "(symmetry)", "ok": False, "errors": [prob], "warnings": []})
    return {"ok": all(p["ok"] for p in packs), "packs": packs}


def main() -> int:
    parser = argparse.ArgumentParser(description="校验场景规则包清单（SCENARIO_PACK_SPEC.md）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    args = parser.parse_args()

    # 强制 UTF-8：避免 Windows GBK 控制台无法编码 ✗/⚠ 等字符导致崩溃
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

    report = validate_all()
    if args.json:
        sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        return 0 if report["ok"] else 1

    print("场景规则包校验（SCENARIO_PACK_SPEC v1.0）")
    print("=" * 60)
    for p in report["packs"]:
        mark = "OK " if p["ok"] else "FAIL"
        print(f"  [{mark}] {p['id']}")
        for e in p["errors"]:
            print(f"        ✗ {e}")
        for w in p["warnings"]:
            print(f"        ⚠ {w}")
    print("=" * 60)
    print(f"  共 {len(report['packs'])} 项检查，{'全部通过' if report['ok'] else '存在失败'}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
