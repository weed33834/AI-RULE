# registry.md — Agent 平台白名单与选型指南
# Agent Platform Whitelist & Selection Guide

---

## 一句话描述 / One-line Description

> 本文档列出经过验证的主流 Agent 开发平台与框架，提供基于真实特性与官网信息的选型决策树，帮助团队在"低代码平台"与"代码框架"之间做出可追溯的技术决策。
>
> This document lists verified mainstream Agent development platforms and frameworks, and provides a selection decision tree based on real features and official sources, helping teams make traceable technical decisions between "low-code platforms" and "code frameworks".

---

## 适用场景 / Applicable Scenarios

- **项目立项阶段**：需要从 0 到 1 选定 Agent 技术栈，避免拍脑袋决策。
- **架构评审阶段**：需要对候选平台做横向对比，给出有依据的取舍理由。
- **技术尽调阶段**：评估某平台是否仍在维护、是否即将废弃、许可证是否合规。
- **团队技能对齐阶段**：新人入职后快速了解"我们为什么选这个平台"。

---

## 核心方法论 / Core Methodology

平台选型遵循 **三层分类法**：

1. **交付形态层**：低代码可视化平台（Dify、Coze）vs 代码框架（LangChain、LangGraph、AutoGen、CrewAI、Semantic Kernel）vs 托管 API 服务（OpenAI Assistants / Responses API）。
2. **控制粒度层**：黑盒（托管 API、低代码）→ 灰盒（框架+托管组件）→ 白盒（纯代码，完全可控）。
3. **生态与治理层**：开源协议、社区活跃度、厂商绑定风险、数据驻留要求。

> 选型不是"选最强"，而是"选最匹配团队能力与合规要求的最小可行集"。

### 平台白名单 / Platform Whitelist

以下平台均经过公开信息核实。标注"需验证"处表示截至撰稿时尚未完全确认，使用前请查阅官网。

#### 1. Dify

| 维度 | 内容 |
|------|------|
| 类型 | 开源 LLM 应用开发平台（低代码 + 可自托管） |
| 官网 | https://dify.ai |
| 文档 | https://docs.dify.ai |
| GitHub | https://github.com/langgenius/dify |
| 开源协议 | Apache-2.0（需验证具体版本条款，请以仓库 LICENSE 为准） |
| 核心特点 | 可视化 Workflow 编排、RAG 管线（知识库）、Prompt 管理、支持多种模型供应商、可自托管（Docker）以保障数据私有 |
| 适用场景 | 企业内部知识助手、需要私有化部署的 RAG 应用、非工程团队主导的 AI 应用搭建 |
| 注意事项 | 自托管需运维能力；高级功能可能与企业版绑定 |

#### 2. Coze / 扣子

| 维度 | 内容 |
|------|------|
| 类型 | 字节跳动旗下的 AI Agent 搭建平台（低代码/无代码） |
| 官网（国际版） | https://www.coze.com |
| 官网（国内版/扣子） | https://www.coze.cn |
| 文档（国际） | https://docs.coze.com |
| 文档（国内） | https://www.coze.cn/open/docs |
| 核心特点 | 可视化 Bot 搭建、插件（Plugin）市场、多渠道发布（飞书、Discord、Telegram 等）、工作流编排、知识库；国内版与飞书生态深度集成 |
| 适用场景 | 快速搭建面向 C 端或多渠道分发的 Bot、营销/客服场景、个人创作者验证想法 |
| 注意事项 | 托管在字节基础设施上，数据驻留需评估合规；国际版与国内版功能和模型支持存在差异；低代码天花板受限 |

#### 3. OpenAI Assistants API（注：即将废弃）

| 维度 | 内容 |
|------|------|
| 类型 | 托管 API 服务（有状态助手） |
| 官网 | https://platform.openai.com/docs/assistants |
| 核心特点 | 内置 Thread（对话状态管理）、内置工具（Code Interpreter、File Search、Function Calling），开发者无需自行管理对话历史 |
| **废弃状态** | **已宣布废弃（deprecated），目标停服日期为 2026 年上半年（社区信息指向 2026 年 8 月 26 日）。** 其能力正迁移至新的 Responses API |
| 替代方案 | Responses API：https://platform.openai.com/docs/api-reference/responses |
| 适用场景 | 新项目不应再基于 Assistants API；已有项目需制定迁移计划 |
| 注意事项 | 务必查阅 OpenAI 官方 deprecation 公告确认时间线，社区信息可能与官方最终公告有出入 |

#### 4. LangChain

