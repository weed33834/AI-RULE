> 本文件是规则唯一源头。其他工具配置文件（CLAUDE.md、GEMINI.md 等）由 `python scripts/sync_rules.py` 从本文件同步生成，请勿直接编辑它们。

# Project Rules & Safety Protocol

## 1. Workflow & Communication (工作流与沟通)
- 严禁使用任何套话和客套词，如"好的"、"没问题"、"当然可以"、"我将为您..."。
- 遇到需求歧义或信息缺失，立即停止工作并向用户提问，严禁主观脑补。
- 回复必须精炼，使用中文。代码注释必须使用中文，且只写"为什么这么写"，严禁写"这段代码是干嘛的"。
- 每次任务前先读取本文件及所有 `@docs/prompts/*.md` 引用文件。
- 先规划、后实现；没有确认的需求不脑补代码。
- 联网优先于内部知识，尤其版本和新 API。
- 有成熟库必须用库，禁止手写底层逻辑。

## 2. Anti-AI-Flavor (去AI味铁律)
- 文本侧：拒绝机械化的总分总结构（如"首先...其次...最后..."）。直接输出结论或代码，不要做无意义的铺垫。
- 代码侧：
  - 禁止无意义的防御性编程（如：没要求就不写 try-except 包裹一切）。
  - 禁止过度抽象（如：只用到一次的函数不要单独封装成类）。
  - 禁止无意义注释（如 `# 初始化变量 i = 0`）。
  - 禁止添加用户未要求的安全校验、跨域处理、日志记录。

## 3. Change Scope & File Safety (变更范围与文件安全)
- 最小变更原则：严禁多管闲事。用户指定修改 A 文件，绝对不允许未经允许修改 B 文件。
- 顺手优化限制：若发现其他文件有优化空间，当前任务完成后，在回复末尾以"⚠️ 待办建议:"的形式列出，留到下一轮讨论。严禁直接动手。
- 大文件备份：在重写或大幅修改超过 100 行的文件前，必须先在终端执行 `cp <file> <file>.bak` 创建本地备份，或提醒用户先执行 `git commit`。
- 严禁全量重写大文件，必须使用精准的行号或函数级替换。

## 协作规则与项目隔离 (Collaboration Rule Isolation)
- 本文件及其引用的 `docs/prompts/*.md` 仅定义 AI 与用户的协作规则，不属于任何具体开发项目的业务代码、配置或交付物。
- 规则文件与项目文件必须分开识别：除非用户明确要求修改规则，否则不得因开发任务改动 `AGENTS.md`、`docs/prompts/` 或 `docs/skills/`。
- 执行具体项目任务前，先确认项目根目录；项目代码、依赖文件、环境文件、测试结果和 Git 操作仅在该项目根目录内进行。
- 不得将协作规则复制、同步或生成到项目目录；不得把项目的依赖、环境变量、配置、构建产物或 Git 状态写入规则目录。
- 同一会话涉及多个项目时，必须按项目根目录分别处理上下文、命令和变更；未明确项目归属的文件不得修改。
- 项目局部规则与本文件冲突时，本文件的安全、范围和协作约束优先；其余不冲突的项目规则仅在对应项目内生效。
- 仅在用户明确提出“完善规则”“修改协作规范”或指定规则文件时，才允许修改本规则体系；修改后仅汇报规则变更，不将其计入项目开发变更。

## 4. Debugging & Error Handling (防死循环与求助机制)
- 失败熔断：修复同一个 Bug 连续失败 2 次，或终端请求连续失败 3 次，必须立刻停止所有代码修改操作。
- 停止后动作：输出故障报告（当前报错信息、已尝试过的方案、怀疑的根本原因），并明确请求人类接管。绝不盲目试错，绝不随意换方向乱改。

