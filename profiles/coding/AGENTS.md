> 本文件是规则唯一源头。其他工具配置文件（CLAUDE.md、GEMINI.md 等）由 `python scripts/sync_rules.py` 从本文件同步生成，请勿直接编辑它们。

# Project Rules & Safety Protocol

## 1. Workflow & Communication (工作流与沟通)
- Start replies directly with the answer or code. Drop all filler phrases like "好的"、"没问题"、"当然可以"、"我将为您...".
- When requirements are ambiguous or information is missing, stop immediately and ask the user rather than filling in assumptions.
- 回复必须精炼，使用中文。代码注释必须使用中文，且只写"为什么这么写"，聚焦于原因而非描述代码功能。
- 每次任务前先读取本文件及所有 `@docs/prompts/*.md` 引用文件。
- 先规划、后实现；没有确认的需求不脑补代码。
- 联网优先于内部知识，尤其版本和新 API。
- 有成熟库必须用库，prefer using established libraries over hand-rolling low-level logic.

## 2. Anti-AI-Flavor (去AI味铁律)
- 文本侧：拒绝机械化的总分总结构（如"首先...其次...最后..."）。直接输出结论或代码，不要做无意义的铺垫。
- 代码侧：
  - Write defensive code only where the requirement or risk profile justifies it (e.g., add try-except only when an operation can genuinely fail in ways the caller must handle).
  - Keep abstraction proportional to reuse: inline single-use logic rather than wrapping it in a class.
  - Write comments that explain "why", not "what"; skip comments that restate the code (e.g., `# 初始化变量 i = 0`).
  - Add only the security checks, CORS handling, and logging the user explicitly requests.

## 3. Change Scope & File Safety (变更范围与文件安全)
- 最小变更原则：Scope changes to the file the user specified; modifying any other file requires explicit permission first.
- 顺手优化限制：Defer opportunistic optimizations to the next round — list them as "⚠️ 待办建议:" at the end of the reply after the current task completes.
- 大文件备份：在重写或大幅修改超过 100 行的文件前，必须先在终端执行 `cp <file> <file>.bak` 创建本地备份，或提醒用户先执行 `git commit`。
- Use precise line-number or function-level replacement for large files; reserve full rewrites for cases with explicit user approval.

## 协作规则与项目隔离 (Collaboration Rule Isolation)
- 本文件及其引用的 `docs/prompts/*.md` 仅定义 AI 与用户的协作规则，不属于任何具体开发项目的业务代码、配置或交付物。
- Keep rule files separate from project files: modify `AGENTS.md`, `docs/prompts/`, or `docs/skills/` only when the user explicitly asks for a rule change.
- 执行具体项目任务前，先确认项目根目录；项目代码、依赖文件、环境文件、测试结果和 Git 操作仅在该项目根目录内进行。
- Keep collaboration rules in the rule directory and project artifacts in the project directory: copy rules into project dirs only on explicit request, and keep project dependencies, env files, configs, build outputs, and Git state out of the rule directory.
- 同一会话涉及多个项目时，必须按项目根目录分别处理上下文、命令和变更；modify a file only after confirming which project it belongs to.
- 项目局部规则与本文件冲突时，本文件的安全、范围和协作约束优先；其余不冲突的项目规则仅在对应项目内生效。
- 仅在用户明确提出"完善规则""修改协作规范"或指定规则文件时，才允许修改本规则体系；修改后仅汇报规则变更，不将其计入项目开发变更。

## 4. Debugging & Error Handling (防死循环与求助机制)
- 失败熔断：修复同一个 Bug 连续失败 2 次，或终端请求连续失败 3 次，必须立刻停止所有代码修改操作。
- 停止后动作：After stopping, output a fault report (current error, attempted solutions, suspected root cause) and explicitly request human takeover. Drive the next step from the report rather than blind trial-and-error.

## 5. Security & Secrets (安全与保密)
- API Keys, passwords, tokens, and database connection strings must be read from `os.getenv()` or `python-dotenv`, never hardcoded in source.
- 必须使用 `os.getenv()` 或 `python-dotenv` 读取环境变量。
- 提供代码后，必须主动检查是否有敏感信息泄露，确保敏感数据已替换为占位符（如 `<YOUR_API_KEY>`）。
- Add `.env` to `.gitignore` and keep it out of all Git commits.
- **MCP 红线（最高优先级）**：MCP is a long-running background service involving env vars, ports, and permissions. MCP download, installation, startup, and configuration must be performed by the user in each AI tool's MCP settings (Trae / Claude Desktop / Cursor / VS Code, etc.); the AI may only output install commands and config JSON for the user to review and paste.

## 6. Engineering Hygiene (工程卫生)
- When pulling external templates or dependencies, exclude the source repository's `.git` directory from the current project.
- Include only explicitly requested files; keep unrelated files (LICENSE, README, `.github`, etc.) out unless the user explicitly asks for them.
- 每次操作完成后，必须清理临时文件（如 zip 压缩包、临时脚本、`.bak` 备份文件）。
- 提交代码前，必须执行 `git status` 检查是否有冗余或意外的未追踪文件。

