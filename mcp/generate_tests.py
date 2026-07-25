#!/usr/bin/env python
"""MCP: generate_tests — 为 Python 代码生成测试骨架。

用法:
    python mcp/generate_tests.py --path <file.py> [--framework pytest|unittest] [--output <test_file.py>]

功能:
    1. 分析目标文件的所有公开函数/方法
    2. 为每个函数生成：正常路径 + 边界值 + 异常路径 测试
    3. 输出可独立运行的测试文件
"""

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


class FunctionExtractor(ast.NodeVisitor):
    """AST 遍历器，提取函数定义信息。"""

    def __init__(self, source_file: str):
        self.source_file = source_file
        self.functions: list[dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # 跳过私有函数（_ 开头）
        if node.name.startswith("_"):
            self.generic_visit(node)
            return

        # 计算参数列表
        params = []
        for arg in node.args.args:
            param_info = {"name": arg.arg}
            if arg.annotation:
                param_info["type"] = ast.unparse(arg.annotation)
            params.append(param_info)

        # 计算返回类型
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        self.functions.append({
            "name": node.name,
            "params": params,
            "return_type": return_type,
            "line_no": node.lineno,
            "has_docstring": (
                isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, (ast.Constant, ast.Str))
                if node.body
                else False
            ),
        })
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        # 同样处理异步函数
        if node.name.startswith("_"):
            self.generic_visit(node)
            return

        params = []
        for arg in node.args.args:
            param_info = {"name": arg.arg}
            if arg.annotation:
                param_info["type"] = ast.unparse(arg.annotation)
            params.append(param_info)

        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        self.functions.append({
            "name": node.name,
            "params": params,
            "return_type": return_type,
            "line_no": node.lineno,
            "has_docstring": (
                isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, (ast.Constant, ast.Str))
                if node.body
                else False
            ),
            "is_async": True,
        })
        self.generic_visit(node)


def generate_pytest_tests(source_path: str, module_name: str, funcs: list[dict]) -> str:
    """生成 pytest 测试骨架。"""
    lines = [
        f'"""自动生成的测试骨架 — 源文件: {source_path}"""',
        "",
        "import pytest",
    ]

    # 添加类型相关的 import
    types_needed = set()
    for f in funcs:
        for p in f.get("params", []):
            if p.get("type"):
                types_needed.add(p["type"])
        if f.get("return_type"):
            types_needed.add(f["return_type"])

    lines.append(f"from {module_name} import " + ", ".join(f["name"] for f in funcs) if funcs else f"# 未找到公开函数")
    lines.append("")
    lines.append("")

    for func in funcs:
        func_name = func["name"]
        is_async = func.get("is_async", False)
        params = func.get("params", [])

        lines.append(f"# ── {func_name} ──")
        lines.append("")

        # 正常路径
        test_class = f"class Test{func_name.title().replace('_', '')}:"
        lines.append(test_class)

        # Test 1: 正常路径
        lines.append(f'    """测试 {func_name} — 正常路径"""')
        lines.append("")
        lines.append("    def test_normal_path(self):")
        # 生成调用示例
        args_str = ", ".join(
            f"{p['name']}='test_{p['name']}'" if p.get("type") and "str" in p["type"] else f"{p['name']}=42"
            for p in params
        )
        call_prefix = "await " if is_async else ""
        lines.append(f"        result = {call_prefix}{func_name}({args_str})")
        lines.append("        assert result is not None")
        lines.append("")

        # Test 2: 边界值
        lines.append("    def test_boundary_values(self):")
        boundary_args = ", ".join(
            f"{p['name']}=None" if p.get("type") else f"{p['name']}=0" for p in params
        )
        lines.append(f"        result = {call_prefix}{func_name}({boundary_args})")
        lines.append("        assert result is not None")
        lines.append("")

        # Test 3: 异常路径
        lines.append("    def test_invalid_inputs(self):")
        lines.append("        with pytest.raises((TypeError, ValueError)):")
        lines.append(f"            {call_prefix}{func_name}()")
        lines.append("")

    return "\n".join(lines)


def generate_unittest_tests(source_path: str, module_name: str, funcs: list[dict]) -> str:
    """生成 unittest 测试骨架。"""
    lines = [
        f'"""自动生成的测试骨架 — 源文件: {source_path}"""',
        "",
        "import unittest",
        f"from {module_name} import " + ", ".join(f["name"] for f in funcs) if funcs else "# 未找到公开函数",
        "",
        "",
    ]

    test_class = f"class Test{module_name.capitalize()}(unittest.TestCase):"
    lines.append(test_class)

    for func in funcs:
        func_name = func["name"]
        params = func.get("params", [])

        args_str = ", ".join(
            f"{p['name']}='test_{p['name']}'" if p.get("type") and "str" in p["type"] else f"{p['name']}=42"
            for p in params
        )

        lines.append(f"    def test_{func_name}_normal(self):")
        lines.append(f"        result = {func_name}({args_str})")
        lines.append("        self.assertIsNotNone(result)")
        lines.append("")

        lines.append(f"    def test_{func_name}_boundary(self):")
        boundary_args = ", ".join(
            f"{p['name']}=None" if p.get("type") else f"{p['name']}=0" for p in params
        )
        lines.append(f"        result = {func_name}({boundary_args})")
        lines.append("        self.assertIsNotNone(result)")
        lines.append("")

        lines.append(f"    def test_{func_name}_invalid(self):")
        lines.append(f"        with self.assertRaises((TypeError, ValueError)):")
        lines.append(f"            {func_name}()")
        lines.append("")

    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    unittest.main()")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="测试骨架生成器")
    parser.add_argument("--path", required=True, help="目标 Python 文件")
    parser.add_argument("--framework", default="pytest", choices=["pytest", "unittest"], help="测试框架")
    parser.add_argument("--output", default=None, help="输出文件路径")
    args = parser.parse_args()

    source = Path(args.path).resolve()
    if not source.exists():
        print(json.dumps({"error": f"文件不存在: {source}"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    # 分析源码
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"))
    except SyntaxError as e:
        print(json.dumps({"error": f"语法错误: {e}"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    extractor = FunctionExtractor(str(source))
    extractor.visit(tree)

    if not extractor.functions:
        print(json.dumps({"warning": "未找到公开函数", "generated": False}, ensure_ascii=False, indent=2))
        sys.exit(0)

    # 确定模块名
    module_name = source.stem

    # 生成测试
    if args.framework == "pytest":
        test_code = generate_pytest_tests(str(source), module_name, extractor.functions)
    else:
        test_code = generate_unittest_tests(str(source), module_name, extractor.functions)

    # 输出
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(test_code, encoding="utf-8")
        print(json.dumps({
            "generated": True,
            "framework": args.framework,
            "target": str(source),
            "output": str(output_path),
            "functions_found": len(extractor.functions),
            "function_names": [f["name"] for f in extractor.functions],
        }, ensure_ascii=False, indent=2))
    else:
        print(test_code)


if __name__ == "__main__":
    main()