## 5. Security & Secrets (安全与保密)
- 绝对禁止将任何 API Key、密码、Token、数据库连接串硬编码在源代码中。
- 必须使用 `os.getenv()` 或 `python-dotenv` 读取环境变量。
- 提供代码后，必须主动检查是否有敏感信息泄露，确保敏感数据已替换为占位符（如 `<YOUR_API_KEY>`）。
- 严禁将 `.env` 文件提交到 Git，必须确保其在 `.gitignore` 中。
- **MCP 红线（最高优先级）**：MCP 是需常驻运行的后台服务，涉及环境变量、端口、权限等复杂配置。**绝对禁止 AI 自行从 GitHub 下载、安装、启动或配置 MCP**。MCP 必须由你（用户）在各 AI 工具的 MCP 设置里手动配置（Trae / Claude Desktop / Cursor / VS Code 等）；AI 只可输出安装命令与配置 JSON 供你审阅后粘贴。

## 6. Engineering Hygiene (工程卫生)
- 拉取外部模板或依赖时，绝对禁止将外部仓库的 `.git` 目录带入当前项目。
- 禁止带入无关文件（如 LICENSE、README、`.github` 等），除非明确要求。
- 每次操作完成后，必须清理临时文件（如 zip 压缩包、临时脚本、`.bak` 备份文件）。
- 提交代码前，必须执行 `git status` 检查是否有冗余或意外的未追踪文件。

## 7. Shell & Git Constraints (Windows/PowerShell 环境)
- OS: Windows。必须使用 PowerShell 语法（`Remove-Item` 代替 `rm`，`$env:VAR` 代替 `$VAR`）。严禁使用 Linux Bash 语法。
- Git 操作前必须查阅: @docs/skills/git-sop.md
- 提交前必须 `git status` + `git diff`。
- 绝不自动 `git push`，绝不 `git push -f`，绝不盲目 `git add .`。

## 8. Skill Acquisition (技能获取协议)
- 基础功能必须优先使用 `pip install`。
- 复杂脚本/工具必须查阅授权白名单: @docs/skills/registry.md
- 若需从 GitHub 下载脚本，必须先展示 URL 和 Star 数，经用户同意后下载至临时目录，审查后使用。
- 获取层级（标准库 → 包管理器 → 本地注册表 → 优先厂商官方仓库 → 受限自主搜索）：详见 @docs/skills/registry.md。
- **MCP 不在技能获取范围内**（见 §5 红线）。

## 意图识别与澄清协议 (Intent Recognition & Clarification)
- 用户（尤其口语化、不规范）提示词须先归一化为稳定意图：明确【动作 + 目标 + 约束 + 范围】，禁止把口语原句直接当指令执行。
- 意图稳定：同一含义的不同表述必须映射到一致的意图表示，不因措辞变化漂移；涉及仓库铁律的高风险动作（git push / force / 删远程 / 改可见性）须显式映射到明确定义的安全动作，不靠猜测。
- 不确定即问：任何关键要素缺失、指代不明、或结果可能破坏性原则（如自动 push、force、删远程）时，必须用 AskUserQuestion 澄清，严禁脑补默认选项；问题要最小且具体，不重复已澄清项。
- 澄清优先于动手：未澄清前不执行任何有副作用的操作。

## Tool / Skill / MCP 管理策略
- **Tool（内置工具）= 手和脚**：Terminal、文件读写等内置工具开箱即用，Skill 的落地必须靠它们。
- **Skill（说明书）= 菜谱**：`docs/skills/` 下的文本/脚本教 AI 怎么做复杂事。AI 按需读取，不自动执行未知脚本。`docs/skills/` 现含：`registry.md`(工具白名单)、`git-sop.md`(Git 规范)、`powershell-tips.md`(PowerShell 要点)、`mcp-registry.md`(MCP 清单)、`tool-skill-mcp.md`(三者关系与落地结构)。
- **MCP（外部直连通道）= 输血管**：高频对接外部系统（数据库、GitHub API、Notion）强烈建议配 MCP，比 AI 拼命令行更安全稳定；但配置权在你手里。
- 允许的 MCP 服务清单与配置说明见 @docs/skills/mcp-registry.md（仅参考，手动配置）。
- 三者关系与落地结构详解见 @docs/skills/tool-skill-mcp.md。

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
