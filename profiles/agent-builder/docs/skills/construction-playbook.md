# Agent Construction Playbook / 智能体构造方法论

## One-line Description / 一句话描述

> 从工业界最佳实践研究中提炼的智能体构造完整方法论：每条规则来自哪里、为什么这样设计、如何组合成一个完整智能体。
>
> A complete agent construction methodology distilled from industry best-practices research: where each rule comes from, why it is designed that way, and how to assemble them into a complete agent.

---

## When to Use / 适用场景

- 从零开始构造一个新智能体时，需要理解每条规则的设计理由 / Understanding the design rationale of each rule when building a new agent from scratch
- 需要向团队或利益相关者解释"为什么这样设计"时 / Explaining "why this design" to teams or stakeholders
- 审计现有智能体时，对照工业界来源检查是否有遗漏 / Auditing existing agents against industry sources for gaps
- 规则版本升级时，评估哪些工业界新实践值得吸收 / Evaluating which new industry practices to absorb during rule version upgrades
- 新人学习智能体构造时，作为入门教材 / Onboarding material for newcomers learning agent construction

---

## Part 1: Industry Source Map / 第一部分：工业界来源图谱

以下表格记录了 AgentCreater 每条规则/框架的工业界来源、原始出处、以及我们吸收时做的调整。

The following table records the industry source, original reference, and our adaptation for each rule/framework in AgentCreater.

### 1.1 规则来源对照表 / Rule Source Mapping

| AgentCreater 规则 | 工业界来源 | 原始出处 / Source | 核心思想 / Core Idea | 我们的调整 / Our Adaptation |
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

## Part 2: Construction Methodology / 第二部分：构造方法论

### 2.1 智能体构造七步法 / Seven-Step Agent Construction

以下是从实际项目中提炼的构造流程，每一步都有明确的输入、输出和质量门禁。

The following construction process is distilled from real projects. Each step has clear inputs, outputs, and quality gates.

```
┌─────────────────────────────────────────────────────────────┐
│                  智能体构造流程 / Construction Flow            │
└─────────────────────────────────────────────────────────────┘
                                                                
  Step 1          Step 2          Step 3          Step 4       
  ┌──────┐       ┌──────┐       ┌──────┐       ┌──────┐      
  │ 需求  │──────▶│ 角色  │──────▶│ 提示词 │──────▶│ 工具  │      
  │ 澄清  │       │ 定义  │       │ 设计  │       │ 编排  │      
  └──────┘       └──────┘       └──────┘       └──────┘      
   output:        output:        output:        output:      
   需求文档        四层角色卡      系统提示词      工具定义集    
                                                                
  Step 5          Step 6          Step 7       
  ┌──────┐       ┌──────┐       ┌──────┐      
  │ 记忆  │──────▶│ 安全  │──────▶│ 测试  │      
  │ &知识 │       │ 护栏  │       │ &评估 │      
  └──────┘       └──────┘       └──────┘      
   output:        output:        output:      
   记忆策略        护栏配置        ≥20 测试用例 
```

#### Step 1: 需求澄清 / Requirements Clarification

**原则**：不确定即问（§1），严禁猜测。

- 核心职责：智能体要解决什么问题？
- 服务对象：谁用？什么场景下用？
- 领域边界：专长什么？不做什么？
- 部署平台：Dify / Coze / OpenAI / LangChain / 自定义？
- 约束条件：合规、品牌、平台限制？

**质量门禁**：需求文档经用户确认后才进入下一步。

#### Step 2: 角色定义 / Role Definition

**原则**：四层建模（§2），禁止模糊描述。

1. **身份层**：角色名 + 一句话定位
2. **能力层**：能做什么（可验证的具体能力）
3. **限制层**：不能做什么 + 回退策略
4. **人格层**：语气、风格、跨对话一致性

**关键教训**：每条禁止行为必须配套回退策略。只说"不能做 X"不够，必须说"不能做 X，遇到 X 时改做 Y"。

#### Step 3: 提示词设计 / Prompt Design

**原则**：CTCO 框架（§3）+ 结构化五段式。

1. **Context**：背景信息、用户画像、场景约束
2. **Task**：单一原子任务描述
3. **Constraints**：负面约束 + 范围限制（与 Task 分离，减少指令漂移）
4. **Output**：精确输出格式（JSON / Markdown / 纯文本）

