# reasoning-patterns.md — 推理模式详解
# Reasoning Patterns In Detail

---

## 一句话描述 / One-line Description

> 本文档详解四种核心 Agent 推理模式——ReAct、Plan-and-Execute、Reflection、Tree-of-Thought——每种附真实原理、论文引用、适用场景、组合规则与选型矩阵，供架构设计时按需选取与组合。
>
> This document details four core Agent reasoning patterns — ReAct, Plan-and-Execute, Reflection, and Tree-of-Thought — each with real principles, paper citations, applicable scenarios, combination rules, and a selection matrix for architecture-level selection and composition.

---

## 适用场景 / Applicable Scenarios

- **Agent 架构设计阶段**：决定 Agent 如何"思考"和"行动"——是边想边做、先规划后执行、事后反思、还是多路探索。
- **效果诊断阶段**：Agent 在某类任务上表现不佳，需定位是推理模式选错还是组合不当。
- **性能权衡阶段**：在准确率、延迟、Token 成本之间做架构级取舍。
- **技术评审阶段**：向团队论证所选推理模式的学术依据与工程权衡。

---

## 核心方法论 / Core Methodology

四种推理模式回答不同问题：

| 模式 | 核心问题 | 一句话本质 |
|------|----------|------------|
| **ReAct** | "如何边推理边行动？" | 推理（Thought）与行动（Action）交替进行，用行动获取外部信息反哺推理。 |
| **Plan-and-Execute** | "如何先规划再执行？" | 先生成完整计划，再逐步执行，执行结果可反馈修正计划。 |
| **Reflection** | "如何从失败中学习？" | 执行后自我评估，将反思转化为语言反馈，在下一轮迭代中改进。 |
| **Tree-of-Thought (ToT)** | "如何在多条路径中择优？" | 将推理组织为树形结构，在每一步生成多个候选"思考"，评估并搜索最优路径。 |

```
复杂度 / 成本递增 ──►

ReAct ──► Plan-and-Execute ──► Reflection（可叠加） ──► Tree-of-Thought
 (低)        (中)                 (中，迭代)              (高)
```

---

### 模式 1: ReAct (Reasoning + Acting)

| 维度 | 内容 |
|------|------|
| 原理 | 模型交替产生 **Thought（推理）** → **Action（行动/工具调用）** → **Observation（观察结果）** 的循环。推理引导下一步行动，行动返回的外部观察又反哺下一步推理，直到得出最终答案。核心贡献：将"推理"与"行动"两种能力协同，弥补纯推理缺乏外部信息、纯行动缺乏规划的缺陷。 |
| 论文引用 | Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models." arXiv:2210.03629 (2022). https://arxiv.org/abs/2210.03629 |
| 适用场景 | 需要调用外部工具获取信息的任务（多跳问答、事实核查）；需要与环境交互的决策任务；信息随时间变化的查询（如实时搜索）。 |
| 不适用 | 纯推理任务（数学证明）且无需外部信息时，行动环节无收益；步骤完全确定的任务（无需动态决策）。 |
| 成本 | 中等（每步一次 LLM 调用 + 一次工具调用，步数 = 迭代轮数）。 |
| 关键风险 | 行动链可能陷入循环（反复调用同一工具）；Thought 过多导致延迟增加。 |

**ReAct 循环结构**：

```
Thought 1: 我需要先查 X 的信息 →
Action 1: search("X") →
Observation 1: X 是... →
Thought 2: 现在我知道了 X，还需要查 Y →
Action 2: search("Y") →
Observation 2: Y 是... →
Thought 3: 综合以上信息，答案是... →
Action: Finish(最终答案)
```

---

### 模式 2: Plan-and-Execute (规划-执行)

