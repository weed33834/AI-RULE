# prompt-patterns.md — 提示词模式库
# Prompt Pattern Library

---

## 一句话描述 / One-line Description

> 本文档收录经过论文验证的七种提示词技术，按"认知负荷从低到高"排列，每种附真实原理、适用场景与可复用示例，供按需组合使用。
>
> This document collects seven prompt techniques validated by research papers, ordered by cognitive load from low to high, each with real principles, applicable scenarios, and reusable examples for on-demand composition.

---

## 适用场景 / Applicable Scenarios

- **提示词工程阶段**：为某类任务选择合适的提示词技术。
- **效果调优阶段**：当前提示词效果不佳，需要升级到更强技术（如从 Zero-shot 升级到 CoT 或 Self-Consistency）。
- **成本权衡阶段**：在准确率与 Token 消耗之间做取舍（如 Self-Consistency 需多次采样）。
- **技术评审阶段**：向团队说明"为什么用这个技术"，提供论文依据。

---

## 核心方法论 / Core Methodology

提示词技术按 **推理深度** 与 **采样次数** 两个维度分类：

```
                    单次采样                    多次采样
              ┌──────────────────┬──────────────────┐
  无推理步骤   │ Zero-shot        │                  │
              │ Few-shot         │                  │
              ├──────────────────┼──────────────────┤
  有推理步骤   │ Chain-of-Thought │ Self-Consistency │
              │ CoVe             │                  │
              │ ToT (在推理模式库)│                  │
              └──────────────────┴──────────────────┘

  结构化输出：Structured Output（正交于上述技术，可叠加）
  元层级：Meta-prompting（用 LLM 生成/优化上述提示词）
```

> **组合原则**：技术可叠加，但每增加一层都会增加 Token 成本与延迟。从最简方案开始，仅在验证效果不足时升级。

---

### 模式 1: Zero-shot / 零样本提示

| 维度 | 内容 |
|------|------|
| 原理 | 不提供任何示例，直接用指令描述任务，依赖模型预训练知识完成任务。 |
| 论文依据 | 概念源于 GPT-3 论文"Language Models are Few-Shot Learners"(Brown et al., 2020, arXiv:2005.14165)，其中定义了 zero-shot 设定。 |
| 适用场景 | 简单分类、翻译、摘要等模型已充分学习过的任务；快速验证可行性。 |
| 不适用 | 需要特定输出格式、需要特定推理范式、任务定义模糊的场景。 |
| 成本 | 最低（单次调用，无示例 Token）。 |
| 示例 | 见下方模板。 |

### 模式 2: Few-shot / 少样本提示

| 维度 | 内容 |
|------|------|
| 原理 | 在提示词中提供少量（通常 1–5 个）输入-输出示例，通过"上下文学习"(in-context learning) 引导模型模仿示例的模式。 |
| 论文依据 | GPT-3 论文 (Brown et al., 2020, arXiv:2005.14165) 系统验证了 few-shot 的有效性。 |
| 适用场景 | 需要特定输出格式、需要隐式定义任务边界、分类标签不直观的任务。 |
| 不适用 | 示例本身会引入偏差；任务需要深度推理而非模式匹配时效果有限。 |
| 成本 | 中等（示例占用 Token）。 |
| 注意 | 示例顺序和选择会影响结果；示例应覆盖目标分布的多样性。 |
| 示例 | 见下方模板。 |

### 模式 3: Chain-of-Thought (CoT) / 思维链

| 维度 | 内容 |
|------|------|
| 原理 | 引导模型在给出最终答案前，先输出中间推理步骤。研究表明这能显著提升模型在算术、常识、符号推理等任务上的表现。可通过在 Few-shot 示例中展示推理过程（CoT prompting）或在指令中加"Let's think step by step"（Zero-shot CoT）触发。 |
| 论文依据 | "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (Wei et al., 2022, arXiv:2201.11903)；Zero-shot CoT 见 "Large Language Models are Zero-Shot Reasoners" (Kojima et al., 2022, arXiv:2205.11916)。 |
| 适用场景 | 多步数学推理、逻辑推导、复杂问答、需要可解释推理过程的场景。 |
| 不适用 | 简单事实问答（增加噪声无收益）；对延迟敏感的实时场景。 |
| 成本 | 中高（推理步骤增加输出 Token）。 |
| 示例 | 见下方模板。 |

