"""pytest 配置：测试结束后用 coding profile 恢复所有生成文件，避免仓库污染。"""
import pytest


@pytest.fixture(scope="session", autouse=True)
def restore_coding_after_tests():
    """所有测试完成后，用 coding profile 重新生成所有工具入口文件。

    原因：test_sync.py 中的 test_all_tools_output / test_cursor_frontmatter / test_drift_overwritten
    会用不同 profile 写入仓库实际文件。不清理会导致仓库工作区的生成文件
    profile 标识错误（如 GEMINI.md 变成 conversation）。
    """
    yield  # 运行所有测试

    # 测试结束后恢复
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
    from sync_rules import build_ruleset, write_tool_file, TOOL_OUTPUT

    rs = build_ruleset("coding")
    for tool in TOOL_OUTPUT:
        write_tool_file(tool, "coding", rs)
    print("\n[conftest] 已用 coding profile 恢复所有生成文件")