**关键教训**：
- 核心指令 < 2000 token，超出的拆分为技能文档按需加载
- 不硬编码用户数据，通过变量注入
- 每条指令必须可测试——禁止"尽量做好"这类模糊表述
- 提示词必须有版本号，每次修改记录变更原因和效果对比

#### Step 4: 工具编排 / Tool Orchestration

**原则**：五级副作用标注（§5）+ 工具内嵌策略。

- 每个工具必须标注副作用级别：只读 / 安全写 / 破坏性 / 执行外部代码 / 网络请求
- 破坏性及以上级别的工具必须有人机协作确认点
- 工具内嵌策略（ToolContext）：工具参数由模型设置，策略约束由开发者设置，工具层强制执行安全边界
- 幂等设计：同一工具调用重复执行不产生副作用
- 单智能体 ≤ 15 个工具，超出则拆分为多智能体

**关键教训**：工具命名用"动词+名词"（如 `send_email` 而非 `email_handler`），参数必须有类型和示例。

#### Step 5: 记忆与知识 / Memory & Knowledge

**原则**：分层记忆（§6）+ 分级注入（§7）。

1. **短期记忆**：当前对话上下文
2. **长期记忆**：RAG 检索，不全量注入
3. **情景记忆**：历史交互模式
4. **知识图谱记忆（可选第4层）**：当任务涉及多实体、跨时间推理时启用。实体记忆自动提取实体并维护关系；时态记忆带 `valid_at`/`invalid_at` 双时间戳；三层子图 Episode→语义实体→社区。来源 Zep/Graphiti。默认不启用——简单 FAQ 场景不需要；多实体跨时间推理场景才启用，启用前评估存储与检索成本。
5. **用户深度建模（可选层）**：跨会话构建用户心智模型，从情景记忆推导"用户是什么样的人"。建模维度：技术栈偏好、代码风格偏好、沟通详略偏好、常见错误模式、知识水平。隐私约束（P0）：不上传、不跨用户共享、可查看可删除；结论须标注"推测："前缀。来源 Hermes Agent + Honcho。默认不启用——需要跨会话个性化时才启用。

**上下文窗口预算分配**（来自实际经验）：
- 系统提示 20% / 工具描述 15% / 用户输入 30% / 记忆注入 20% / 输出 15%

**关键教训**：Token 预算不受限，但上下文窗口是稀缺资源。不放弃上下文管理，每 5 轮重注入原始用户目标防漂移。知识图谱与用户建模是可选高级层，不要为凑功能而强行启用——只在该角色确实需要多实体跨时间推理或跨会话个性化时才开启，否则徒增存储与维护成本。

#### Step 6: 安全护栏 / Safety Guardrails

**原则**：P0 红线永不可例外（§8）+ LLM-as-Judge 双层审查。

1. **第一层（规则护栏）**：行为边界声明 + 人机协作确认点 + 提示注入防御
2. **第二层（LLM-as-Judge）**：廉价快速模型审查主模型输出

**提示注入防御四层**（来自实际审计经验）：
- 信任边界隔离：外部数据打 `[UNTRUSTED]` 标记
- 指令覆盖检测：检测"忽略以上指令"等覆盖模式
- 高权限动作确认：发邮件/付款/删数据必须人工确认
- 动作隔离：外部数据不直接触发动作

#### Step 7: 测试与评估 / Testing & Evaluation

**原则**：四维评估（§12）+ ≥ 20 测试用例 + 三道判定 + 工具调用量化 + τ-bench harness + 对抗性测试 + 幻觉检测。

Step 7 在 v1.5.0 大幅扩展，从"写 20 个测试用例"升级为多层评估体系。完整 12 项高级架构模式见 `@@docs/skills/advanced-patterns.md`。

##### 7.1 测试用例设计（基础层）/ Test Case Design (Base Layer)

- **正常流程测试**：核心路径覆盖
- **边界测试**：极端输入、空输入、超长输入
- **对抗测试**：提示注入、越权、PII 提取
- **真实性测试**：给不确定问题，验证是否承认"不知道"而非编造

每个 golden case 含三段结构化字段：
1. **期望响应要点**（required points）：输出必须覆盖的语义要点，用于第二道语义必中判定
2. **禁止响应**（forbidden patterns）：输出不得包含的内容，正则化后用于第一道正则黑名单判定
3. **期望工具调用序列**（expected tool calls）：`[{tool, args, order}]` 结构化字段，用于 BFCL 五指标比对

