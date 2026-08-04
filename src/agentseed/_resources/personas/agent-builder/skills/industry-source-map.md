---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 需要了解每条规则的工业界来源 / 审计现有智能体对照来源时
terminates_when: T    # 完成对应规则的工业界来源、集成模式、实战教训查阅
provides: π           # 工业界来源图谱 + 集成模式 + 实战教训
interface: R          # 输入=智能体构造需求；输出=构造流程 + 来源图谱 + 检查清单
---

# 工业界来源图谱 (Industry Source Map)

## Part 1: Industry Source Map / 第一部分：工业界来源图谱

以下表格记录了 AgentSeed 每条规则/框架的工业界来源、原始出处、以及我们吸收时做的调整。

The following table records the industry source, original reference, and our adaptation for each rule/framework in AgentSeed.

### 1.1 规则来源对照表 / Rule Source Mapping

| AgentSeed 规则 | 工业界来源 | 原始出处 / Source | 核心思想 / Core Idea | 我们的调整 / Our Adaptation |
|---|---|---|---|---|
| §1 真实性铁律 (10 条) | Anthropic Constitutional AI + Karpathy 实践 | Anthropic "Claude's Constitution" (2023); Karpathy "AI Coding Rules" (2025) | AI 必须有不可违反的真实性底线 | 扩展为 10 条，加入用户矛盾检测和高声失败 |
| §2 角色定义铁律 | OpenAI GPT Best Practices | OpenAI Cookbook "GPT Best Practices" (2023) | 角色必须具体、边界清晰 | 增加可验证性要求和人格一致性 |
| §3 CTCO 框架 | GPT-5.2 系统提示词工程 | OpenAI GPT-5.2 Prompting Guide (2025) | Context→Task→Constraints→Output 四段式 | 与现有结构化提示词规则融合 |
| §3 结构化提示词 | OpenAI + Anthropic 通用实践 | OpenAI Prompt Engineering Guide; Anthropic Prompt Engineering | 身份→能力→约束→输出→异常 | 增加 < 2000 token 限制和版本号要求 |
| §4 推理深度切换 | GPT-5.2 Reasoning Effort | OpenAI GPT-5.2 System Card (2025) | Low/Medium/High 显式声明推理深度 | 整合到现有推理模式选型矩阵 |
| §4 推理模式选型 | ReAct + Plan-and-Execute 论文 | Yao et al. "ReAct" (2022); Wang et al. "Plan-and-Solve" (2023) | 按任务复杂度选推理模式 | 扩展为 5 种模式 + 决策树 |
| §5 工具内嵌策略 | Google ADK Tool Context | Google Agent Development Kit Documentation (2025) | ToolContext 携带 policy 约束 | 与现有五级副作用标注结合 |
| §5 工具副作用五级标注 | AutoGen Tool Safety | Microsoft AutoGen Framework (2024) | 工具按副作用分级管理 | 扩展为五级：只读/安全写/破坏性/执行代码/网络请求 |
| §5 幂等工具调用 | AutoGen Idempotency | Microsoft AutoGen "Tool Call Patterns" (2024) | 同一调用重复执行无副作用 | 作为工具设计强制要求 |
| §6 记忆分层架构 | LangChain Memory + MemGPT | LangChain Memory Types; Packer et al. "MemGPT" (2023) | 短期/长期/情景记忆分层 | 增加上下文窗口预算分配 |
| §7 知识注入分级 | RAG + Anthropic Context | Lewis et al. "RAG" (2020); Anthropic "Context Engineering" (2025) | 来源分级、时效标注 | 增加冲突解决和单次 ≤ 3000 token 限制 |
| §8 LLM-as-Judge | Google ADK + Anthropic | Google ADK "LLM-as-Judge" (2025); Anthropic "Using LLMs to Evaluate LLMs" (2024) | 廉价模型做安全审查层 | 与现有安全护栏融合，作为第二审查层 |
| §8 安全护栏 | OWASP LLM Top 10 | OWASP "Top 10 for LLM Applications" (2024) | 提示注入防御、PII 保护 | 扩展为人机协作确认点 + 降级策略 |
| §9 notify vs ask | Manus 消息分级 | Manus AI "System Prompt Design" (2025) | 非阻断通知 vs 阻断询问 | 整合到现有对话流程状态管理 |
| §9 对话流程设计 | Rasa + Microsoft Bot Framework | Rasa "Conversation Design" (2023); Microsoft Bot Framework | 意图归一化、状态管理 | 增加 {action+target+constraints} 格式 |
| §10 Token 无限、上下文有限 | Anthropic Context Engineering | Anthropic "Effective Context Engineering" (2025); Karpathy "Context Window" (2025) | Token 预算不受限但上下文窗口是稀缺资源 | 与现有压缩策略和重注入机制结合 |
| §10 上下文压缩 | Anthropic + OpenAI 实践 | Anthropic "Long Context" (2025); OpenAI "Managing Context" (2024) | 压缩保留决策与结果 | 增加 5 轮重注入和子智能体摘要限制 |
| §11 委托深度限制 | AutoGen Delegation | Microsoft AutoGen "Multi-Agent Patterns" (2024) | 多智能体委托链最大 3-5 跳 | 作为强制限制写入规则 |
| §11 多智能体协作 | AutoGen + CrewAI | AutoGen (Microsoft); CrewAI (João Moura, 2024) | 顺序/并行/层级协作模式 | 增加 JSON-only 通信约束 |
| §12 评估框架 | DeepEval + RAGAS | DeepEval (Confident AI); RAGAS (2023) | 多维度评估 + 对抗测试 | 扩展为四维评估 + ≥ 20 测试用例 |
| §13 部署配置 | LangChain + Dify 部署实践 | LangChain Deploy; Dify Platform (2024) | 平台无关配置 + 适配层 | 设计六域 config.yaml 模式 |
| §14 演进策略 | Anthropic Rule Evolution | Anthropic "Claude Improvement" (2024); Karpathy "Rule Iteration" (2025) | 规则需要持续迭代 | 增加日志分析和优化循环 |
| §15 反 AI 味 | Karpathy + 工业界共识 | Karpathy "De-AI-ifying" (2025); 通用写作指南 | 去模板化、直接输出结论 | 作为强制规则而非建议 |
| §16 隐私合规 | GDPR + PIPL + CCPA | EU GDPR (2018); China PIPL (2021); California CCPA (2018) | PII 脱敏、数据最小化 | 增加审计日志要求 |
| §17 紧急例外 | Karpathy Emergency Override | Karpathy "AI Coding Rules" §Emergency (2025) | 紧急时可降级非 P0 规则 | P0 永不可例外 |
| 规则自进化协议 | Anthropic "Wrong Twice, Add a Rule" | Anthropic "Constitutional AI Updates" (2024); Karpathy "Rule Self-Evolution" (2025) | 同类错误出现两次则加规则 | 增加季度精简和规则衰减机制 |
| 自动化评估框架 | DeepEval / RAGAS / G-Eval | DeepEval (Confident AI); RAGAS (2023); Liu et al. "G-Eval" (2023) | 三道判定 + 多维雷达图 + CI 集成 | 扩展为正则黑名单→语义必中→LLM-as-judge CoT |
| 工具调用量化 | BFCL (Berkeley) | UC Berkeley Function Calling Leaderboard (2024) | 5 指标量化工具调用质量 | AST + 语义双层比对 |
| τ-bench 测试架构 | τ-bench (Sierra) | Yao et al. "τ-bench" (Sierra, 2024) | 三角色 + 策略遵守率 + 状态校验 | 作为集成测试层与单元评估互补 |
| 跨平台一致性 | Chatbot Arena | Chiang et al. "Chatbot Arena" (LMSYS, 2024) | pairwise + Elo 排名 | 增加可接受差异范围定义 |
| 六类 span 模型 | OpenTelemetry GenAI | OTel GenAI semantic conventions | root/agent/subagent/transfer/rule/tool 六类 span | 扩展原有四类追踪为六类 |
| 可观测性架构 | Langfuse / Phoenix / OTel | Langfuse (开源); Arize Phoenix; OTel GenAI | 采集→存储→分析三层 + trace→dataset 闭环 | 增加自部署隐私约束 |
| 对抗性测试 | Promptfoo / Garak / PyRIT | Promptfoo; NVIDIA Garak; Microsoft PyRIT | 7 类攻击 + 多轮对抗 | 每规则 50–100 变体 |
| 幻觉检测 | SelfCheckGPT / HEM / RAGAS | Manakul et al. "SelfCheckGPT" (Cambridge, 2023); Vectara HEM; RAGAS | 三层检测 + 数字类重点 | 按成本递增使用三层 |
| Constitutional Self-Critique | Anthropic Constitutional AI | Bai et al. "Constitutional AI" (Anthropic, 2022) | 全规则 self-critique + RLAIF 内化 | 从 5 关自检扩展为全规则 critique |
| Reflexion 自我反思 | Shinn et al. "Reflexion" | Shinn et al. "Reflexion" (2023) | 失败三步循环 + 反思记忆 | 与步骤检查点互补 |
| GraphRAG / Agentic RAG | Microsoft GraphRAG / CRAG / Self-RAG | Edge et al. "GraphRAG" (Microsoft, 2024); Yan et al. "CRAG" (2024); Asai et al. "Self-RAG" (2023) | Naive→Graph→Corrective→Self 四层 | 与知识图谱记忆叠加 |
| MCP Server 封装 | Anthropic MCP | Anthropic "Model Context Protocol" (2024.11 开源) | 核心能力封装为标准 MCP 工具 | 默认只读，写操作显式授权 |

