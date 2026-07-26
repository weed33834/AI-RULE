"""
打包资源检测测试：验证 ai_rule/_resources/ 资源根检测优先级和路径解析协议。

测试目标：
1. dev 模式下（无 _resources/）_packaged_resources_root() 返回 None
2. 当 _resources/ 存在时（pip 安装模式），_packaged_resources_root() 返回该路径
3. AI_RULE_REPO 环境变量优先级高于 packaged（让用户能热覆盖规则）
4. refresh_resources_root() 清缓存后能正确重新检测
5. build_ruleset 在 packaged 模式下能成功装配规则（包内资源可被 Read）

运行: python -m pytest tests/test_packaged.py -v
"""
import os
import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
# 直接从 ai_rule.sync_rules 拿到真实模块（含模块级状态 _RESOURCES_ROOT_CACHE 等）
# scripts/sync_rules.py shim 用 from ai_rule.sync_rules import * 不会带下划线开头的属性
sys.path.insert(0, str(REPO_ROOT))

from ai_rule import sync_rules as _sr  # noqa: E402
from ai_rule.sync_rules import (  # noqa: E402
    _packaged_resources_root, _find_rule_hub_root, refresh_resources_root,
    resources_source, build_ruleset,
)


PKG_DIR = Path(_sr.__file__).resolve().parent
RESOURCES_DIR = PKG_DIR / "_resources"


@pytest.fixture
def packaged_resources_dir():
    """在 ai_rule/_resources/ 创建临时 _resources/ 目录，测试后清理。

    使用真实 ai_rule/_resources/ 路径而非 tmp_path，因为 _packaged_resources_root()
    用 Path(__file__).resolve().parent / "_resources" 检测，必须在那里创建。
    """
    # 备份当前 cache 状态
    saved_cache = _sr._RESOURCES_ROOT_CACHE
    saved_source = _sr._RESOURCES_SOURCE
    saved_env = os.environ.pop("AI_RULE_REPO", None)

    # 创建 _resources/ + 拷贝真实源让 build_ruleset 能装配
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    for src in ["manifests", "core", "profiles", "capabilities", "adapters", "mcp.example.json"]:
        src_path = REPO_ROOT / src
        dst_path = RESOURCES_DIR / src
        if dst_path.exists():
            shutil.rmtree(dst_path) if dst_path.is_dir() else dst_path.unlink()
        if src_path.is_dir():
            shutil.copytree(src_path, dst_path)
        elif src_path.is_file():
            shutil.copy2(src_path, dst_path)

    # 清缓存强制重新检测
    _sr._RESOURCES_ROOT_CACHE = None
    _sr._RESOURCES_SOURCE = None

    yield RESOURCES_DIR

    # 清理：删除临时 _resources/，恢复 cache 和环境变量
    if RESOURCES_DIR.exists():
        shutil.rmtree(RESOURCES_DIR)
    _sr._RESOURCES_ROOT_CACHE = saved_cache
    _sr._RESOURCES_SOURCE = saved_source
    if saved_env is not None:
        os.environ["AI_RULE_REPO"] = saved_env
    else:
        os.environ.pop("AI_RULE_REPO", None)
    # 重新刷新让其他测试回到 dev 模式
    _sr._RESOURCES_ROOT_CACHE = None
    _sr._RESOURCES_SOURCE = None
    refresh_resources_root()


def _clear_cache():
    """清掉模块级缓存让下次检测重新跑"""
    _sr._RESOURCES_ROOT_CACHE = None
    _sr._RESOURCES_SOURCE = None


def test_packaged_resources_root_returns_none_in_dev_mode():
    """dev 模式下 _resources/ 不存在，应返回 None"""
    if RESOURCES_DIR.exists():
        pytest.skip("ai_rule/_resources/ 已存在（构建环境），跳过 dev 模式测试")
    result = _packaged_resources_root()
    assert result is None, f"dev 模式应返回 None，实际: {result}"
    print("[PASS] dev 模式下 _packaged_resources_root() 返回 None")


def test_packaged_resources_root_detects_when_exists(packaged_resources_dir):
    """当 _resources/ 存在时（pip 安装模式），应返回该路径"""
    result = _packaged_resources_root()
    assert result is not None, "_resources/ 存在时应返回路径"
    assert result == RESOURCES_DIR, f"应返回 {RESOURCES_DIR}，实际: {result}"
    print(f"[PASS] _packaged_resources_root() 正确检测到 {result}")