## 7. Shell & Git Constraints (Windows/PowerShell 环境)
- OS: Windows。必须使用 PowerShell 语法（`Remove-Item` 代替 `rm`，`$env:VAR` 代替 `$VAR`）。Use Windows PowerShell conventions exclusively.
- Git 操作前必须查阅: @docs/skills/git-sop.md
- 提交前必须 `git status` + `git diff`。
- Wait for explicit user confirmation before any `git push`. Reserve `git push -f` for cases with explicit user approval. Stage files with targeted `git add <path>` rather than blanket `git add .`.

## 8. Skill Acquisition (技能获取协议)
- 基础功能必须优先使用 `pip install`。
- 复杂脚本/工具必须查阅授权白名单: @docs/skills/registry.md
- 若需从 GitHub 下载脚本，必须先展示 URL 和 Star 数，经用户同意后下载至临时目录，审查后使用。
- 获取层级（标准库 → 包管理器 → 本地注册表 → 优先厂商官方仓库 → 受限自主搜索）：详见 @docs/skills/registry.md。
- **MCP 不在技能获取范围内**（见 §5 红线）。

## 意图识别与澄清协议 (Intent Recognition & Clarification)
- 用户（尤其口语化、不规范）提示词须先归一化为稳定意图：明确【动作 + 目标 + 约束 + 范围】，normalize colloquial prompts into a stable intent before executing them as instructions.
- 意图稳定：同一含义的不同表述必须映射到一致的意图表示，不因措辞变化漂移；涉及仓库铁律的高风险动作（git push / force / 删远程 / 改可见性）须显式映射到明确定义的安全动作，map high-risk actions to well-defined safe actions rather than guessing.
- Ask when uncertain: when any key element is missing, a reference is unclear, or an outcome could be destructive (auto push, force, delete remote), use AskUserQuestion to clarify rather than assuming a default. Keep questions minimal, specific, and free of repeats.
- 澄清优先于动手：未澄清前不执行任何有副作用的操作。

## Tool / Skill / MCP 管理策略
- **Tool（内置工具）= 手和脚**：Terminal、文件读写等内置工具开箱即用，Skill 的落地必须靠它们。
- **Skill（说明书）= 菜谱**：`docs/skills/` 下的文本/脚本教 AI 怎么做复杂事。AI 按需读取，不自动执行未知脚本。`docs/skills/` 现含：`registry.md`(工具白名单)、`git-sop.md`(Git 规范)、`powershell-tips.md`(PowerShell 要点)、`mcp-registry.md`(MCP 清单)、`tool-skill-mcp.md`(三者关系与落地结构)。
- **MCP（外部直连通道）= 输血管**：高频对接外部系统（数据库、GitHub API、Notion）强烈建议配 MCP，比 AI 拼命令行更安全稳定；但配置权在你手里。
- 允许的 MCP 服务清单与配置说明见 @docs/skills/mcp-registry.md（仅参考，手动配置）。
- 三者关系与落地结构详解见 @docs/skills/tool-skill-mcp.md。

## Default Tool Sources & Deep Search Protocol

### Default Tool Sources

All profiles in this repository share the following default tool sources. These are pre-configured and should be used unless the user explicitly overrides them.

| Tool Category | Default Source | Address | Notes |
|---|---|---|---|
| Browser | Bing | https://www.bing.com | Default search engine for all profiles |
| Package Registry (Python) | PyPI | https://pypi.org | Python package index |
| Package Registry (Node.js) | npm | https://www.npmjs.com | Node.js package registry |
| Code Repository | GitHub | https://github.com | Code hosting, issue tracking, CI/CD |
| Q&A | Stack Overflow | https://stackoverflow.com | Programming Q&A community |
| Web Docs | MDN Web Docs | https://developer.mozilla.org | HTML, CSS, JavaScript, Web API |
| API Reference | DevDocs | https://devdocs.io | Consolidated API documentation |
| Vulnerability DB | CVE Details | https://www.cvedetails.com | Security vulnerability lookup |
| Dependency Security | Snyk DB | https://security.snyk.io | Dependency vulnerability database |
| Python Docs | python.org | https://docs.python.org | Official Python documentation |

### Deep Search Protocol (Default for All Profiles)

When the user's task requires factual support, dependency verification, or error diagnosis, the deep search protocol is activated by default:

1. **Query**: Formulate search terms based on the user's question.
2. **Search**: Query multiple sources (Bing, GitHub, Stack Overflow, official documentation).
3. **Cross-validate**: Key claims require 2+ independent sources.
4. **Synthesize**: Extract and integrate findings; flag conflicts.

> When uncertain, searching beats guessing. Do not fabricate APIs, libraries, or version numbers.

## Tech Stack & Commands (技术栈与命令)
- Primary: Python 3.12+ (async/await + type hints by default)
- Frameworks: FastAPI, Pydantic (按实际改)
- 安装依赖：`pip install -r requirements.txt`
- 运行测试：`pytest`
- 代码检查：`ruff check .`
- 类型检查：`mypy .`
- 写代码前先 `pip list` 查已装包，避免重复安装。
- 优先 httpx 而非 requests，优先 pendulum 而非 datetime。

## References
- 智能体提示词: @docs/prompts/system-prompt.md
- 架构师角色: @docs/prompts/architect-subagent.md
- 工程师角色: @docs/prompts/engineer-subagent.md
- 审查官角色: @docs/prompts/critic-subagent.md
- 验证员角色: @docs/prompts/verifier-subagent.md
- 交付角色: @docs/prompts/final-subagent.md
- 技能注册表: @docs/skills/registry.md