### 1.2 研究过的其他来源（未直接采用但影响了设计）/ Other Sources Researched

| 来源 / Source | 贡献 / Contribution | 为何未直接采用 / Why Not Adopted Directly |
|---|---|---|
| Devin (Cognition) | 自主编码智能体架构参考 | 闭源，仅从演示视频推断，无法验证细节 |
| AGENTS.md 标准 (agents.md) | 跨工具规则文件标准 | 我们已有 AGENTS.md + sync_rules.py 体系，功能覆盖 |
| steipete/agent-rules | 实用编码规则集合 | 与 Karpathy 规则重叠度高，选择 Karpathy 作为主参考 |
| Meta Llama Guard | 内容安全分类器 | 需要模型部署，超出提示词工程范围 |
| Cursor Rules (.cursorrules) | 项目级 AI 规则文件 | 我们已有更完善的路径级规则系统 |
| Microsoft Semantic Kernel | 智能体编排框架 | 编排框架非规则体系，理念已被 AutoGen 参考 |
| LangGraph | 图式智能体编排 | 编排框架，我们的工作流编排技能已覆盖核心思想 |

---

## Part 3: Integration Patterns / 第三部分：集成模式

### 3.1 单一事实源模式 / Single Source of Truth Pattern

```
AGENTS.md（唯一源头）
    │
    ├──▶ scripts/sync_rules.py（同步脚本）
    │       │
    │       ├──▶ CLAUDE.md（Claude Code 适配）
    │       ├──▶ GEMINI.md（Gemini 适配）
    │       └──▶ .github/copilot-instructions.md（Copilot 适配）
    │
    ├──▶ @@skills/*.md（技能文档，内联展开）
    │
    └──▶ prompts/*.md（子智能体定义，参见链接）
```

