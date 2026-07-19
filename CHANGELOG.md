# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/)，版本号参考语义化版本。

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

- `core/profile-router.md`：能力包白名单所有 Profile 加入 `dar`。
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

- `core/profile-router.md`：主 Profile 表加入 paper；互斥表更新；锚点加入 `manuscript/` 和 `references.bib`；关键词加入论文/文献/引用/投稿/审稿。
- `manifests/coding.yaml`、`conversation.yaml`、`novel.yaml`、`interactive-novel.yaml`：互斥列表加入 paper。
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