##### 7.2 三道判定机制（自动化评估框架）/ Three-Gate Judgment (Automated Eval Framework)

来源：DeepEval / RAGAS / G-Eval。每个 case 依次通过三道关卡，全部通过才算合格：

- **第一道：正则黑名单**——禁止响应用正则表达死，命中即判失败。成本最低、速度最快。
- **第二道：语义必中**——期望要点用 embedding 相似度或轻量 LLM 判定是否覆盖，处理"说法不同但意思一致"。
- **第三道：LLM-as-Judge（G-Eval 式 CoT 评审）**——judge 模型先生成评审 CoT（好在哪、差在哪、几分），再输出最终分数。

关键约束：**judge 模型与被测模型不能同型号**（避免同源偏差）。被测用 GPT-4o 则 judge 用 Claude/Gemini，反之亦然。

评估维度从"通过/失败"二值升级为**多维雷达图**：正确性 / 效率 / 完整性 / 工具使用 / 推理质量 / 规则遵守率。每维设定最低线（如规则遵守率不得低于 0.9），低于线即判失败。

golden cases 版本化（纳入 git，只新增不修改），测试集防污染（SWE-bench Live 思想，定期轮换）。CI 集成为 pytest 风格断言，规则变更后自动回归，失败的 case 在 CI 报告里显示是哪一道关卡挂了。

##### 7.3 工具调用可靠性量化（BFCL 五指标）/ Tool-Call Reliability (BFCL)

来源：BFCL (Berkeley Function Calling Leaderboard)。把工具调用拆成 5 个可独立量化的指标：

1. **Tool Selection F1**：该调哪些工具选对了吗（应调集 vs 实调集做 F1）
2. **Argument Exact Match**：参数填对了吗（逐参数比对）
3. **Call Order Accuracy**：调用顺序对吗（有依赖的工具顺序错了会失败）
4. **Hallucinated Tool Call Rate**：调用了不存在的工具吗（模型幻觉出系统里没有的工具名）
5. **Missing Tool Call Rate**：该调没调的工具占应调工具的比例

评估方法分两层：**AST-based（结构等价）** 快筛，**semantic match（语义等价）** 兜底（"北京" = "北京市" = "Beijing"）。5 个指标独立报告，不合成单一分数——合成后定位不了问题。

##### 7.4 τ-bench 式测试架构（集成测试层）/ τ-bench Harness (Integration Layer)

来源：τ-bench (Sierra 2024)。比单轮问答更接近真实部署的三角色架构：

- **用户模拟器**（LLM 扮演用户，多画像：急躁/啰嗦/模糊/对抗）
- **被测 Agent**（正常处理）
- **判定器**（LLM，与被测不同族，判定合规性）

两个关键贡献：
1. **策略遵守率作为独立指标**——不只看任务完成，更看过程是否违反 policy。智能体可能完成任务但违规（绕过身份验证就退款），这种"成功"是事故。
2. **数据库状态校验**——除了对话正确，查数据库验证智能体是否正确修改了系统状态。不能只信对话里的"已修改"措辞。

policy 必须有可机器判定的条款，每个条款配判定函数。多轮对话测试固定随机种子，确保可回归。

##### 7.5 对抗性测试设计（7 类攻击）/ Adversarial Testing (7 Attack Categories)

来源：Promptfoo / Garak (NVIDIA) / PyRIT (Microsoft)。每条 P0 规则配对抗性测试套件：

7 类攻击分类法：注入攻击 / 越狱 / PII 泄露 / 偏见 / 跨语言注入 / 转介链注入 / 知识库投毒。每个规则配 50–100 个攻击变体（LLM 批量生成，人工审核）。

多轮对抗测试：attacker LLM ↔ target LLM（不同模型族），attacker 根据上一轮 target 反应调整策略，逐步逼近突破口。比单轮"一击脱离"更接近真实"持续渗透"。

##### 7.6 幻觉自动检测（三层）/ Hallucination Detection (Three Layers)

来源：SelfCheckGPT / Vectara HEM / RAGAS。重点应用于具体数字类输出（电话/金额/时限/法条号）：

1. **多次采样一致性（SelfCheckGPT）**：同问题采样 N 次，不一致 = 高幻觉概率
2. **输出-来源支撑度（Vectara HEM）**：输出每句话与知识库片段的支撑度
3. **RAG 四维评估（RAGAS）**：faithfulness / answer relevance / context precision / context recall