def test_find_rule_hub_root_uses_packaged_when_no_env(packaged_resources_dir):
    """无 AI_RULE_REPO 时，_find_rule_hub_root 应优先用 packaged"""
    os.environ.pop("AI_RULE_REPO", None)
    _clear_cache()

    root = _find_rule_hub_root()
    assert root == RESOURCES_DIR, f"无 env 时应返回 packaged: {RESOURCES_DIR}，实际: {root}"
    assert _sr.resources_source() == "packaged", \
        f"resources_source 应为 'packaged'，实际: {_sr.resources_source()}"
    print("[PASS] 无 AI_RULE_REPO 时 _find_rule_hub_root 使用 packaged 资源")


def test_ai_rule_repo_env_takes_priority_over_packaged(packaged_resources_dir, tmp_path):
    """AI_RULE_REPO 优先级高于 packaged（用户热覆盖规则场景）"""
    # 用 tmp_path 创建一个假的 Rule Hub 仓库
    fake_repo = tmp_path / "fake-rule-hub"
    fake_repo.mkdir()
    (fake_repo / "manifests").mkdir()
    (fake_repo / "core").mkdir()
    # 写一个最小 manifest 让 _find_rule_hub_root 命中
    (fake_repo / "manifests" / "coding.yaml").write_text(
        "includes:\n  core:\n    - core/governance.md\n  profile:\n    - profiles/coding/AGENTS.md\n",
        encoding="utf-8",
    )

    os.environ["AI_RULE_REPO"] = str(fake_repo)
    _clear_cache()

    root = _find_rule_hub_root()
    assert root.resolve() == fake_repo.resolve(), \
        f"AI_RULE_REPO 优先级应高于 packaged，期望 {fake_repo}，实际: {root}"
    assert _sr.resources_source() == "env", \
        f"resources_source 应为 'env'，实际: {_sr.resources_source()}"
    print("[PASS] AI_RULE_REPO 环境变量优先于 packaged 资源")


def test_refresh_resources_root_clears_cache(packaged_resources_dir):
    """refresh_resources_root 应清缓存重新检测"""
    _clear_cache()
    root1 = _find_rule_hub_root()
    assert root1 == RESOURCES_DIR
    # 模拟 cache 被污染
    _sr._RESOURCES_ROOT_CACHE = Path("/nonexistent/path")
    # refresh 后应回到正确路径
    root2 = refresh_resources_root()
    assert root2 == RESOURCES_DIR, f"refresh 后应回到 packaged，实际: {root2}"
    print("[PASS] refresh_resources_root 正确清缓存重新检测")


def test_build_ruleset_works_in_packaged_mode(packaged_resources_dir):
    """packaged 模式下 build_ruleset 应能成功装配规则（核心/governance 可被读）"""
    os.environ.pop("AI_RULE_REPO", None)
    _clear_cache()
    refresh_resources_root()

    rs = build_ruleset("coding", mode="skeleton")
    assert "CORE LAYER" in rs, "packaged 模式下 build_ruleset 缺 CORE LAYER"
    assert "ON-DEMAND INDEX" in rs, "packaged 模式下 build_ruleset 缺 ON-DEMAND INDEX"
    # 验证 governance.md 内容真的从 _resources/ 读到了
    assert "P0" in rs or "红线" in rs or "red line" in rs.lower(), \
        "packaged 模式下未读到 governance.md 内容"
    # 验证 ON-DEMAND INDEX 头部含包内资源路径记录
    assert str(RESOURCES_DIR) in rs or "_resources" in rs, \
        "ON-DEMAND INDEX 应记录资源根为包内 _resources/ 路径"
    assert "包内打包资源" in rs or "packaged" in rs.lower() or "pip install" in rs, \
        "ON-DEMAND INDEX 应提示资源来源为包内打包"
    print("[PASS] packaged 模式下 build_ruleset 成功装配规则")


def test_packaged_index_protocol_includes_path_resolution():
    """ON-DEMAND INDEX 路径解析协议文本必须包含包内资源查找步骤"""
    os.environ.pop("AI_RULE_REPO", None)
    _clear_cache()
    refresh_resources_root()

    rs = build_ruleset("coding", mode="skeleton")
    # 协议文本必须提到通过 python -c "import ai_rule" 找包内 _resources 路径
    assert "import ai_rule" in rs, "ON-DEMAND INDEX 路径协议缺包内查找步骤"
    assert "_resources" in rs, "ON-DEMAND INDEX 路径协议缺 _resources 引用"
    assert "git clone" in rs.lower() or "clone" in rs.lower(), "协议缺 clone fallback"
    print("[PASS] ON-DEMAND INDEX 含完整路径解析协议（含包内资源查找步骤）")


if __name__ == "__main__":
    # 直接运行模式：用 pytest 执行
    sys.exit(pytest.main([__file__, "-v", "-s"]))
