"""ai-rule CLI：分发层入口。

用法：
    ai-rule list
    ai-rule setup                          # 零配置默认链路（推荐入门）
    ai-rule setup --intent "帮我写小说"      # 口语化意图自动切 profile
    ai-rule apply --profile coding --tool claude-code
    ai-rule apply --profile coding --tool all
    ai-rule apply --profile coding --tool claude-code --mode full
    ai-rule apply --profile coding --tool all --output /path/to/project
    ai-rule apply --profile coding --tool claude-code --emit-constraints
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


def cmd_setup(args) -> int:
    """零配置默认链路：自动检测 profile + tool + emit-constraints。
    用户口语化请求"帮我配置规则"时走这条路径。
    """
    _sr.refresh_resources_root()
    user_intent = args.intent or ""
    output_dir = Path(args.output).resolve() if args.output else None

    result = _sr.setup_default(user_intent=user_intent, output_dir=output_dir)

    profile = result["profile"]
    tool = result["tool"]
    budget_status = "✓ 预算内" if result["ruleset_size"] <= _sr.SKELETON_BUDGET_BYTES else "✗ 超预算"

    print("=" * 60)
    print("ai-rule setup: 默认链路已配置")
    print("=" * 60)
    print(f"  profile : {profile}")
    print(f"  tool    : {tool}")
    print(f"  mode    : skeleton")
    print(f"  output  : {result['output']}")
    print(f"  ruleset : {result['ruleset_path']} ({result['ruleset_size']} 字节 {budget_status})")

    if result["hook_files"]:
        print(f"\n  hook 适配器（{len(result['hook_files'])} 个文件已分发）：")
        for hf in result["hook_files"]:
            print(f"    - {hf}")
        print("\n  下一步：重启你的 AI 工具，hook 自动生效。")
    else:
        print("\n  该平台不支持 hook（仅软引导），规则文件已生成。")

    if user_intent:
        print(f"\n  （检测到用户意图: {user_intent!r}，已自动切换 profile）")
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

            # 可选：同时分发 hook 适配器
            if getattr(args, "emit_constraints", False):
                hook_files = _sr.emit_constraints(t)
                for hf in hook_files:
                    try:
                        hf_rel = hf.relative_to(display_root)
                    except ValueError:
                        hf_rel = hf
                    print(f"           hook -> {hf_rel}")
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

    print("=" * 80)
    print("ai-rule verify: skeleton 模式硬断言报告")
    print("=" * 80)
    print(f"{'profile':18s} {'size':>7s}  {'margin':>7s}  P0  DEF  IDX  MTX  CAP  GAT")
    for pid, r in reports.items():
        p0 = "✓" if r["p0_inlined"] else "✗"
        df = "✓" if r["deferred_intact"] else "✗"
        ix = "✓" if r["index_complete"] else "✗"
        mt = "✓" if r.get("mutex_symmetric", True) else "✗"
        cp = "✓" if r.get("capabilities_consistent", True) else "✗"
        gt = "✓" if r.get("gates_files_exist", True) else "✗"
        margin = f"+{r['budget_margin']}" if r["budget_ok"] else f"{r['budget_margin']}"
        print(f"{pid:18s} {r['size']:>6d}B  {margin:>7s}  {p0}   {df}   {ix}   {mt}   {cp}   {gt}")
    print()
    print("  P0=P0内联  DEF=deferred完整  IDX=INDEX段  MTX=互斥对称  CAP=cap无冲突  GAT=gates文件存在")
    all_ok = all(
        r["budget_ok"] and r["p0_inlined"] and r["deferred_intact"] and r["index_complete"]
        and r.get("mutex_symmetric", True)
        and r.get("capabilities_consistent", True)
        and r.get("gates_files_exist", True)
        for r in reports.values()
    )
    print(f"[{'PASS' if all_ok else 'FAIL'}] {len(reports)} 个 profile 验证{'通过' if all_ok else '失败'}")
    return 0 if all_ok else 1


def cmd_check_output(args) -> int:
    """AI 交付前自检：按 profile + output_type 校验输出 schema。
    失败时给出明确的"哪里错了 + 怎么修"反馈，触发 AI 自动重写。
    """
    from . import output_schemas as _os
    _sr.refresh_resources_root()
    content = args.content
    if args.file:
        from pathlib import Path
        content = Path(args.file).read_text(encoding="utf-8")

    result = _os.validate_for_profile(args.profile, args.output_type, content)
    print("=" * 60)
    print(f"ai-rule check-output: {args.profile}/{args.output_type}")
    print("=" * 60)
    print(f"  schema_id : {result.schema_id}")
    print(f"  is_valid   : {'✓ PASS' if result.is_valid else '✗ FAIL'}")
    if result.errors:
        print(f"\n  Errors ({len(result.errors)}):")
        for e in result.errors:
            print(f"    ✗ {e}")
    if result.warnings:
        print(f"\n  Warnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"    ⚠ {w}")
    if result.fixes_suggested:
        print(f"\n  Suggested fixes:")
        for f in result.fixes_suggested:
            print(f"    → {f}")
    print()
    return 0 if result.is_valid else 1


def cmd_sandbox_run(args) -> int:
    """在沙箱里执行命令。三级降级：E2B → 本地 subprocess 隔离 → 拒绝破坏性命令。
    AI 想跑代码时应优先用此命令，而不是直接调用 Bash。
    """
    from . import sandbox as _sb
    _sr.refresh_resources_root()
    cwd = Path(args.cwd).resolve() if args.cwd else None
    result = _sb.run_in_sandbox(args.command, cwd=cwd, timeout=args.timeout)
    print("=" * 60)
    print(f"ai-rule sandbox-run: {result.sandbox_used}")
    print("=" * 60)
    if result.denied_reason:
        print(f"  🚫 DENIED: {result.denied_reason}")
        return 1
    print(f"  exit_code  : {result.exit_code}")
    print(f"  duration   : {result.duration_ms}ms")
    if result.stdout:
        print(f"\n  stdout:")
        for line in result.stdout.splitlines()[:50]:
            print(f"    {line}")
        if len(result.stdout.splitlines()) > 50:
            print(f"    ... ({len(result.stdout.splitlines()) - 50} more lines)")
    if result.stderr:
        print(f"\n  stderr:")
        for line in result.stderr.splitlines()[:30]:
            print(f"    {line}")
    return 0 if result.exit_code == 0 else result.exit_code


def cmd_judge(args) -> int:
    """LLM-as-judge 语义合规检查。
    用 LLM 实时审查 agent 输出，违规即拒绝。
    降级策略：DeepEval → OpenAI → Anthropic → 跳过
    """
    from . import llm_judge as _lj
    _sr.refresh_resources_root()
    content = args.content
    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
    rules = [r.strip() for r in args.rules.split(",") if r.strip()]

    result = _lj.judge_output(content, rules, user_language=args.language)
    print("=" * 60)
    print(f"ai-rule judge: {result.backend_used}")
    print("=" * 60)
    print(f"  is_compliant    : {'✓ PASS' if result.is_compliant else '✗ FAIL'}")
    if result.violated_rules:
        print(f"\n  Violated rules ({len(result.violated_rules)}):")
        for r in result.violated_rules:
            print(f"    ✗ {r}")
    if result.reasoning:
        print(f"\n  Reasoning: {result.reasoning}")
    if result.severity:
        print(f"  Severity : {result.severity}")
    if result.suggested_fix:
        print(f"\n  Suggested fix: {result.suggested_fix}")
    print()
    return 0 if result.is_compliant else 1


def main():
    parser = argparse.ArgumentParser(
        prog="ai-rule",
        description="Rule Hub CLI — 装配 AI 协作规则（skeleton + 按需加载）",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="列出可用 profile 和 tool")
    p_list.set_defaults(func=cmd_list)

    p_setup = sub.add_parser("setup", help="零配置默认链路：自动检测 profile + tool + emit-constraints")
    p_setup.add_argument("--intent", default="",
                         help="用户口语化意图（如 '帮我写代码' / '写小说'），用于自动识别 profile")
    p_setup.add_argument("--output", default=None,
                         help="生成产物输出目录（默认当前工作目录）")
    p_setup.set_defaults(func=cmd_setup)

    p_apply = sub.add_parser("apply", help="生成指定 profile+tool 的规则文件")
    p_apply.add_argument("--profile", required=True, help="主 profile (如 coding/novel/paper...)")
    p_apply.add_argument("--tool", required=True,
                         help="目标工具 (claude-code/gemini/cursor/trae/agents-md/all/...)")
    p_apply.add_argument("--mode", default="skeleton", choices=["skeleton", "full"],
                         help="装配模式（默认 skeleton）")
    p_apply.add_argument("--output", default=None,
                         help="生成产物输出目录（默认当前工作目录）")
    p_apply.add_argument("--emit-constraints", action="store_true", default=False,
                         help="同时分发 hook 适配器配置（仅支持 PreToolUse 的 6 个平台有效；"
                              "其他平台静默跳过）")
    p_apply.set_defaults(func=cmd_apply)

    p_verify = sub.add_parser("verify", help="CI 用：硬断言验证 skeleton 模式产物达标")
    p_verify.add_argument("--profile", default=None,
                          help="只验证指定 profile（默认全部）")
    p_verify.set_defaults(func=cmd_verify)

    p_check = sub.add_parser("check-output", help="AI 交付前自检：按 profile + output_type 校验输出 schema")
    p_check.add_argument("--profile", required=True, help="主 profile (coding/novel/paper/...)")
    p_check.add_argument("--output-type", required=True,
                         help="输出类型 (code_change/paper_outline/novel_chapter/conversation_response/agent_design)")
    p_check.add_argument("--content", default="",
                         help="待校验内容（与 --content 二选一）")
    p_check.add_argument("--file", default=None,
                         help="从文件读取待校验内容（与 --content 二选一）")
    p_check.set_defaults(func=cmd_check_output)

    p_sandbox = sub.add_parser("sandbox-run", help="在沙箱里执行命令（三级降级：E2B→本地→拒绝）")
    p_sandbox.add_argument("--command", required=True, help="要执行的命令")
    p_sandbox.add_argument("--cwd", default=None, help="工作目录（默认当前目录）")
    p_sandbox.add_argument("--timeout", type=int, default=60, help="超时秒数（默认 60）")
    p_sandbox.set_defaults(func=cmd_sandbox_run)

    p_judge = sub.add_parser("judge", help="LLM-as-judge 语义合规检查")
    p_judge.add_argument("--content", default="", help="待检查内容（与 --file 二选一）")
    p_judge.add_argument("--file", default=None, help="从文件读取内容（与 --content 二选一）")
    p_judge.add_argument("--rules", required=True,
                         help="规则列表（逗号分隔），如 no_pii_in_commit,language_match_user")
    p_judge.add_argument("--language", default="", help="用户语言提示（如 '中文'/'English'）")
    p_judge.set_defaults(func=cmd_judge)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