三层按成本递增使用：先跑 SelfCheckGPT（无需知识库），再跑 HEM（需检索片段），最后跑 RAGAS（需标准答案）。检测失败时降级输出（"我需要确认这个信息"）。

**关键教训**：
- 真实性测试是最容易被忽略但最重要的测试类型。一个会编造答案的智能体比一个承认不知道的智能体危险得多。
- 无自动化评估导致回归成本高——每次改规则后手工 spot-check 漏掉回归问题，生产事故后才发觉。三道判定 + CI 集成是解药。
- 无对抗测试导致生产事故——手工写的几个边界 case 测不出攻击者的真实套路，7 类攻击 × 50–100 变体才能覆盖。
- 无 trace 导致盲优化——没有 span 模型和 trace，出了问题不知道是哪一步挂的，只能瞎猜瞎改。

### 2.2 推理模式选型决策 / Reasoning Pattern Selection

```
任务复杂度?
│
├─ 简单（单步、确定性强）
│  └─ Direct（直接回答）
│     来源：通用 LLM 实践
│
├─ 中等（需要工具调用）
│  └─ ReAct（思考→行动→观察循环）
│     来源：Yao et al. "ReAct" (2022)
│
├─ 复杂（多步骤、有依赖）
│  └─ Plan-and-Execute（先规划再执行）
│     来源：Wang et al. "Plan-and-Solve" (2023)
│
├─ 高风险（需要自我纠错）
│  └─ Reflection（生成→审查→修正）
│     来源：Shinn et al. "Reflexion" (2023)
│
└─ 探索性（多种可能路径）
   └─ Tree-of-Thought（树状探索）
      来源：Yao et al. "Tree of Thoughts" (2023)
```

推理深度（来自 GPT-5.2）：
- **Low**：简单事实查询、格式转换
- **Medium**：分析、对比、工具调用
- **High**：复杂推理、多步规划、创意生成

### 2.3 多智能体协作模式选型 / Multi-Agent Collaboration

| 模式 | 来源 | 适用场景 | 通信方式 | 委托深度 |
|------|------|---------|---------|---------|
| 顺序流水线 | AutoGen | 固定流程、每步独立 | JSON 传递 | 1 跳 |
| 并行扇出 | AutoGen | 独立子任务同时执行 | 汇聚合并 | 1 跳 |
| 层级委托 | CrewAI | 复杂任务分解+委派 | 上下→下指令 | ≤ 3-5 跳 |
| 竞争选择 | DeepEval | 多方案择优 | 投票/评分 | 1 跳 |
| 反馈循环 | Reflexion | 迭代改进 | 评价→修正 | ≤ 3 轮 |

### 2.4 高级架构模式选型（Part 2.5）/ Advanced Architecture Pattern Selection

v1.5.0 新增。12 项高级架构模式的选择决策树。完整模式说明见 `@@docs/skills/advanced-patterns.md`。

#### 2.4.1 选型决策树 / Selection Decision Tree

```
你的智能体处于什么阶段？
│
├─ 还没上线，需要评估体系
│  ├─ 需要自动化 CI 评估 ──► Pattern 1 (自动化评估框架)
│  │     触发：每个智能体必须配备
│  │     成本：中（评估套件开发 + CI 运行）
│  ├─ 工具调用频繁 ──► Pattern 2 (BFCL 工具调用量化)
│  │     触发：智能体有 ≥ 3 个工具
│  ├─ 多轮对话 + 有 policy ──► Pattern 3 (τ-bench harness)
│  │     触发：多轮对话场景 + 有可判定 policy
│  └─ 多平台部署 ──► Pattern 4 (跨平台一致性)
│        触发：部署到 ≥ 2 个平台
│
├─ 已上线，需要可观测性
│  ├─ 还没有 trace ──► Pattern 5 (六类 span 模型)
│  │     触发：生产环境必须
│  └─ 有 trace 但没闭环 ──► Pattern 6 (可观测性架构)
│        触发：trace 不能自动沉淀为测试集时
│
├─ 安全敏感场景
│  ├─ 担心被攻击 ──► Pattern 7 (对抗性测试)
│  │     触发：有 P0 规则的智能体必须
│  ├─ 输出含数字/事实 ──► Pattern 8 (幻觉检测)
│  │     触发：输出含电话/金额/时限/法条号
│  └─ 需要输出前对齐 ──► Pattern 9 (Constitutional self-critique)
│        触发：高敏感输出（金额/PII/决策）
│
└─ 任务复杂度超出基础形态
   ├─ 失败重试不智能 ──► Pattern 10 (Reflexion)
   │     触发：失败率 > 10% 且简单重试无效
   ├─ RAG 检索不够好 ──► Pattern 11 (GraphRAG/CRAG/Self-RAG)
   │     触发：Naive RAG 检索质量不达标
   └─ 想多平台复用核心能力 ──► Pattern 12 (MCP 封装)
         触发：核心能力需在 ≥ 3 个平台复用
```