| 维度 | 内容 |
|------| 原理 | 分两阶段：(1) **Plan（规划）**：模型先将复杂任务分解为有序的子步骤列表；(2) **Execute（执行）**：逐步执行每个子步骤（可调用工具或子 Agent）；(3) **Re-plan（重规划）**：执行结果与预期不符时，可重新规划剩余步骤。核心贡献：将"全局规划"与"局部执行"解耦，避免 ReAct 式的短视（每步只看眼前）。 |
|------|------|
| 论文引用 | 作为 Agent 架构模式，Plan-and-Execute 在 LangChain/LangGraph 等框架中被广泛实现。相关的提示词层面研究见 Wang, L. et al. "Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models." arXiv:2305.04091 (2023). https://arxiv.org/abs/2305.04091 。注意：Plan-and-Solve Prompting（提示词技术）与 Plan-and-Execute Agent（架构模式）是相关但不同的概念。 |
| 适用场景 | 步骤较多、需要全局视野的复杂任务（多步骤研究、长流程自动化）；需要可审计的执行计划（每步可追溯）；子任务间有依赖关系。 |
| 不适用 | 步骤无法预先规划、需高度动态响应的任务（更适合 ReAct）；简单任务（规划开销不划算）。 |
| 成本 | 中等（1 次规划调用 + N 次执行调用 + 可能的重规划调用）。 |
| 关键风险 | 初始计划质量决定整体上限；若计划过于僵化，遇到意外无法适应。 |

**Plan-and-Execute 结构**：

```
[Planner Agent]
  输入: 用户任务
  输出: 步骤列表 [step1, step2, step3, ...]

[Executor Agent] (循环)
  for each step:
    执行 step_i → 得到 result_i
    if result_i 异常:
      [Re-planner] 基于已完成步骤和异常 → 修订剩余计划

[Final Answer]
  汇总所有 step 结果 → 输出
```

---

### 模式 3: Reflection (反思)

| 维度 | 内容 |
|------|------|
| 原理 | Agent 在完成任务后（或尝试失败后），对自身的执行过程进行 **自我评估（Self-Reflection）**，生成语言形式的反思反馈（"哪里做错了""应该如何改进"），并将反思存入记忆，在下一次尝试中利用该反馈改进。核心贡献：不更新模型权重，仅通过"语言反馈"实现类似强化学习的迭代改进，因此称为"verbal reinforcement learning"。 |
| 论文引用 | Shinn, N. et al. "Reflexion: Language Agents with Verbal Reinforcement Learning." arXiv:2303.11366 (2023). https://arxiv.org/abs/2303.11366 |
| 适用场景 | 可重试的任务（代码生成+测试、解题、写作迭代）；有客观反馈信号的场景（测试是否通过、答案是否正确）；需要从失败中改进的多轮任务。 |
| 不适用 | 无法重试的一次性任务；无反馈信号可评估的场景；对延迟敏感的实时场景（反思需要额外轮次）。 |
| 成本 | 中高（每次尝试 + 1 次反思调用，可能多轮迭代）。 |
| 关键风险 | 反思可能"自我确认"错误（若模型无法识别自身错误）；反思过多但无实质改进导致浪费 Token。 |

**Reflection 循环结构**：

```
Attempt 1:
  Actor: 生成解决方案 → 执行 → 结果: 失败（测试未通过）
  Evaluator: 评估 → 反馈: "函数未处理空列表输入"

Attempt 2:
  Actor (利用反思记忆): 生成改进方案 → 执行 → 结果: 失败（边界值错误）
  Evaluator: 评估 → 反馈: "未考虑负数索引"

Attempt 3:
  Actor (利用全部反思记忆): 生成方案 → 执行 → 结果: 成功

Final Answer: 输出 Attempt 3 的方案
```

---

### 模式 4: Tree-of-Thought (ToT) / 思维树

