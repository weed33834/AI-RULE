# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/)，版本号参考语义化版本。

## [2.4.1] — 2026-08-05

### 新增

- **MCP Server** `src/agentseed/mcp_server.py`：通过 `agentseed serve` 启动，暴露治理引擎和画像管理能力为 MCP 工具。
- **4 个 MCP 工具**：
  - `governance_check`：检查工具调用是否违反 core/constraints.yaml 中的 P0 安全红线
  - `persona_list`：列出 personas/ 目录下所有可用画像包
  - `persona_activate`：切换到指定画像并返回配置摘要
  - `gap_detect`：基于 core/self-evolution.md 的 GapScore 公式分析上下文能力缺口
- **CLI 新命令** `agentseed serve`：支持 stdio 模式（默认）和 HTTP/SSE 模式（--port）。

### 变更

- 安装方式从 PyPI 切换到 GitHub Releases（README.md / README.zh.md）

## [2.3.0] — 2026-08-04

### 新增

- **画像路由引擎** `src/agentseed/router.py`：实现 `core/persona-router.md` 全部路由逻辑——显式指定 > 目录锚点 > 意图关键词 > fallback；互斥检查（novel ↔ interactive-novel ↔ paper）；能力包白名单；Agent 模式路由（默认模式/推理深度）。
- **Persona 市场** `src/agentseed/market.py`：`agentseed persona search / install`；安装走 Quality Gate 三关（安全/质量/兼容）；P0 约束（MCP 不自安装、外部内容不可信）。
- **CLI 新命令**：`agentseed forge`（一键装配：检测环境 → 路由画像 → 生成平台文件，支持 `--dry-run` / `--intent`）、`agentseed switch`（切换画像含互斥检查）、`agentseed persona list/search/install`、`agentseed status`（装配状态）、`agentseed sync`（同步到平台）。
- **forge 引擎对接 sync_rules**：装配链路真正落地——`forge()` 调用 `build_ruleset` + `write_tool_file` 生成真实平台文件，并集成 GapScore 缺口分析。

### 变更

- `docs/AGENTSEED_ARCHITECTURE.md`：§4.4 结构图与 §5 映射表同步实际仓库结构（`persona.yaml`、`capabilities/<cap>/`、`research/dar/`、src 包文件清单）；§4.2 CLI 命令表对齐实现。
- `CONTRIBUTING.md`：更新为 v2 工作流（规则源文件编辑、`agentseed sync`、画像开发指南）。

## [2.0.0] — 2026-08-03

### 变更

- **品牌重塑**：`AI-RULE`（Rule Hub）→ **AgentSeed**。包名 `ai-rule` → `agentseed`，CLI 入口 `agentseed`。
- **目录重构**：
  - `ai_rule/` → `src/agentseed/`
  - `profiles/` → `personas/`
  - `manifests/*.yaml` → `personas/<id>/persona.yaml`
  - `personas/<id>/docs/prompts/` → `prompts/`（扁平化）
  - `personas/<id>/docs/skills/` → `skills/`（扁平化）
  - `capabilities/*.md` → `capabilities/<cap>/`（cap.yaml + prompt.md + mcp.json）
  - `core/profile-router.md` → `core/persona-router.md`
  - 删除顶层 `skills/`、`mcp/`、`README.ja.md`
- **资源根环境变量**：`AI_RULE_REPO` → `AGENTSEED_REPO`；缓存路径 `~/.cache/agentseed/`；clone 回退 URL 指向 `github.com/weed33834/agentseed.git`。

### 新增

- **自进化引擎** `src/agentseed/evolution.py` + `core/self-evolution.md`：GapScore 加权公式（0.35/0.25/0.20/0.10/0.10）、阈值决策树（0.30/0.55/0.75）、Action Decision Matrix、Quality Gate 三关骨架、置信度加权模型。
- **装配引擎** `src/agentseed/forge.py`：环境检测（锚点/平台）+ CapabilityCheck + GapScore 分析。
- **画像脚手架** `personas/_template/default/`：AGENTS.md / persona.yaml / prompts/system-prompt.md / skills/.gitkeep / SOUL.md。

### 修复

