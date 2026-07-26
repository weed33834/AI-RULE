"""ai-rule CLI：分发层入口。

用法：
    ai-rule list
    ai-rule apply --profile coding --tool claude-code
    ai-rule apply --profile coding --tool all
    ai-rule apply --profile coding --tool claude-code --mode full
    ai-rule apply --profile coding --tool all --output /path/to/project
    ai-rule verify                       # 验证全部 profile（CI 用）
    ai-rule verify --profile coding      # 验证单个 profile
"""
import argparse
import sys
from pathlib import Path

from . import sync_rules as _sr


def cmd_list(args) -> int:
    # 刷新资源根，响应当前 AI_RULE_REPO 环境变量
    _sr.refresh_resources_root()
    profiles = _sr.list_profiles()
    print("可用 Profile:")
    for p in profiles:
        print(f"  - {p}")
    print()
    print("可用 Tool:")
    for t in _sr.TOOL_OUTPUT:
        out = _sr.TOOL_OUTPUT[t]
        limit = _sr.TOOL_CHAR_LIMIT.get(t)
        suffix = f" (limit={limit})" if limit else ""
        print(f"  - {t:12s} -> {out}{suffix}")
    print()
    print(f"Rule Hub 资源根: {_sr.RESOURCES_ROOT}")
    print(f"资源来源: {_sr.resources_source()}")
    return 0


def cmd_apply(args) -> int:
    profile = args.profile
    tool = args.tool
    mode = args.mode

    # 刷新资源根，响应当前 AI_RULE_REPO 环境变量
    _sr.refresh_resources_root()

    if profile not in _sr.list_profiles():
        print(f"error: 未知 profile '{profile}'，可用: {_sr.list_profiles()}", file=sys.stderr)
        return 1
    if tool != "all" and tool not in _sr.TOOL_OUTPUT:
        print(f"error: 未知 tool '{tool}'，可用: all 或 {list(_sr.TOOL_OUTPUT)}", file=sys.stderr)
        return 1

    # 装配规则集（读源，源根由 sync_rules 自动检测）
    ruleset = _sr.build_ruleset(profile, mode=mode)

    # 产物输出根：
    # - --output 指定 → 用户目录
    # - 否则默认 → 当前工作目录（符合 pip install 后端用户期望：
    #   在用户项目里运行 ai-rule apply 应在项目里生成 AGENTS.md / CLAUDE.md）
    # - dev 模式（在 Rule Hub 仓库内运行）：cwd 通常 == RESOURCES_ROOT，行为不变
    output_dir_changed = True  # 默认就要切到 cwd（refresh_resources_root 把 OUTPUT_ROOT 重置到了 RESOURCES_ROOT）
    if args.output:
        output_dir = Path(args.output).resolve()
    else:
        output_dir = Path.cwd().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    _sr.set_output_root(output_dir)
    display_root = output_dir

    try:
        budget_status = "✓ 预算内" if len(ruleset) <= _sr.SKELETON_BUDGET_BYTES else "✗ 超预算"
        print(f"装配 profile={profile} mode={mode}")
        print(f"规则集大小: {len(ruleset)} 字符 (预算 {_sr.SKELETON_BUDGET_BYTES}) {budget_status}")

        tools = list(_sr.TOOL_OUTPUT.keys()) if tool == "all" else [tool]
        for t in tools:
            out_path = _sr.write_tool_file(t, profile, ruleset, mode=mode)
            try:
                rel = out_path.relative_to(display_root)
            except ValueError:
                rel = out_path
            extra = ""
            char_limit = _sr.TOOL_CHAR_LIMIT.get(t)
            if char_limit:
                extra = f" [limit={char_limit}, {'分片' if len(ruleset) > char_limit else '单文件'}]"
            print(f"  [{t}] -> {rel}{extra}")
    finally:
        # 恢复 OUTPUT_ROOT（避免污染后续调用）
        if output_dir_changed:
            _sr.reset_output_root()
    return 0


def cmd_verify(args) -> int:
    """CI 用：硬断言验证 skeleton 模式产物达标（预算、P0 内联、内容不丢、INDEX 完整）。
    任一断言失败抛 AssertionError，退出码 1。
    """
    _sr.refresh_resources_root()
    try:
        reports = _sr.verify_ruleset(profile_id=args.profile, strict_budget=True)
    except AssertionError as e:
        print(f"[FAIL] {e}", file=sys.stderr)
        return 1

    print("=" * 60)
    print("ai-rule verify: skeleton 模式硬断言报告")
    print("=" * 60)
    print(f"{'profile':20s} {'size':>8s}  {'margin':>7s}  P0  deferred  INDEX")
    for pid, r in reports.items():
        p0 = "✓" if r["p0_inlined"] else "✗"
        df = "✓" if r["deferred_intact"] else "✗"
        ix = "✓" if r["index_complete"] else "✗"
        margin = f"+{r['budget_margin']}" if r["budget_ok"] else f"{r['budget_margin']}"
        print(f"{pid:20s} {r['size']:>7d}B  {margin:>7s}  {p0}   {df}         {ix}")
    print()
    all_ok = all(r["budget_ok"] and r["p0_inlined"] and r["deferred_intact"] and r["index_complete"]
                 for r in reports.values())
    print(f"[{'PASS' if all_ok else 'FAIL'}] {len(reports)} 个 profile 验证{'通过' if all_ok else '失败'}")
    return 0 if all_ok else 1


def main():
    parser = argparse.ArgumentParser(
        prog="ai-rule",
        description="Rule Hub CLI — 装配 AI 协作规则（skeleton + 按需加载）",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="列出可用 profile 和 tool")
    p_list.set_defaults(func=cmd_list)

    p_apply = sub.add_parser("apply", help="生成指定 profile+tool 的规则文件")
    p_apply.add_argument("--profile", required=True, help="主 profile (如 coding/novel/paper...)")
    p_apply.add_argument("--tool", required=True,
                         help="目标工具 (claude-code/gemini/cursor/trae/agents-md/all/...)")
    p_apply.add_argument("--mode", default="skeleton", choices=["skeleton", "full"],
                         help="装配模式（默认 skeleton）")
    p_apply.add_argument("--output", default=None,
                         help="生成产物输出目录（默认当前工作目录）")
    p_apply.set_defaults(func=cmd_apply)

    p_verify = sub.add_parser("verify", help="CI 用：硬断言验证 skeleton 模式产物达标")
    p_verify.add_argument("--profile", default=None,
                          help="只验证指定 profile（默认全部）")
    p_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