| 维度 | 内容 |
|------|------|
| 原理 | 将推理过程组织为 **树形结构**：在每个推理节点生成多个候选"思考"（分支），用评估函数（LLM 自评或外部评估）对每个分支打分，通过搜索算法（BFS/DFS）探索最有前景的路径，可回溯放弃死路。核心贡献：突破 CoT 的线性思维限制，允许"探索多条路径 + 自我评估 + 回溯"，适用于需要"前瞻"和"搜索"的复杂问题。 |
| 论文引用 | Yao, S. et al. "Tree of Thoughts: Deliberate Problem Solving with Large Language Models." arXiv:2305.10601 (2023). https://arxiv.org/abs/2305.10601 |
| 适用场景 | 需要探索多种可能性的问题（24 点游戏、创意写作、填字游戏、策略规划）；解空间大且需要搜索的任务；有明确评估标准可判断中间状态优劣的场景。 |
| 不适用 | 简单线性推理任务（CoT 足够，ToT 过度设计）；对延迟极度敏感的场景（树搜索需大量 LLM 调用）；无明确评估标准的开放式任务。 |
| 成本 | 高（每个节点生成 K 个候选 + 评估 + 搜索，总调用数 = 节点数 × 分支数）。 |
| 关键风险 | 评估函数质量决定搜索效果；分支因子和搜索深度需仔细设定，否则成本爆炸。 |

**ToT 结构**：

```
                    [根问题]
                   /    |    \
            候选A    候选B    候选C     ← 生成 K 个候选思考
           [评估]   [评估]   [评估]     ← 打分
            0.8      0.3      0.6
           /  \               |
       A1    A2              C1          ← 保留高分分支，继续展开
     [评估][评估]           [评估]
      0.9   0.4             0.7
       |
    最终答案 (沿最高分路径回溯)
```

---

## 组合规则 / Combination Rules

四种模式并非互斥，可按以下规则组合：

| 组合 | 方式 | 效果 | 成本 |
|------|------|------|------|
| **ReAct + Reflection** | 在 ReAct 循环失败后触发反思，将反思存入记忆供下一轮 ReAct 使用 | 提升工具调用策略的迭代改进 | 中高 |
| **Plan-and-Execute + ReAct** | Planner 规划步骤，每个步骤的 Executor 内部用 ReAct 执行 | 兼顾全局视野与局部动态决策 | 中 |
| **Plan-and-Execute + Reflection** | 执行后反思计划质量，改进重规划能力 | 提升计划的适应性 | 中高 |
| **ToT + Reflection** | ToT 的评估函数用 Reflection 机制自评并改进 | 提升分支评估质量 | 高 |
| **ToT + ReAct** | ToT 的每个叶子节点用 ReAct 执行行动 | 在搜索空间中结合外部信息 | 高 |

**组合原则**：
1. **先确定主模式**：根据任务特征选 1 个主推理模式。
2. **按需叠加 Reflection**：Reflection 是"正交增强"，几乎可与任何主模式叠加，但需有可重试条件和反馈信号。
3. **成本守恒**：每叠加一层，Token 与延迟近似翻倍。组合不超过 2 层（主模式 + 1 增强）。
4. **避免 ToT + Plan-and-Execute + Reflection 三层叠加**：除非任务极复杂且预算充足，否则成本不可控。

---

## 选型矩阵 / Selection Matrix

| 评估维度 | ReAct | Plan-and-Execute | Reflection | ToT |
|----------|-------|-------------------|------------|-----|
| **推理深度** | 浅（逐步） | 中（全局规划） | 中（迭代改进） | 深（树搜索） |
| **外部工具依赖** | 高（核心依赖） | 中（执行阶段使用） | 低（可选） | 低（主要用于推理） |
| **延迟** | 中 | 中 | 高（多轮） | 高（多分支） |
| **Token 成本** | 中 | 中 | 中高 | 高 |
| **可解释性** | 高（Thought 可读） | 高（计划可审计） | 中（反思可读） | 中（树结构复杂） |
| **可重试性** | 否（单链） | 否（单计划） | 是（核心特性） | 是（可回溯） |
| **最佳任务类型** | 信息检索型问答 | 多步骤流程自动化 | 代码生成/解题迭代 | 策略搜索/创意探索 |
| **实现复杂度** | 低 | 中 | 中 | 高 |
| **框架支持** | LangChain/LangGraph 原生 | LangGraph Plan-and-Execute | LangGraph/Reflexion | 自实现或 ToT 库 |

