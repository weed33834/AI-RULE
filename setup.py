"""setup.py — 与 pyproject.toml 配合工作，唯一目的是在 build_py 阶段
把仓库根的规则源文件（core/ personas/ capabilities/ personas/ adapters/
mcp.example.json）拷贝到 agentseed/_resources/，让它们随 wheel 分发。

这样 `pip install agentseed` 后无需外部仓库即可运行（_packaged_resources_root() 检测包内资源）。

dev 模式（pip install -e .）不触发 build_py 的拷贝，
此时 _resources/ 不存在，sync_rules 自动回退到 dev 模式（用 parent.parent = REPO_ROOT 读源）。
"""
import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist

ROOT = Path(__file__).resolve().parent
PKG_RESOURCES = ROOT / "src" / "agentseed" / "_resources"

# 必须随包分发的源文件/目录（相对仓库根）
PACKAGED_SOURCES = [
    "core",
    "personas",
    "capabilities",
    "adapters",
    "mcp.example.json",
]


def _sync_resources() -> None:
    """把规则源同步到 agentseed/_resources/。

    幂等：每次构建前清空 _resources/ 重建，避免旧文件残留。
    """
    if PKG_RESOURCES.exists():
        shutil.rmtree(PKG_RESOURCES)
    PKG_RESOURCES.mkdir(parents=True, exist_ok=True)
    for src in PACKAGED_SOURCES:
        src_path = ROOT / src
        dst_path = PKG_RESOURCES / src
        if not src_path.exists():
            continue
        if src_path.is_dir():
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)


class BuildPyCommand(build_py):
    """build_py 子类：构建前同步规则源到包内。"""

    def run(self):
        _sync_resources()
        super().run()


class SdistCommand(sdist):
    """sdist 子类：打包源分发前同步规则源到包内（让 sdist 也能直接 pip install）。"""

    def run(self):
        _sync_resources()
        super().run()


setup(cmdclass={"build_py": BuildPyCommand, "sdist": SdistCommand})
