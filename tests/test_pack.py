"""
场景规则包市场（pack 子系统）测试。

覆盖：市场清单、按需安装单个包（本地 file:// 市场夹具）、创建向导、
发布回路、卸载、以及 validate_packs 的市场感知（互斥引用未安装包不误报）。

运行: python -m pytest tests/test_pack.py -v
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from agentseed import pack as _pk  # noqa: E402
from agentseed.pack import (  # noqa: E402
    PackResult, add_pack, list_market, new_pack, publish_pack, remove_pack,
)
from validate_packs import validate_pack  # noqa: E402


# ─── 夹具：本地"市场"仓库 ────────────────────────────────────────────

def _make_market(tmp_path: Path, pack_id: str = "fixture-pack", good: bool = True) -> str:
    """在 tmp_path 下建一个 git 仓库模拟市场，含一个场景包。返回 file:// URL。"""
    market = tmp_path / "market"
    pdir = market / "personas" / pack_id
    (pdir / "prompts").mkdir(parents=True)
    (pdir / "skills").mkdir()
    if good:
        (pdir / "AGENTS.md").write_text("# Fixture Protocol\n", encoding="utf-8")
    # good=False 时缺 AGENTS.md → Quality Gate(quality) 必拦
    (pdir / "prompts" / "system-prompt.md").write_text("# System\n", encoding="utf-8")
    mutex = "\n  mutually_exclusive_with: []\n"
    if not good:
        mutex = "\n  mutually_exclusive_with: [not-a-real-pack]\n"
    (pdir / "persona.yaml").write_text(
        f"""profile:
  id: {pack_id}
  name: 夹具场景
  source_repo: file://{market}
  agent_mode:
    default: task
    allowed: [task, project]{mutex}
includes:
  core: [core/governance.md, core/interaction.md]
  profile: [personas/{pack_id}/AGENTS.md, personas/{pack_id}/prompts/system-prompt.md]
  skills: []
enables_capabilities: []
forbids_capabilities: []
""", encoding="utf-8")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=market, check=True)
    subprocess.run(["git", "add", "-A"], cwd=market, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-qm", "init"], cwd=market, check=True)
    return f"file://{market}"


# ─── 测试 ─────────────────────────────────────────────────────────────

def test_list_market_contains_core_packs(tmp_path):
    """市场清单应包含基础包（离线兜底或网络均可）。"""
    packs = list_market(tmp_path)
    ids = [p.id for p in packs]
    assert "coding" in ids and "novel" in ids and "paper" in ids


def test_new_pack_creates_template(tmp_path):
    result = new_pack("my-scenario", name="我的场景", scenario="数据分析", dest_root=tmp_path)
    assert result.ok, result.message
    pack_dir = tmp_path / "personas" / "my-scenario"
    for rel in ["persona.yaml", "AGENTS.md", "prompts/system-prompt.md"]:
        assert (pack_dir / rel).exists(), f"缺少 {rel}"
    assert (pack_dir / "skills").is_dir()


def test_new_pack_rejects_bad_id(tmp_path):
    assert new_pack("Bad_ID!", dest_root=tmp_path).ok is False


def test_publish_ok_and_materials(tmp_path):
    new_pack("my-scenario", name="我的场景", scenario="数据分析", dest_root=tmp_path)
    result = publish_pack("my-scenario", dest_root=tmp_path)
    assert result.ok, result.message
    assert result.details["pack_id"] == "my-scenario"
    assert "git add personas/my-scenario" in result.details["commit_cmd"]


def test_add_pack_from_local_market(tmp_path):
    url = _make_market(tmp_path)
    result = add_pack("fixture-pack", dest_root=tmp_path, source=url)
    assert result.ok, result.message
    assert (tmp_path / "personas" / "fixture-pack" / "persona.yaml").exists()
    assert result.gates, "应执行 Quality Gate"


def test_add_pack_rejects_missing(tmp_path):
    url = _make_market(tmp_path)
    result = add_pack("no-such-pack", dest_root=tmp_path, source=url)
    assert result.ok is False


def test_add_pack_rejects_bad_gate(tmp_path):
    url = _make_market(tmp_path, good=False)
    result = add_pack("fixture-pack", dest_root=tmp_path, source=url)
    assert result.ok is False
    assert "Quality Gate" in result.message or "校验" in result.message


def test_remove_pack_moves_to_trash(tmp_path):
    url = _make_market(tmp_path)
    assert add_pack("fixture-pack", dest_root=tmp_path, source=url).ok
    result = remove_pack("fixture-pack", dest_root=tmp_path)
    assert result.ok, result.message
    assert not (tmp_path / "personas" / "fixture-pack").exists()
    assert (tmp_path / "personas" / ".trash" / "fixture-pack").exists()


def test_validate_market_aware_mutex(tmp_path):
    """互斥引用市场存在但未本地安装的包 → 警告不报错。"""
    url = _make_market(tmp_path)
    assert add_pack("fixture-pack", dest_root=tmp_path, source=url).ok
    # 制造一个引用 novel（市场存在）但本地未安装 novel 的场景
    pdir = tmp_path / "personas" / "fixture-pack"
    manifest = pdir.joinpath("persona.yaml").read_text(encoding="utf-8")
    manifest = manifest.replace("mutually_exclusive_with: []",
                                "mutually_exclusive_with: [novel]")
    pdir.joinpath("persona.yaml").write_text(manifest, encoding="utf-8")
    report = validate_pack("fixture-pack", personas_dir=tmp_path / "personas",
                           ref_root=tmp_path)
    assert report["ok"], report["errors"]
    assert any("市场中但未安装" in w for w in report["warnings"])