### 选型决策树 / Selection Decision Tree

```
Q1: 任务是否需要调用外部工具获取信息？
├─ 是 ──► Q2
└─ 否 ──► Q3

Q2: 步骤是否可预先规划？
├─ 是（多步骤流程）──► Plan-and-Execute（+ ReAct 执行子步骤）
└─ 否（需动态决策）──► ReAct

Q3: 任务是否可重试且有明确反馈信号？
├─ 是（代码/解题/可验证）──► Reflection（+ CoT 或 ReAct 作为基础执行器）
└─ 否 ──► Q4

Q4: 是否需要探索多种可能性并择优？
├─ 是（策略搜索/创意）──► Tree-of-Thought (ToT)
└─ 否（线性推理即可）──► Chain-of-Thought (CoT)（见 prompt-patterns.md）

Q5: 是否需要从失败中改进？（正交增强）
└─ 是 ──► 在上述选择上叠加 Reflection
```

---

## Reasoning Depth Switching (推理深度显式切换)

对应 AGENTS.md §4 新增规则。

根据任务复杂度显式设定推理深度：
| 深度 | 适用场景 | 示例 |
|------|---------|------|
| Low/Minimal | 格式转换、数据提取、简单查询 | JSON 解析、字段提取 |
| Medium | 常规编码、文档撰写、代码审查 | API 实现、测试编写 |
| High/Thinking | 架构重构、复杂逻辑、方案设计 | 系统迁移、算法设计 |

推理深度必须在智能体配置中显式声明，不隐式依赖模型自行决定。

---

## 模板示例 / Template Examples

### ReAct Prompt 模板

```text
你是一个使用 ReAct 模式的 Agent。请严格按照以下格式交替输出：

Thought: <你的推理，决定下一步行动>
Action: <工具名称>
Action Input: <工具输入参数>
Observation: <工具返回结果>
...（重复 Thought/Action/Observation 循环）
Thought: 我现在有足够信息回答了
Final Answer: <最终答案>

可用工具:
- search(query): 搜索网络信息
- calculate(expression): 计算数学表达式

问题: {用户问题}
```

### Plan-and-Execute Prompt 模板

```text
# Planner 提示词
你是一个任务规划器。请将以下任务分解为清晰的、可执行的步骤列表。
每个步骤应是一个独立的、可验证的子任务。

任务: {用户任务}

请输出步骤列表（JSON 数组）:
[
  {"step": 1, "description": "...", "tool": "..."},
  {"step": 2, "description": "...", "tool": "..."}
]

# Executor 提示词（对每个步骤）
请执行以下步骤，使用可用工具完成任务。
当前步骤: {step_description}
已完成步骤结果: {previous_results}
```

### Reflection Prompt 模板

```text
# Evaluator/Reflector 提示词
你是一个评估器。请评估上一次尝试的结果，并给出改进建议。

任务: {任务描述}
上次尝试: {attempt}
执行结果: {result}
是否成功: {success/failure}

请输出:
1. 评估: 哪里做得好，哪里有问题
2. 反思: 具体的改进方向
3. 改进建议: 下次尝试应该注意什么

改进建议将作为记忆供下次尝试参考。
```

### ToT Prompt 模板（核心组件）

```text
# Thought Generator（生成候选思考）
问题: {problem}
当前状态: {current_state}
请生成 {K} 个可能的下一步思考（各自独立、有差异）:

# State Evaluator（评估状态）
问题: {problem}
候选状态: {candidate_state}
请评估此状态的前景（1-10 分），并说明理由:

# Search Controller（搜索控制）
基于评估分数，保留分数最高的 {N} 个状态，继续展开。
若某状态已是终态，记录为候选答案。
最终从所有候选答案中选择最优。
```