#### 2.4.2 选型矩阵 / Selection Matrix

| 模式 | 类别 | 默认启用 | 触发条件 | 实现成本 | 运行成本 | 不启用的后果 |
|------|------|---------|---------|---------|---------|------------|
| 1 自动化评估 | 评估 | 推荐 | 每个智能体 | 中 | 低 | 回归问题漏检 |
| 2 BFCL 量化 | 评估 | 按需 | ≥ 3 工具 | 低 | 低 | 工具调用问题定位不了 |
| 3 τ-bench harness | 评估 | 按需 | 多轮 + policy | 高 | 中 | 集成问题测不出 |
| 4 跨平台一致性 | 评估 | 按需 | ≥ 2 平台 | 中 | 中 | 平台差异未量化 |
| 5 六类 span | 可观测 | 推荐 | 生产环境 | 中 | 低 | 事故无法复盘 |
| 6 可观测架构 | 可观测 | 推荐 | 生产环境 | 中 | 中 | trace 无法闭环利用 |
| 7 对抗测试 | 安全 | 推荐 | 有 P0 规则 | 高 | 低 | 生产事故 |
| 8 幻觉检测 | 安全 | 按需 | 数字类输出 | 中 | 中 | 数字类幻觉事故 |
| 9 Constitutional | 安全 | 按需 | 高敏感输出 | 中 | 高 | 输出前未对齐 |
| 10 Reflexion | 高级 | 按需 | 失败率 > 10% | 中 | 中 | 失败重试低效 |
| 11 GraphRAG | 高级 | 按需 | 跨文档推理 | 高 | 中 | 检索质量不足 |
| 12 MCP 封装 | 高级 | 按需 | 多平台复用 | 中 | 低 | 重复适配 |

#### 2.4.3 选型原则 / Selection Principles