**关键教训**：
- 永远只编辑 AGENTS.md，生成文件不可手动编辑
- `@@path` 表示内联展开（同步时嵌入），`path` 表示参见链接（不展开）
- 修改后必须运行 `python scripts/sync_rules.py` 并提交所有变更

### 3.2 规则级联管理 / Rule Cascade Management

当新增或修改规则时，以下文件可能需要同步更新——这是从实际审计中总结的级联影响清单：

When adding or modifying rules, the following files may need cascade updates — this checklist is summarized from real audit experience:

| 变更类型 | 可能受影响的文件 | 检查要点 |
|---------|----------------|---------|
| 新增 §X 规则 | system-prompt.md XML 段 | 新规则是否需要镜像到 XML 段？ |
| 新增 §X 规则 | 子智能体 .md 文件 | 哪些子智能体需要引用新规则？ |
| 新增 §X 规则 | README.md / README_CN.md / README_JA.md | 章节数量是否需要更新？描述是否需要添加？ |
| 新增 §X 规则 | PR_TEMPLATE.md | 是否需要添加新规则的 checklist 项？ |
| 新增 §X 规则 | CONTRIBUTING.md | 规则范围是否需要更新？ |
| 新增 §X 规则 | CHANGELOG.md | 是否记录了变更？ |
| 新增 §X 规则 | INIT-PROMPT.md | 初始化指令是否需要同步？ |
| 新增技能文档 | AGENTS.md References | 新技能是否已登记在引用清单？ |
| 新增技能文档 | registry.md | 新技能是否已注册？ |
| 新增技能文档 | skill-hub.md | 新技能是否已加入导航索引？ |
| 版本号变更 | AGENTS.md 顶部版本号 | 版本号是否已更新？ |
| 版本号变更 | README badge | 徽章版本号是否已更新？ |
| 版本号变更 | CHANGELOG.md | 新版本条目是否已添加？ |