---

## 常见陷阱 / Common Pitfalls

1. **ReAct 陷入循环**：模型反复调用同一工具、获得相同观察，陷入死循环。应设置最大迭代次数与重复检测机制。
2. **Plan-and-Execute 计划过于僵化**：初始计划在第一步就出错，但执行器仍机械执行后续步骤。应加入重规划（re-plan）触发条件。
3. **Reflection 无实质改进**：模型反思后只是重复"要更仔细"等空话，未给出具体可操作的改进。反思提示词应要求具体的、可操作的改进点。
4. **Reflection 自我确认**：模型无法识别自身错误，反思后"确认"错误答案正确。应尽可能引入外部反馈信号（如测试结果）而非纯自评。
5. **ToT 成本爆炸**：分支因子（K）和搜索深度（D）设置过大，调用次数 = K^D 指数增长。应严格限制 K（通常 3–5）和 D（通常 2–4）。
6. **ToT 评估函数不可靠**：LLM 自评打分不稳定，导致搜索方向错误。可结合外部确定性评估（如规则检查）提升可靠性。
7. **忽视论文与实现的差异**：论文中的理想效果在工程实现中受模型能力、工具质量、延迟约束影响而打折。应以实际测试为准，论文结果为参考上限。
8. **混淆 Plan-and-Solve Prompting 与 Plan-and-Execute Agent**：前者是提示词技术（单次调用中规划+求解），后者是 Agent 架构（多阶段、可调用工具、可重规划）。

---

## 检查清单 / Checklist

### 模式选择 / Pattern Selection
- [ ] 已确认任务是否需要外部工具（决定 ReAct vs 纯推理模式）。
- [ ] 已确认步骤是否可预先规划（决定 Plan-and-Execute vs ReAct）。
- [ ] 已确认任务是否可重试且有反馈信号（决定是否叠加 Reflection）。
- [ ] 已确认是否需要多路径探索（决定是否用 ToT）。
- [ ] 组合不超过 2 层（主模式 + 1 增强）。

### 论文核实 / Paper Verification
- [ ] ReAct (arXiv:2210.03629) 已通过 arXiv.org 确认。
- [ ] ToT (arXiv:2305.10601) 已通过 arXiv.org 确认。
- [ ] Reflexion (arXiv:2303.11366) 已通过 arXiv.org 确认。
- [ ] Plan-and-Solve (arXiv:2305.04091) 已通过 arXiv.org 确认。
- [ ] 已区分 Plan-and-Solve Prompting（提示词技术）与 Plan-and-Execute Agent（架构模式）。

### 工程实现 / Engineering
- [ ] 已设置 ReAct/Plan-and-Execute 的最大迭代/步数上限。
- [ ] 已为 Reflection 设置最大重试次数与终止条件。
- [ ] 已为 ToT 设置分支因子 K 与搜索深度 D 的上限。
- [ ] 已在关键路径加入循环检测/重复检测机制。
- [ ] 已评估组合模式的 Token 成本与延迟，在可接受范围内。

### 测试 / Testing
- [ ] 已用真实任务测试所选模式的端到端效果。
- [ ] 已测试异常路径（工具失败、超时、循环）。
- [ ] 已对比基线（如纯 CoT）验证所选模式的增益是否值得成本。

## 进阶：12 项高级架构模式 / Advanced: 12 Architecture Patterns

> 本文档的推理模式选型在 `advanced-patterns.md` 中有进一步的架构扩展：
> - **模式 10（Reflexion 自我反思机制）**：在 Reflection 模式基础上的进阶——失败时三步循环（分析原因 → 调整策略 → 重试），含反思记忆（失败原因存入 memory）与最大重试次数限制。与步骤检查点的区别：检查点是预防性中断，Reflexion 是失败后的纠正性反思。来源 Shinn et al. "Reflexion" 2023 (arXiv:2303.11366)。