### 模式 4: Self-Consistency / 自洽性

| 维度 | 内容 |
|------|------|
| 原理 | 在 CoT 基础上，对同一问题采样多条不同推理路径（通过提高 temperature 产生多样化输出），然后对最终答案取多数投票（majority vote）。核心思想：正确答案更可能在多条路径中一致出现。 |
| 论文依据 | "Self-Consistency Improves Chain of Thought Reasoning in Language Models" (Wang et al., 2022, arXiv:2203.11171)。 |
| 适用场景 | 答案可枚举/可比较的任务（数学题、多选题、分类）；对准确率要求高、可接受多次采样的场景。 |
| 不适用 | 开放式生成（如创意写作，无唯一正确答案，无法投票）；对延迟/成本极度敏感的场景。 |
| 成本 | 高（需 N 次采样，通常 N=5~40）。 |
| 示例 | 见下方模板。 |

### 模式 5: Chain-of-Verification (CoVe) / 验证链

| 维度 | 内容 |
|------|------|
| 原理 | 模型先生成初始草稿回答，然后自主规划验证问题（verification questions）来检查草稿中的事实，逐一回答验证问题，最后基于验证结果生成修订后的回答。核心目标：减少幻觉。 |
| 论文依据 | "Chain-of-Verification Reduces Hallucination in Large Language Models" (Dhuliawala et al., 2023, arXiv:2309.11495)。 |
| 适用场景 | 事实性问答、列表式问答（如"列出 X 的所有 Y"）、闭卷 QA；幻觉风险高的场景。 |
| 不适用 | 创意生成、主观观点类任务；对延迟敏感的场景（需多轮调用）。 |
| 成本 | 高（草稿 + 验证问题生成 + 逐个回答 + 修订，共多轮调用）。 |
| 示例 | 见下方模板。 |

### 模式 6: Structured Output / 结构化输出

| 维度 | 内容 |
|------|------|
| 原理 | 通过约束模型输出为结构化格式（如 JSON、XML、表格），使输出可被程序解析。实现方式有两种：(1) 提示词层面要求格式 + 提供 schema 示例；(2) API 层面强制约束——如 OpenAI 的 Structured Outputs 功能（通过 `response_format` 参数 + JSON Schema 强制模型输出符合 schema 的 JSON）。 |
| 论文/文档依据 | OpenAI Structured Outputs 官方文档：https://platform.openai.com/docs/guides/structured-outputs 。提示词层面的结构化输出是工程实践，无单一论文。 |
| 适用场景 | 需要程序消费模型输出的任何场景（Agent 工具调用、数据抽取、流水线编排）。 |
| 不适用 | 开放式对话、创意写作。 |
| 成本 | 低额外成本（主要是 schema 描述 Token）。 |
| 注意 | API 层面的强制约束（Structured Outputs）比纯提示词约束更可靠；纯提示词方式模型仍可能偏离格式。 |
| 示例 | 见下方模板。 |

### 模式 7: Meta-prompting / 元提示

| 维度 | 内容 |
|------|------|
| 原理 | 使用 LLM 来生成、优化或编排提示词本身。即"用提示词写提示词"。包括：让模型根据任务描述自动生成提示词、让模型批判并改进现有提示词、让多个专家角色协作生成提示词等。 |
| 论文依据 | "Meta-Prompting: Enhancing Language Models with Task-Agnostic Scaffolding" (Suzgun & Kalai, 2024, arXiv:2311.11482)（需验证确切作者与编号，使用前请查阅 arXiv）。 |
| 适用场景 | 提示词工程自动化、批量生成提示词、不确定如何写提示词时让模型辅助。 |
| 不适用 | 已有成熟提示词且无需迭代；对提示词可解释性要求极高的场景（元提示生成的提示词可能难以理解）。 |
| 成本 | 中等（额外的元层调用）。 |
| 示例 | 见下方模板。 |

