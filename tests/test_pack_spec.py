"""
场景规则包清单校验测试（SCENARIO_PACK_SPEC.md 配套）。

运行 scripts/validate_packs.py 的校验逻辑，断言全部包通过：
  - manifest 结构完整（id/name/source_repo/agent_mode）
  - includes 引用文件存在且非空（防止 forge 产物出现 [missing]）
  - 能力 id 有效、互斥关系对称

这是"规则包引用漂移 → forge 产物缺失 → 跑不通"的 CI 防线。
运行: python -m pytest tests/test_pack_spec.py -v
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_packs import REPO_ROOT as V_ROOT  # noqa: E402
from validate_packs import PERSONAS_DIR, validate_all, validate_pack  # noqa: E402


def test_validator_root_points_at_repo():
    assert V_ROOT == REPO_ROOT
    assert PERSONAS_DIR.is_dir()


def test_all_packs_pass_validation():
    report = validate_all()
    failures = [p for p in report["packs"] if not p["ok"]]
    assert not failures, f"存在校验失败的包: {failures}"


def test_every_pack_has_profile_agents_md():
    """每个包必须带场景协议源文件（缺失=forge 产物 [missing]，历史坑）。"""
    for pack_dir in sorted(PERSONAS_DIR.iterdir()):
        if not pack_dir.is_dir() or pack_dir.name.startswith("_"):
            continue
        agents = pack_dir / "AGENTS.md"
        assert agents.exists(), f"{pack_dir.name}: AGENTS.md 缺失"
        assert agents.stat().st_size > 0, f"{pack_dir.name}: AGENTS.md 为空"


def test_mutex_symmetry_via_validator():
    report = validate_all()
    sym_problems = [p for p in report["packs"] if p["id"] == "(symmetry)"]
    assert not sym_problems, sym_problems


def test_validate_pack_ok_for_coding():
    result = validate_pack("coding")
    assert result["ok"], result