- 全部 107+ 处旧品牌/旧路径残留（`ai_rule` / `ai-rule` / `AI-RULE` / `Rule Hub` / `profile-router` / `manifests`）清理至零残留。
- `setup.py` 语法错误（空逗号）；MANIFEST.in 引用不存在的目录/README；`scripts/validate_rules.py` 与测试对 `manifests/` 的路径依赖。
- 6 个 `persona.yaml` 与 6 个 `core/*.md` 的 GBK 乱码全部修复为 UTF-8。

### 测试

- 69 passed, 1 skipped，零回归。

## [1.4.0] — 2026-07-25

### 新增

- **Runtime Skills（运行时技能）**：`skills/` 目录下 7 个可在 Main Agent 侧按需加载的专业技能。
  - `git-sop.md`：Git 标准操作流程——提交前检查、粒度控制、Conventional Commits。
  - `workflow-five-roles.md`：五子角色工作流——Architect → Engineer → Critic → Verifier → Final。
  - `skill-acquisition.md`：技能获取五层协议——标准库 → 包管理器 → 本地注册表 → 官方仓库 → 受限搜索。
  - `deep-search-first.md`：深度搜索优先——先联网确认再编码，不凭训练数据硬扛。
  - `frontend-design.md`：前端设计——先参考优秀开源仓库/设计系统再落地，不凭空生成 UI。
  - `backend-scaffold.md`：后端脚手架——项目结构、技术选型、API 设计。
  - `fullstack-deploy.md`：全栈部署——CI/CD、Docker、环境变量、监控。
- **MCP 工具**：`mcp/` 目录下 4 个 Python 工具。
  - `validate_codebase.py`：代码库结构验证。
  - `review_code.py`：代码审查。
  - `git_precommit_check.py`：提交前自动检查。
  - `generate_tests.py`：测试生成。
- **规则注入脚本**：`scripts/inject_rules.py`——按 Profile+Mode 装配规则，将 runtime skills 注入 Agent 上下文。
- **规则注入指南**：`scripts/rule_injection_guide.md`——Main Agent 派发前注入规则的操作说明。
- **BOOTSTRAP 自检**：`scripts/sync_rules.py` 新增 BOOTSTRAP 自检加载块，防止在未初始化环境中运行。
- **Agent 可执行指令段**：`core/attention-budget.md` 新增 ABA 压缩 / RT 推理控制 / 模式切换指令，支持运行时直接消费。
- **DAR 修复**：`core/mode-overrides.yaml` 新增 DAR 默认禁用但 coding/paper/conversation 按模式启用的配置。

### 变更

- `personas/coding/persona.yaml`：新增 `runtime_skills` 与 `rule_injection` 段。
- `README.md` / `README.zh.md` / `README.ja.md`：徽章数 260+→380+；结构树补全 `skills/` / `mcp/` / `agent-modes.md` / `mode-overrides.yaml` / `inject_rules.py`；新增 Runtime Skills 章节。
- `PROJECT.md`：文件速查表更新。
- `CONTRIBUTING.md`：修正多语言 README 文件名引用（`README_CN.md`→`README.zh.md`、`README_JA.md`→`README.ja.md`）；新增 Runtime Skills 与 MCP 工具章节。

### 修复

- **AGENTS.md 异常**：此前被错误生成为 paper profile 且内容从 33k 字缩至 3k，已恢复至 agent-builder profile。
- **形同虚设项全部落地**：6 Profile 运行时此前 0 开发专用 Skill/MCP，现已补全并在 manifests 中注册。
- **coding Profile 3 弱点修复**：ABA/RT 未落地、mode-overrides 未测试、规则未加载问题均已解决。

### 测试

- **6 Profile 全量测试**：coding 20 轮 + 其余 5 个各 5~10 轮，通过率 100%。
- **validate_rules.py**：6 Profile 全部通过（0 BLOCKER, 0 WARNING, 0 INFO）。
- **inject_rules.py 验证**：按 Profile 装配规则，输出 P0=5 / P1=5 / P2=5。

## [1.3.1] — 2026-07-19

### 新增