---

## 决策树 / Decision Tree

```
Q1: 任务是否需要程序解析输出？
├─ 是 ──► 叠加 Structured Output，继续 Q2
└─ 否 ──► Q2

Q2: 任务是否需要多步推理？
├─ 否（简单分类/翻译/摘要）──► Q3
└─ 是（数学/逻辑/多跳问答）──► Q4

Q3: 模型是否已充分理解任务格式？
├─ 是 ──► Zero-shot（最简）
└─ 否 ──► Few-shot（加示例对齐格式）

Q4: 是否需要降低幻觉 / 提高事实准确性？
├─ 是（事实性问答）──► Chain-of-Verification (CoVe)
└─ 否 ──► Q5

Q5: 答案是否可枚举/可投票，且预算允许多次采样？
├─ 是 ──► Self-Consistency（CoT + 多次采样投票）
└─ 否 ──► Chain-of-Thought (CoT)（单次推理链）

Q6: 是否不确定如何写好提示词？
└─ 是 ──► 在上述选择基础上，用 Meta-prompting 辅助生成/优化提示词
```

---

## 模板示例 / Template Examples

### Zero-shot 示例

```text
将以下句子翻译为英文：

"今天天气很好，适合出门散步。"
```

### Few-shot 示例

```text
将以下情感分类为"正面"或"负面"：

示例：
句子：这家餐厅的服务态度太差了。
分类：负面

句子：产品质量超出预期，非常满意。
分类：正面

现在请分类：
句子：价格偏贵，但物有所值。
分类：
```

### Chain-of-Thought (CoT) 示例 — Few-shot CoT

```text
问答以下数学题，请展示推理过程：

问题：食堂里有 23 个苹果，用掉 20 个做午餐，又买了 6 个，现在有多少？
推理：食堂一开始有 23 个苹果。用掉 20 个后剩下 23 - 20 = 3 个。
又买了 6 个，所以现在有 3 + 6 = 9 个。
答案：9

问题：停车场有 15 辆车，开走 8 辆，又开来 12 辆，现在有多少？
推理：
```

### Chain-of-Thought (CoT) 示例 — Zero-shot CoT

```text
问题：一个数加上 5 等于 12，这个数的 3 倍是多少？

让我们一步一步思考。
```

### Self-Consistency 示例（伪代码流程）

```text
# Self-Consistency 流程（需多次调用 API）
问题："一个班有 32 个学生，男生比女生多 4 人，女生有多少人？"

# 对同一问题用较高 temperature 采样 N=5 次，各得到一条推理链：
路径 1: 男生 + 女生 = 32，男生 = 女生 + 4 → 2*女生 + 4 = 32 → 女生 = 14
路径 2: 女生 = x, 男生 = x+4, x + x+4 = 32, 2x = 28, x = 14
路径 3: ... → 14
路径 4: ... → 13（错误路径）
路径 5: ... → 14

# 多数投票：14 出现 4 次，13 出现 1 次
最终答案：14
```

> 注意：上述为流程说明，实际需通过 API 参数（如 temperature > 0、n > 1 或多次调用）实现。

### Chain-of-Verification (CoVe) 示例（流程）

```text
# 步骤 1: 生成草稿回答
问题："列出太阳系中距离太阳最近的 3 颗行星。"
草稿："水星、金星、地球。"

# 步骤 2: 模型自主规划验证问题
验证问题 1: 水星是距离太阳最近的行星吗？
验证问题 2: 金星是距离太阳第二近的行星吗？
验证问题 3: 地球是距离太阳第三近的行星吗？

# 步骤 3: 逐一回答验证问题
答 1: 是，水星是距离太阳最近的行星。
答 2: 是，金星是第二近的。
答 3: 是，地球是第三近的。

# 步骤 4: 基于验证结果生成修订回答
最终回答："距离太阳最近的 3 颗行星依次是：水星、金星、地球。"
```