1. **按需选择，不要全上**——12 项模式都有成本（实现 + 运行 + 维护）。评估体系（1–4）和可观测性（5–6）是基础设施，建议优先；安全对齐（7–9）按场景风险等级选择；高级架构（10–12）按任务复杂度选择。
2. **评估和可观测性优先于高级架构**——没有评估和可观测性就上 Reflexion/GraphRAG，等于盲人开跑车。先把"能量化、能监控"做扎实，再上"高级推理"。
3. **安全对齐按风险等级**——低风险场景（内部工具）可只做 Pattern 7 对抗测试；高风险场景（金融/医疗/法务）三项全上（7+8+9）。
4. **高级架构按复杂度**——简单 FAQ 不需要 Reflexion/GraphRAG；跨文档推理才上 GraphRAG；失败率高且简单重试无效才上 Reflexion。
5. **MCP 封装看复用需求**——单平台部署不需要 MCP；核心能力需在 3+ 平台复用才值得封装成本。

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
    ├──▶ @@docs/skills/*.md（技能文档，内联展开）
    │
    └──▶ docs/prompts/*.md（子智能体定义，参见链接）
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

| # | 规则 | AgentCreater 对应 | 落地位置 |
|---|------|------------------|---------|
| 1 | Think Before Coding | §4 推理模式选型 | 强制选型+显式声明 |
| 2 | Simplicity First | §2 角色定义 | 能力边界最小化 |
| 3 | Surgical Changes | §3 提示词质量 | 不改无关代码 |
| 4 | Goal-Driven Execution | §1 真实性铁律 | 不确定即问 |

**扩展八规则（Extended 8 Rules）**：

| # | 规则 | AgentCreater 对应 | 落地位置 |
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

---

## Part 5: Construction Checklist / 第五部分：构造清单

以下是从零构造一个完整智能体的清单，按步骤组织。每项都必须打勾才能进入下一步。

The following is a step-by-step checklist for building a complete agent from scratch. Every item must be checked before proceeding.

### Phase 1: Foundation / 基础

- [ ] 需求文档已撰写并经用户确认
- [ ] 核心职责一句话可描述
- [ ] 服务对象和使用场景已明确
- [ ] 部署平台已确定
- [ ] 合规约束已列出

### Phase 2: Role & Prompt / 角色与提示词

- [ ] 角色名 + 一句话定位已定义
- [ ] 能力清单（每条可验证）已列出
- [ ] 限制清单（每条有回退策略）已列出
- [ ] 人格/语气已定义
- [ ] 系统提示词按 CTCO 框架编写
- [ ] 核心指令 < 2000 token
- [ ] 无硬编码用户数据（通过变量注入）
- [ ] 提示词有版本号

### Phase 3: Tools & Memory / 工具与记忆

- [ ] 每个工具标注五级副作用
- [ ] 工具命名"动词+名词"
- [ ] 参数有类型和示例
- [ ] 破坏性工具有人机确认点
- [ ] 工具设计为幂等
- [ ] 工具 ≤ 15 个
- [ ] 记忆分层策略已定义
- [ ] 上下文窗口预算已分配
- [ ] 知识注入来源已分级
- [ ] 是否启用知识图谱层已决策（默认关闭；多实体跨时间推理才启用）
- [ ] 若启用知识图谱：实体/关系类型、时态字段（valid_at/invalid_at）、三层子图、检索深度限制已定义
- [ ] 若启用知识图谱：图遍历 ≤ 2 跳、单次注入实体 ≤ 20 已配置
- [ ] 是否启用用户深度建模层已决策（默认关闭；需跨会话个性化才启用）
- [ ] 若启用用户建模：建模维度、置信度阈值、重估周期已定义
- [ ] 若启用用户建模：隐私约束（不上传/不共享/可删除/推测前缀，P0）已配置

### Phase 4: Safety & Evaluation / 安全与评估

- [ ] P0 红线已声明
- [ ] 提示注入防御四层已配置
- [ ] 人机协作确认点已设置
- [ ] 降级策略已定义
- [ ] ≥ 20 个测试用例（含对抗+真实性测试）
- [ ] LLM-as-Judge 审查层已配置（如适用）

#### Phase 4.1: 评估套件 Checklist / Evaluation Suite（Pattern 1–4）

- [ ] 每个 golden case 含三段结构化字段（期望响应要点 + 禁止响应 + 期望工具调用序列）
- [ ] 三道判定机制已实现（正则黑名单 → 语义必中 → LLM-as-judge CoT）
- [ ] judge 模型与被测模型不同族（避免同源偏差）
- [ ] 多维雷达图已配置（正确性/效率/完整性/工具使用/推理质量/规则遵守率）
- [ ] 每维最低阈值线已设定（如规则遵守率不得低于 0.9）
- [ ] golden cases 版本化（纳入 git，只新增不修改，废弃标注原因）
- [ ] 测试集防污染机制已建立（定期轮换，公开/私有拆分）
- [ ] CI 集成为 pytest 风格断言，规则变更触发自动回归
- [ ] BFCL 五指标已采集（selection F1 / arg match / order accuracy / hallucinated rate / missing rate）
- [ ] BFCL AST 比对优先，语义比对兜底
- [ ] τ-bench harness 已配置（如适用：用户模拟器 + 被测 + 判定器 + 状态校验）
- [ ] policy 条款可机器判定，每条款配判定函数
- [ ] 多轮对话测试固定随机种子
- [ ] 跨平台一致性期望已标注（如多平台部署：必须一致项 + 可接受差异项 + 禁止项）

#### Phase 4.2: 可观测性 Checklist / Observability（Pattern 5–6）

- [ ] 六类 span 模型已定义（root / agent / subagent / transfer / rule / tool）
- [ ] rule span 覆盖所有 P0/P1 规则触发
- [ ] transfer span 记录转介原因
- [ ] span 关系形成树（每个 span 有且仅有一个 parent_span_id）
- [ ] 可观测性接入方案已声明（trace 格式 / 存储位置 / 隐私策略）
- [ ] 采集层（OTel SDK）与存储层（Langfuse）通过 OTLP 解耦
- [ ] 高敏感场景 Langfuse 自部署，数据不出本地
- [ ] PII 在采集时脱敏（非存储时）
- [ ] trace → dataset 沉淀闭环已建立（含人工审核 before golden）
- [ ] 事故记录结构化为 JSONL trace（含 trace_id/parent_span_id/agent_name/input/output/rules_triggered/latency/tool_calls）

#### Phase 4.3: 对抗测试 Checklist / Adversarial Testing（Pattern 7）

- [ ] 每条 P0 规则配对抗性测试套件
- [ ] 7 类攻击分类法已覆盖（注入/越狱/PII 泄露/偏见/跨语言/转介链/知识库投毒）
- [ ] 每规则 ≥ 50 个攻击变体（LLM 批量生成 + 人工审核）
- [ ] 多轮对抗测试已开启（attacker 与 target 不同模型族）
- [ ] 攻击成功归因已记录（哪类攻击、哪个变体、突破哪条规则）
- [ ] 红队定期重跑机制已建立（智能体升级后历史变体全重跑）

#### Phase 4.4: 幻觉检测 Checklist / Hallucination Detection（Pattern 8）

- [ ] 需幻觉检测的输出类型已定义（重点：数字类——电话/金额/时限/法条号）
- [ ] 三层检测已配置（SelfCheckGPT 一致性 → Vectara HEM 支撑度 → RAGAS 四维）
- [ ] 三层按成本递增使用（前层过了不跑后层）
- [ ] 数字类输出用严格精确匹配（非语义等价）
- [ ] 检测失败时降级输出（"我需要确认这个信息"或附不确定性标注）

### Phase 5: Deployment & Evolution / 部署与演进

- [ ] config.yaml 六域已填写
- [ ] 平台适配说明已撰写
- [ ] 回滚策略已定义
- [ ] 日志分析机制已配置
- [ ] 规则自进化反馈循环已建立
- [ ] 技能生命周期五阶段已落地（创建→使用→评估→改进→淘汰）
- [ ] 技能评估指标（成功率/耗时/反馈）采集与汇总机制已配置
- [ ] 技能淘汰阈值（连续 N 次低分）已设定
- [ ] 自主策展器定期运行机制已配置（只建议不执行，须用户确认）
- [ ] 轨迹洞察已配置（沉默失败检测 + 失败轨迹聚类 + 根因推断）

### Phase 6: Advanced Architecture Patterns / 高级架构模式（Pattern 9–12，按需）

- [ ] Constitutional self-critique 触发条件已定义（高敏感/低置信度/首次任务类型）
- [ ] self-critique 覆盖规则范围已声明（P0 全覆盖）
- [ ] self-critique 修订可追溯（初稿/违反项/修订版本已记录）
- [ ] RLAIF 微调是否启用已决策（默认 prompt 内 self-critique；高频+规则稳定才 RLAIF）
- [ ] Reflexion 失败处理策略已定义（最大重试 3 次 + 反思深度分层）
- [ ] 反思记忆已接入情景记忆（只存失败教训，有衰减机制）
- [ ] RAG 策略层级已定义（Naive → Graph → Corrective → Self-RAG）
- [ ] GraphRAG 启用前已评估成本（仅跨文档推理场景启用）
- [ ] CRAG 检索质量评估阈值可调
- [ ] Self-RAG 检索决策可观测（reasoning 记录到 trace）
- [ ] 核心工具的 MCP 封装选项已标注（规则校验/知识查询/转介执行/状态管理）
- [ ] MCP server 默认只读，写操作显式授权
- [ ] MCP 工具描述完整（name / description / inputSchema / 副作用级别）

---

## Cross-References / 交叉引用

- 角色设计方法论 → `docs/skills/role-design.md`
- 提示词模式库 → `docs/skills/prompt-patterns.md`
- 推理模式详解 → `docs/skills/reasoning-patterns.md`
- 工具设计规范 → `docs/skills/tool-design.md`
- 记忆系统设计 → `docs/skills/memory-systems.md`
- 知识注入策略 → `docs/skills/knowledge-injection.md`
- 安全护栏设计 → `docs/skills/safety-guardrails.md`
- 评估框架 → `docs/skills/evaluation-framework.md`
- 多智能体协作 → `docs/skills/multi-agent.md`
- 上下文工程 → `docs/skills/context-engineering.md`
- 对话流程设计 → `docs/skills/conversation-design.md`
- 演进策略 → `docs/skills/evolution-policy.md`
- 部署指南 → `docs/skills/deployment-guide.md`
- 技能导航索引 → `docs/skills/skill-hub.md`
- 高级架构模式（12 项） → `docs/skills/advanced-patterns.md`