**关键教训**：每次规则变更后，必须运行级联检查。遗漏级联更新是最常见的质量问题——在我们实际项目中，40+ 文件需要级联更新，遗漏率高达 30%。

### 3.3 版本管理策略 / Version Management

遵循语义化版本（Semantic Versioning）：

| 变更类型 | 版本 bump | 示例 |
|---------|----------|------|
| 规则结构重组、红线重新定义 | MAJOR (x.0.0) | 从 1.x 到 2.0 |
| 新增规则或增强，向后兼容 | MINOR (x.y.0) | 新增 §X 规则 |
| 修正措辞、补充说明 | PATCH (x.y.z) | 修复错别字 |

**版本兼容策略**：AI 注入新版规则时先检查项目 AGENTS.md 版本号；MAJOR 差异时警告用户迁移。

---

## Part 4: Lessons Learned / 第四部分：实战教训

### 4.1 常见失败模式 / Common Failure Modes

以下是从实际项目中反复出现的失败模式，每一条都有对应的规则来防止：

The following failure modes recurred in real projects. Each has a corresponding rule to prevent it:

| 失败模式 | 频率 | 后果 | 防护规则 | 规则来源 |
|---------|------|------|---------|---------|
| 编造 API/库 | 极高 | 代码无法运行 | §1 禁止造假 + 反幻觉机制 | Anthropic + Karpathy |
| 遗漏级联更新 | 高 | 规则不一致 | 级联影响清单（本文 §3.2） | 实际审计经验 |
| 模糊角色定义 | 高 | 智能体行为不可预测 | §2 角色定义铁律 | OpenAI Best Practices |
| 上下文漂移 | 中 | 忘记原始目标 | §10 每 5 轮重注入 | Anthropic Context Engineering |
| 提示注入成功 | 中 | 安全漏洞 | §8 四层注入防御 | OWASP LLM Top 10 |
| 工具副作用失控 | 中 | 数据丢失 | §5 五级副作用标注 | AutoGen |
| 多智能体无限委托 | 低 | 资源耗尽 | §11 委托深度 ≤ 5 跳 | AutoGen |
| 规则膨胀不精简 | 低 | 规则过多难以遵守 | 规则自进化协议·规则衰减 | Anthropic + Karpathy |
| 技能只创建不淘汰 | 中 | 技能库膨胀、低效技能误导加载 | §14 技能生命周期·淘汰阶段（连续 N 次低分归档） | Hermes Agent + MUSE-Autoskill |
| 策展器自动执行合并/淘汰 | 低 | 误删有用技能、不可回滚 | §14 策展器安全约束（只建议不执行，须用户确认） | Hermes Agent v0.12.0 Curator |
| 沉默失败被忽略 | 中 | 错误答案长期未被发现 | §14 轨迹洞察·沉默失败检测 | Amazon Bedrock AgentCore |
| 知识图谱全图遍历 | 低 | 检索成本爆炸、响应超时 | §6 图遍历 ≤ 2 跳、单次注入实体 ≤ 20 | Zep/Graphiti |
| 用户画像当事实陈述 | 低 | 侵犯隐私、冒犯用户 | §6 用户建模·推测前缀 + 隐私约束（P0） | Hermes Agent + Honcho |
| 无 trace 导致盲优化 | 高 | 出了问题不知道哪一步挂的，只能瞎猜瞎改 | Pattern 5 六类 span 模型 + Pattern 6 可观测性架构 | OpenTelemetry GenAI / Langfuse |
| 无自动化评估导致回归成本高 | 高 | 每次改规则后手工 spot-check 漏掉回归问题，生产事故后才发觉 | Pattern 1 三道判定 + CI 集成 + 多维雷达图 | DeepEval / RAGAS / G-Eval |
| 无对抗测试导致生产事故 | 中 | 手工写的几个边界 case 测不出攻击者真实套路，上线后被注入 | Pattern 7 对抗测试（7 类攻击 × 50–100 变体 + 多轮对抗） | Promptfoo / Garak / PyRIT |
| 数字类幻觉未检测 | 中 | 电话/金额/时限/法条号输出错误，硬伤事故 | Pattern 8 幻觉检测（三层 + 数字类重点） | SelfCheckGPT / HEM / RAGAS |
| judge 与被测同模型 | 中 | 评估虚高，同源偏差，问题被掩盖 | Pattern 1 judge 模型与被测不同族 | G-Eval 实践 |
| Reflexion 无限重试 | 低 | 资源耗尽、API 配额烧光 | Pattern 10 最大重试 3 次，超限请求人工 | Shinn et al. "Reflexion" |
| GraphRAG 用于简单场景 | 低 | 过度设计，构建知识图谱成本远超收益 | Pattern 11 简单场景用 Naive RAG，跨文档推理才上 GraphRAG | Microsoft GraphRAG |
| MCP server 默认开放写 | 低 | 安全漏洞，未授权写操作 | Pattern 12 默认只读，写操作显式授权 | Anthropic MCP |