| 维度 | 内容 |
|------|------|
| 类型 | LLM 应用开发框架（Python / JavaScript 双语言） |
| 官网 | https://www.langchain.com |
| 文档（Python） | https://python.langchain.com |
| 文档（JS） | https://js.langchain.com |
| GitHub | https://github.com/langchain-ai/langchain |
| 开源协议 | MIT |
| 核心特点 | 大量集成（模型、向量库、工具）、LCEL（LangChain Expression Language）声明式链、文档加载与切分工具链、社区生态最大 |
| 适用场景 | 需要"胶水层"快速串联多组件的 PoC 与生产应用、需要丰富第三方集成 |
| 注意事项 | 抽象层较厚，调试与升级时可能遇到兼容性问题；复杂状态管理建议直接用 LangGraph |

#### 5. LangGraph

| 维度 | 内容 |
|------|------|
| 类型 | 有状态、多角色 Agent 编排库（基于图/状态机） |
| 官网 | https://langchain-ai.github.io/langgraph/ |
| GitHub | https://github.com/langchain-ai/langgraph |
| 开源协议 | MIT |
| 核心特点 | 以"节点 + 边 + 共享状态"建模 Agent 流程，原生支持循环（cycle）、条件分支、人机协作（human-in-the-loop）、持久化检查点（checkpointing）；LangGraph Cloud / Studio 提供可视化 |
| 适用场景 | 需要精确控制 Agent 决策循环、多 Agent 协作、需要断点续跑与状态回放的生产级系统 |
| 注意事项 | 学习曲线高于普通 LangChain Chain；需要理解图论与状态管理概念 |

#### 6. AutoGen

| 维度 | 内容 |
|------|------|
| 类型 | 微软开源的多 Agent 对话框架 |
| 官网 | https://github.com/microsoft/autogen |
| 文档 | https://microsoft.github.io/autogen/ |
| 开源协议 | MIT（需验证，以仓库 LICENSE 为准） |
| 核心特点 | 以"可对话实体（Conversable Agent）"为核心抽象，支持多 Agent 对话、群聊（GroupChat）、代码执行（Code Executor）、事件驱动架构（v0.4+）；AutoGen Studio 提供无代码 UI |
| 适用场景 | 研究/实验型多 Agent 协作、需要 Agent 间自由对话与代码生成执行的场景 |
| 注意事项 | v0.2 与 v0.4 架构差异较大，迁移需注意 API 变化；微软正将其与 Semantic Kernel 整合进统一的 Agent 体系（需验证整合的最终形态） |

#### 7. CrewAI

| 维度 | 内容 |
|------|------|
| 类型 | 基于角色的多 Agent 协作框架 |
| 官网 | https://www.crewai.com |
| GitHub | https://github.com/crewAIInc/crewAI |
| 文档 | https://docs.crewai.com |
| 开源协议 | MIT（需验证，以仓库 LICENSE 为准） |
| 核心特点 | 三大核心概念——Agent（执行者，含 Role/Goal/Backstory）、Task（任务定义）、Crew（组织与编排）；支持工具、流程（Process：sequential/hierarchical）、Handoff 模式；企业版提供托管与监控 |
| 适用场景 | 内容生产流水线、研究自动化、需要"团队分工"隐喻的业务流程自动化 |
| 注意事项 | 抽象较重，Token 消耗可能较高（多角色对话）；调试链路较长 |

#### 8. Semantic Kernel

| 维度 | 内容 |
|------|------|
| 类型 | 微软开源的 AI 编排 SDK（支持 C# / Python / Java） |
| 官网 | https://github.com/microsoft/semantic-kernel |
| 文档 | https://learn.microsoft.com/semantic-kernel/ |
| 开源协议 | MIT（需验证，以仓库 LICENSE 为准） |
| 核心特点 | 以"插件（Plugin）+ 函数（Function）"为核心，原生 Function Calling 与规划（Planner）；与 .NET / Azure 生态深度集成；强调企业级可扩展性 |
| 适用场景 | .NET 技术栈团队、企业级应用集成 Azure OpenAI、需要强类型与工程化治理的场景 |
| 注意事项 | Python 生态不如 LangChain 丰富；主要面向微软技术栈 |

---

## 决策树 / Decision Tree

