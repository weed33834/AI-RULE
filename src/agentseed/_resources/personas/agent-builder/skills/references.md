---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 用户要查 Agent 平台白名单、默认工具源、深度搜索协议、或本 Profile 全部 skill/prompt 引用清单
terminates_when: T    # 用户已找到目标引用路径或确认默认工具源
provides: π           # 平台白名单表、默认工具源表、深度搜索 4 步协议、全部 skill/prompt 引用清单
interface: R          # 输入=查询关键词；输出=引用路径 + 默认源 + 协议步骤
---

# 引用清单与默认工具源 (References & Default Tool Sources)

> 本文件是 agent-builder Profile 的引用汇总，承载原 AGENTS.md 的 References、Default Tool Sources、Deep Search Protocol 三节内容。

## 1. 子智能体与 Skill 引用清单 / Sub-agents & Skills Reference

### 子智能体 / Sub-agents
- 系统提示词 / System prompt: prompts/system-prompt.md
- 角色设计子智能体 / Role designer: prompts/role-designer.md
- 能力注入子智能体 / Skill injector: prompts/skill-injector.md
- 工具编排子智能体 / Tool orchestrator: prompts/tool-orchestrator.md
- 记忆架构子智能体 / Memory architect: prompts/memory-architect.md
- 评估测试子智能体 / Evaluator: prompts/evaluator.md
- 安全护栏子智能体 / Safety guard: prompts/safety-guard.md

### Skills（按主题分组）
- 平台白名单 / Platform registry: skills/registry.md
- 角色设计 / Role design: skills/role-design.md
- 提示词模式 / Prompt patterns: skills/prompt-patterns.md
- 推理模式 / Reasoning patterns: skills/reasoning-patterns.md
- 工具设计 / Tool design: skills/tool-design.md
- 记忆系统 / Memory systems: skills/memory-systems.md
- 知识注入 / Knowledge injection: skills/knowledge-injection.md
- 多智能体协作 / Multi-agent: skills/multi-agent.md
- 评估框架 / Evaluation framework: skills/evaluation-framework.md
- 安全护栏核心 / Safety guardrails core: skills/safety-guardrails-core.md
- LLM-as-Judge + NeMo 模板 / LLM-as-Judge & NeMo templates: skills/safety-guardrails-llm-judge.md
- 安全护栏决策树与模板 / Safety guardrails decision tree & templates: skills/safety-guardrails-templates.md
- 部署指南 / Deployment guide: skills/deployment-guide.md
- 上下文工程 / Context engineering: skills/context-engineering.md
- 对话设计 / Conversation design: skills/conversation-design.md
- 人格设计 / Persona design: skills/persona-design.md
- 演进策略 / Evolution policy: skills/evolution-policy.md
- 深度搜索 / Deep search: skills/deep-search.md
- 技能导航索引 / Skill hub: skills/skill-hub.md
- 微调决策指南 / Fine-tuning guide: skills/fine-tuning-guide.md
- 智能体测试自动化 / Agent testing automation: skills/agent-testing-automation.md
- 成本优化 / Cost optimization: skills/cost-optimization.md
- 智能体可观测性 / Agent observability: skills/agent-observability.md
- 工作流编排 / Workflow design: skills/workflow-design.md
- 模板使用指南 / Agent templates guide: skills/agent-templates-guide.md
- 智能体构造方法论 / Construction playbook: skills/construction-playbook.md
- 工业界来源图谱 / Industry source map: skills/industry-source-map.md
- 高级架构模式总览 / Advanced patterns overview: skills/advanced-patterns-overview.md
- 评估体系设计 / Evaluation system design: skills/advanced-patterns-evaluation.md
- 可观测性设计 / Observability design: skills/advanced-patterns-observability.md
- 安全对齐+高级架构 / Safety alignment + advanced architecture: skills/advanced-patterns-safety.md
- 反模式 / Anti-patterns: skills/anti-patterns.md
- 编排模式 / Orchestration patterns: skills/orchestration-patterns.md
- 自我精炼 / Self-refinement: skills/self-refinement.md

## 2. 默认工具源 / Default Tool Sources

All profiles in this repository share the following default tool sources. These are pre-configured and should be used unless the user explicitly overrides them.

| 工具类别 / Tool Category | 默认源 / Default Source | 地址 / Address | 备注 / Notes |
|---|---|---|---|
| 浏览器 / Browser | Bing | https://www.bing.com | 所有 Profile 默认搜索引擎 |
| AI 模型 / AI Models | Hugging Face | https://huggingface.co | 模型库与基准 |
| AI 论文 / AI Papers | Papers with Code | https://paperswithcode.com | ML 论文 + 代码实现 |
| 提示词库 / Prompt Library | Prompt Engineering Guide | https://www.promptingguide.ai | 提示词模式与技巧 |
| Agent 框架 / Agent Framework | LangChain Docs | https://python.langchain.com | Agent 框架文档 |
| LLM 评估 / LLM Evaluation | Open LLM Leaderboard | https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard | LLM 基准榜单 |
| ML 数据集 / ML Datasets | Hugging Face Datasets | https://huggingface.co/datasets | 数据集库 |
| 向量数据库 / Vector Database | Chroma | https://www.trychroma.com | 开源向量数据库 |
| MCP 注册表 / MCP Registry | Anthropic MCP | https://modelcontextprotocol.io | Model Context Protocol 规范 |
| Python 包 / Python Package | PyPI | https://pypi.org | Python 包索引 |

## 3. 深度搜索协议 / Deep Search Protocol

When the user's task requires factual support (model capabilities, benchmark results, framework features), the deep search protocol is activated by default:

1. **Query / 提问**：Formulate search terms based on the user's question.
2. **Search / 检索**：Query multiple sources (Bing, Hugging Face, Papers with Code, official documentation).
3. **Cross-validate / 交叉验证**：Key claims require 2+ independent sources.
4. **Synthesize / 综合**：Extract and integrate findings; flag conflicts.

> When uncertain about a model's capability, a benchmark result, or a framework feature, search rather than guess. Do not fabricate model names, benchmark scores, or API capabilities.