### 4.2 审计方法论 / Audit Methodology

从三次大规模仓库审计中总结的方法论：

1. **交叉引用检查**：所有 `@@path` 引用必须指向存在的文件
2. **版本号一致性**：AGENTS.md 版本号 = README badge = CHANGELOG 最新条目
3. **计数一致性**：README 中的章节数/技能数 = 实际文件数 = CI 检查数
4. **中英文一致性**：中文规则条数 = 英文规则条数（双语仓库特有）
5. **镜像一致性**：system-prompt.md XML 段 = AGENTS.md 对应章节
6. **级联完整性**：新增规则后，级联影响清单中的每一项都要检查

### 4.3 Karpathy 12 规则系统详解 / Karpathy 12-Rule System

Andrej Karpathy 公开了他的 AI 编码规则系统，在实践中将错误率从 41% 降到 3%。以下是完整对照：

**基础四规则（Base 4 Rules）**：

| # | 规则 | AgentSeed 对应 | 落地位置 |
|---|------|------------------|---------|
| 1 | Think Before Coding | §4 推理模式选型 | 强制选型+显式声明 |
| 2 | Simplicity First | §2 角色定义 | 能力边界最小化 |
| 3 | Surgical Changes | §3 提示词质量 | 不改无关代码 |
| 4 | Goal-Driven Execution | §1 真实性铁律 | 不确定即问 |

**扩展八规则（Extended 8 Rules）**：

| # | 规则 | AgentSeed 对应 | 落地位置 |
|---|------|------------------|---------|
| 5 | Model for Judgment Only | §11 模型边界规则 | 判断归模型，确定性归代码 |
| 6 | Token Budgets | §10 上下文工程 | Token 无限但上下文有限 |
| 7 | Surface Conflicts | §3 冲突表面化 | 两种矛盾模式标记其一 |
| 8 | Read Before Write | §3 读后写 | 加代码前先读文件 |
| 9 | Step Checkpoints | §16 步骤检查点 | 每步完成后总结+验证 |
| 10 | Tests Verify Intent | §12 评估框架 | 测试验证意图而非实现 |
| 11 | Match Conventions | §13 部署配置 | 遵循项目现有约定 |
| 12 | Fail Loud | §1 高声失败 | 不隐藏不确定性 |

### 4.4 Anthropic 规则自进化机制 / Anthropic Rule Self-Evolution

Anthropic 提出的"Wrong Twice, Add a Rule"反馈循环：

```
错误发生
    │
    ▼
第一次 ──────▶ 记录但不加规则（可能是偶发）
    │
    ▼
同类错误第二次 ──────▶ 触发规则提案
    │
    ▼
提案格式：
  [Suggested Rule]
  Location: §X → New item
  Content: ...
  Reason: Nth occurrence of same error
    │
    ▼
用户确认 ──────▶ AI 写入规则 → 运行 sync_rules.py
    │
    ▼
规则生效
    │
    ▼
季度精简 ──────▶ 连续 10 次正确遵守的规则
    │           可从"必须"降级为"建议"
    ▼
规则衰减
```