```
Q1: 是否需要私有化部署 / 数据不出境？
├─ 是 ──► Q2
└─ 否 ──► Q3

Q2: 团队是否有工程能力（Docker / 后端运维）？
├─ 是 ──► Dify（自托管，低代码 + 私有化）或 LangGraph / LangChain（纯代码，完全可控）
└─ 否 ──► Dify Cloud（需评估数据驻留）或 寻求企业版方案

Q3: 更偏好低代码可视化，还是代码控制？
├─ 低代码 ──► Q4
└─ 代码 ──► Q5

Q4: 面向国内还是国际，是否需要多渠道分发？
├─ 国内 + 飞书生态 ──► Coze 国内版（扣子）
├─ 国际 / 多渠道 ──► Coze 国际版
└─ 企业内部 + RAG ──► Dify

Q5: 是否需要多 Agent 协作？
├─ 是 ──► Q6
└─ 否（单 Agent / 简单链）──► Q7

Q6: 协作模式偏好？
├─ 精确状态机控制 / 循环 / 人机协作 ──► LangGraph
├─ 角色分工团队隐喻 ──► CrewAI
└─ 自由多 Agent 对话 / 研究 ──► AutoGen

Q7: 技术栈与定位？
├─ .NET / Azure 企业级 ──► Semantic Kernel
├─ 需要海量第三方集成 / 快速 PoC ──► LangChain
└─ 单助手托管（新项目）──► OpenAI Responses API（注意：Assistants API 已废弃）
```

### 选型矩阵速查 / Quick Matrix

| 平台 | 交付形态 | 控制粒度 | 多 Agent | 私有化 | 学习曲线 | 生态绑定 |
|------|----------|----------|----------|--------|----------|----------|
| Dify | 低代码 | 灰盒 | 弱 | 支持 | 低 | 中 |
| Coze | 低代码 | 黑盒 | 弱 | 不支持 | 低 | 高（字节） |
| OpenAI Responses API | 托管 API | 黑盒 | 弱 | 不支持 | 低 | 高（OpenAI） |
| LangChain | 代码框架 | 白盒 | 弱 | N/A | 中 | 低 |
| LangGraph | 代码框架 | 白盒 | 强 | N/A | 高 | 低 |
| AutoGen | 代码框架 | 白盒 | 强 | N/A | 高 | 中（微软） |
| CrewAI | 代码框架 | 灰盒 | 强 | N/A | 中 | 低 |
| Semantic Kernel | 代码 SDK | 白盒 | 中 | N/A | 中 | 中（微软） |

---

## 模板示例 / Template Example

### 平台选型记录卡 / Platform Selection Record

```markdown
## 选型决策记录 / Selection Decision Record

- 项目名称 / Project: ___________
- 日期 / Date: ___________
- 决策人 / Decision Maker: ___________

### 候选平台 / Candidates
1. ___________  — 选择理由: ___________
2. ___________  — 淘汰理由: ___________

### 关键约束 / Key Constraints
- [ ] 是否需要私有化部署: 是 / 否
- [ ] 团队技术栈: ___________
- [ ] 合规要求: ___________
- [ ] 预算限制: ___________

### 最终选择 / Final Choice
- 平台: ___________
- 官网核实日期 / Verified date: ___________
- 已查阅官方废弃公告 / Checked deprecation notice: 是 / 否

### 风险与缓解 / Risks & Mitigation
- 风险 1: ___________  → 缓解: ___________
```

---

## 常见陷阱 / Common Pitfalls

1. **忽视废弃公告**：OpenAI Assistants API 已宣布废弃，新项目若仍基于它将面临强制迁移风险。务必在选型时查阅官方 deprecation 页面。
2. **混淆国内版与国际版**：Coze 国内版（扣子）与国际版功能、模型、合规政策不同，选型时必须明确目标用户所在地。
3. **用框架复杂度换短期便利**：简单 RAG 场景用 LangGraph 是过度设计；反之，复杂多步决策用纯 LangChain Chain 会难以维护。
4. **未核实开源协议**：部分仓库协议可能随版本变更，生产使用前必须以仓库根目录 LICENSE 文件为准。
5. **厂商绑定低估**：托管 API（OpenAI、Coze）的迁移成本高，若未来需多云/多模型，应在架构层抽象接口。
6. **忽视社区信息时效性**：本文档中标注"需验证"或来自社区的信息（如废弃日期）可能滞后，最终以官方公告为准。

---

## 检查清单 / Checklist

- [ ] 已访问候选平台官网，确认其仍在活跃维护。
- [ ] 已查阅目标平台的开源协议（LICENSE 文件）。
- [ ] 已确认目标平台是否处于废弃/迁移状态（特别是 OpenAI Assistants API）。
- [ ] 已明确数据驻留与合规要求，并据此判断是否必须私有化部署。
- [ ] 已走过决策树的 Q1–Q7，记录了每个分支的选择理由。
- [ ] 已填写"平台选型记录卡"并存档，便于后续追溯。
- [ ] 标注"需验证"的信息已在动手前通过官方文档二次确认。