- **DAR 多模型实测评估**：10 个模型 × 6 场景（120 次 API 调用）的全覆盖测试，客观对比基准（无 DAR）vs 增强（含 DAR 提示词）。
  - `tests/dar-evaluation/multi-model-report.md`：完整评估报告——模型可用性、逐场景得分对比、六维度分析、关键发现、优化建议。
  - `tests/dar-evaluation/full-test-results.json`：60 条测试结果原始数据（含每次 API 调用的完整响应、评分、耗时）。
  - `tests/dar-evaluation/test-scenarios.md`：6 个测试场景题目清单 + DAR 增强提示词 + 6 维评分标准。
  - `tests/dar-evaluation/dar_test_runner.py`、`dar_test3.py`：测试执行脚本。
  - `tests/dar-evaluation/logs/`：3 个阶段的详细运行日志（phase1/2/3）。
  - 覆盖多语种（English/中文/日本語）、全领域（coding/conversation/paper/novel/agent-builder）。

### 变更

- `README.md`、`README_CN.md`：新增「DAR Multi-Model Evaluation Results」章节，含 Mermaid 图表（基准 vs 增强对比、六维度影响）、热力图、核心发现、优化路线。

## [1.3.0] — 2026-07-19

### 新增

- **DAR（Domain Authority Registry，域权威注册表）**：新增模块化注册表体系，为每个领域预置权威源名录、打分规则、检索通道和领域知识，让搜索行为更有指向性，避免无意义的全网乱搜。
  - `core/dar-spec.md`：DAR 统一规范——T1-T4 四档分级、打分公式（α×相关性 + β×可信度 + γ×时效 + δ×共识）、时效表、路由规则、冲突策略、动态调整机制。
  - `capabilities/dar/`：6 个领域配置（paper/coding/conversation/novel/interactive-novel/agent-builder），每个包含 source_registry、scoring_weights、freshness_table、routing_rules、domain_knowledge、conflict_policy。
  - **paper 顶刊名录**：Nature、Science、PNAS、Cell、Lancet、JAMA、BMJ、IEEE TPAMI、JMLR 等顶刊 + Google Scholar、Semantic Scholar、arXiv、PubMed、DBLP、CrossRef、Retraction Watch 等索引验证工具。
  - **coding 资源平台**：Python/Node.js/Rust/Go 官方文档 + PyPI/npm/crates.io 包仓库 + CVE/NVD/Snyk 漏洞库 + AWS/Azure/GCP 云文档 + Docker/K8s/Terraform 工具文档。
  - **统一来源分级**：将此前 A-E 五档（conversation）统一为 DAR T1-T4 四档，跨领域可比。
- **DAR 评估框架**：`tests/dar-evaluation/` 包含 5 个复杂企业级测试场景（每个 ≥200 字，覆盖多节点联动）和 6 维评估框架（Source Quality / Citation Fidelity / Routing Accuracy / Conflict Handling / Freshness Awareness / Domain Knowledge）。
- **DAR 测试**：`tests/test_dar.py`，11 项结构验证测试。

### 变更

- `core/persona-router.md`：能力包白名单所有 Profile 加入 `dar`。
- `deep-search.md`：查询设计阶段加入 DAR 路由规则引用；结果分析阶段加入 DAR 打分公式引用。
- `truth-protocol.md`：CoV 验证流程加入 DAR T1-T4 分级引用。
- `source-credibility.md`：来源分级从 A-E 五档统一为 DAR T1-T4 四档。
- 6 个 manifest：`enables_capabilities` 加入 `dar`。

## [1.2.0] — 2026-07-18

### 新增

- **paper Profile（学术论文写作）**：新增第 6 个 Profile，专门用于学术论文写作。包含 22 个文件（1 AGENTS.md + 1 INIT-PROMPT + 4 prompts + 16 skills），覆盖学术诚信协议、引用验证流程、文献综述方法论、论文结构框架（IMRaD/Review/Position/Case Study）、研究问题提炼、方法论设计、数据呈现、去AI学术味、模拟同行评审、修订信回复。
- **默认工具源配置**：所有 6 个 Profile 统一默认工具源——浏览器 Bing（所有 Profile 默认）、coding（PyPI/npm/GitHub/Stack Overflow/MDN）、conversation（Google/Wikipedia/Snopes/Statista）、novel（Merriam-Webster/Etymonline/Behind the Name/Zdic）、interactive-novel（Game Designing/Unity Docs/Unreal Docs）、agent-builder（Hugging Face/Papers with Code/LangChain/MCP Registry）、paper（Google Scholar/Semantic Scholar/arXiv/PubMed/DBLP/Zotero/CrossRef/Retraction Watch）。
- **深度搜索协议**：所有 6 个 Profile 默认启用深度搜索协议——查询 → 多源搜索 → 交叉验证（2+ 独立来源）→ 综合。用于事实支持、数据验证和领域特定查找。
- **CITATION.cff**：学术引用文件，GitHub 自动显示"Cite this repository"按钮。
- **GitHub Discussions**：已启用，Q&A 与 Issue 分离。
- **Star History + Back to Top**：三个语言版本 README 末尾添加。