### Structured Output 示例 — 提示词层面

```text
请从以下文本中提取人物信息，严格按 JSON 格式输出，不要输出其他内容。

输出格式：
{
  "name": "姓名",
  "age": 年龄（整数，未知则 null）,
  "occupation": "职业"
}

文本：张三今年 35 岁，是一名软件工程师。
```

### Structured Output 示例 — OpenAI API 层面（Structured Outputs）

```json
// 使用 response_format 参数强制 JSON Schema 约束（OpenAI Structured Outputs）
{
  "type": "json_schema",
  "json_schema": {
    "name": "person_info",
    "strict": true,
    "schema": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "age": { "type": ["integer", "null"] },
        "occupation": { "type": "string" }
      },
      "required": ["name", "age", "occupation"],
      "additionalProperties": false
    }
  }
}
```

> 参考来源：OpenAI Structured Outputs 官方文档 https://platform.openai.com/docs/guides/structured-outputs

### Meta-prompting 示例

```text
你是一位提示词工程专家。请根据以下任务描述，生成一个高质量的提示词。

任务描述：我需要一个能从用户输入的中文文本中提取关键事件信息
（时间、地点、人物、事件）的提示词。输出需为 JSON 格式。

要求：
1. 提示词应包含清晰的角色定义
2. 包含至少 2 个 few-shot 示例
3. 包含输出格式说明
4. 包含边界情况处理（如信息缺失）

请直接输出生成的提示词：
```

---

## 常见陷阱 / Common Pitfalls

1. **盲目堆叠技术**：对简单任务也用 CoT + Self-Consistency，导致成本与延迟暴增而准确率无明显提升。应从最简方案开始。
2. **Few-shot 示例有偏**：示例只覆盖一种情况，导致模型对其他情况表现下降。示例应覆盖输入分布的多样性。
3. **Self-Consistency 用于开放式生成**：对没有唯一正确答案的任务（如写诗）做多数投票无意义。仅适用于答案可枚举/可比较的任务。
4. **混淆提示词层与 API 层的结构化输出**：纯提示词要求 JSON 仍可能被模型违反；需要可靠结构化时应使用 API 层面的强制约束（如 OpenAI Structured Outputs）。
5. **CoT 推理链被截断**：复杂问题推理链过长，触发 max_tokens 截断，导致只有过程没有答案。应适当调大 max_tokens 或分段推理。
6. **CoVe 验证问题与原始问题同源**：验证问题仍由同一模型生成，若模型本身知识有误，验证环节可能"自我确认"错误。CoVe 降幻觉但非消除幻觉。
7. **Meta-prompting 生成的提示词未经验证直接上线**：模型生成的提示词可能包含幻觉性指令或不合理约束，必须人工审查与测试。

---

## 检查清单 / Checklist

### 技术选择 / Technique Selection
- [ ] 已确认任务是否需要多步推理（决定是否用 CoT）。
- [ ] 已确认答案是否可枚举/可投票（决定是否适用 Self-Consistency）。
- [ ] 已确认是否需要程序解析输出（决定是否叠加 Structured Output）。
- [ ] 已从最简方案（Zero-shot）开始验证，仅在不足时升级。

### 论文与来源核实 / Source Verification
- [ ] 引用的 arXiv 编号已通过 arXiv.org 二次确认。
- [ ] OpenAI Structured Outputs 用法已对照官方文档核实。
- [ ] 标注"需验证"的信息已在使用前确认。

### 成本与效果 / Cost & Effectiveness
- [ ] 已评估所选技术的 Token 成本与延迟影响。
- [ ] Self-Consistency 的采样次数 N 已根据预算设定（非默认无限大）。
- [ ] CoVe 的多轮调用延迟已在可接受范围内。

### 测试 / Testing
- [ ] 已准备测试集验证提示词效果。
- [ ] 已测试边界情况（输入缺失、格式异常）。
- [ ] Meta-prompting 生成的提示词已经人工审查与测试。