### 变更

- `core/persona-router.md`：主 Profile 表加入 paper；互斥表更新；锚点加入 `manuscript/` 和 `references.bib`；关键词加入论文/文献/引用/投稿/审稿。
- `personas/coding/persona.yaml`、`conversation.yaml`、`novel.yaml`、`interactive-novel.yaml`：互斥列表加入 paper。
- 3 个 README：Profile 数 5→6；文件数 209→234；徽章更新。
- `SECURITY.md`：漏洞披露联系方式改为"在仓库提 issue 向维护者索取"。
- `tests/conftest.py`：新增 session-scope fixture，测试结束后自动用 coding profile 恢复所有生成文件。

## [1.1.0] — 2026-07-17

### 新增

- **指令预算 (Instruction Budget)**：`core/governance.md` 新增指令预算章节，基于 ManyIFEval (ICLR 2025) 研究限制同时激活的规则数量（P0 ≤5，总计 ≤12）。
- **位置效应 (Position Effects)**：`context-engineering.md` 新增 Lost in the Middle 现象说明与双端放置策略。
- **反模式库 (Anti-Patterns)**：新增 `anti-patterns.md`，收录 5 种已过时的提示词技术（全大写、纯否定、手动 CoT 等）及迁移清单。
- **扩展思考 (Extended Thinking)**：`prompt-patterns.md` 新增模式 8，指导使用模型原生推理预算替代手动 CoT。
- **三层行为边界**：`safety-guardrails.md` 行为边界声明重构为 Allowed / Confirmation Required / Forbidden 三层结构。
- **GUID 分隔符注入防御**：`safety-guardrails.md` 输入标记层新增随机 GUID 分隔符方案，防止标记闭合逃逸攻击。
- **NeMo 自检模板**：`safety-guardrails.md` 新增 `self_check_input` 和 `self_check_output` 配置模板。
- **弃权协议 (Abstention Protocol)**：`truth-protocol.md` 新增弃权协议章节，允许说"我不知道"并防止虚张声势。
- **自我精炼 (Self-Refinement)**：新增 `self-refinement.md`，涵盖 Reflexion 循环、Constitutional 自我批评、轻量级自检流程。
- **规则理由 (Rationale)**：`governance.md` 全部 P0 规则补充 Rationale（存在理由）说明。

### 变更

- 所有 5 套系统提示词统一添加语言中介协议（输入端 + 输出端），实现自动语言检测、英语推理、用户语言输出。
- `coding` 系统提示词移除硬编码中文，统一为通用语言中介协议。
- `safety-guardrails.md` YAML 模板 `input_marking` 新增 `guid_delimiter` 配置项。
- 负面指令重构：将"严禁/绝不"纯否定式约束改为正向表达 + 条件逻辑。

### 修复

- README.md 从中文改为英文（GitHub 国际化），添加 shields.io 徽章与语言切换链接。
- README_JA.md 从旧版（仅 coding）重写为完整 5-profile 结构。
- README_CN.md 添加徽章与研究驱动优化章节。
- `agent-builder` manifest 补全 `anti-patterns.md` 和 `self-refinement.md` 引用。
- `agent-builder` AGENTS.md 补全反模式与自我精炼的技能引用。

### 测试

- 5 套测试套件，40 项检查，全部通过。

## [1.0.0] — 2026-07-16

- 初始版本：5 套 Profile 合并发布（coding / conversation / novel / interactive-novel / agent-builder）。
