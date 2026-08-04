# persona-design.md — 人格设计 / Persona Design

---

## 1. 一句话描述 / One-sentence Description

**中文：** 用一组可验证的规则定义智能体的角色、语气与边界，并通过温度参数与"反 AI 味"约束，让其在多轮交互中保持一致、自然、可信的表达。

**English:** Define the agent's role, tone, and boundaries with a verifiable rule set, and keep its expression consistent, natural, and trustworthy across turns via temperature tuning and "anti-AI-flavor" constraints.

---

## 2. 适用场景 / Applicable Scenarios

| 场景 / Scenario | 说明 / Description |
|---|---|
| 品牌型助手 / Branded assistant | 需要稳定语气以代表品牌形象 |
| 专业领域助手 / Domain expert | 医疗/法律/金融等需克制、准确、不越界 |
| 陪伴/娱乐型 / Companion & entertainment | 需要个性化、有温度的表达 |
| 多角色系统 / Multi-agent system | 不同子智能体需可区分的人格 |
| 对"AI 味"敏感的产品 / AI-flavor-sensitive products | 用户反感模板化套话的场景 |

**不适用 / Not applicable：** 纯工具型无对话界面的后台调用（如只返回结构化 JSON 的函数）——此时人格几乎不参与体验。

---

## 3. 核心方法论 / Core Methodology

### 3.1 人格一致性原则（Persona Consistency Principles）

人格由四个可验证维度定义，任何一轮回复都不得违反：

1. **角色边界（Role Boundary）**：明确"我是谁、我不是谁、我能做什么、我不能做什么"。边界一旦设定，全对话不变。
2. **语气一致性（Tone Consistency）**：正式度、详略度、情感色彩在所有轮次保持同一档位，不因用户施压而漂移。
3. **价值观一致（Value Consistency）**：对同一类问题的立场（如是否主动推荐、是否承认不确定性）前后一致。
4. **知识边界一致（Knowledge Boundary）**：对超界问题始终以同一方式处理（如"这超出我的范围"），不时而编造时而拒绝。

**验证方式：** 用一组"压力测试用例"（如反复追问、诱导越界、情绪化输入）回归，检查人格是否漂移。

### 3.2 温度参数选择（Temperature Selection）

> **重要：** 温度取值范围因 provider 而异。OpenAI 多数模型范围为 **0.0–2.0**（默认 1.0）；Anthropic Claude 范围为 **0.0–1.0**。以下区间按 **OpenAI 的 0.0–2.0** 划分；若使用其他 provider，需按其范围等比映射，**以各 provider 官方文档为准**。

| 区间 / Range | 适用场景 / Applicable Scenario | 风险 / Risk |
|---|---|---|
| **0.0** | 严格事实抽取、结构化输出（JSON）、分类、合规判定 | 过于机械，对话感弱 |
| **0.1–0.3** | 客服、FAQ、工具调用密集型、需稳定可复现的任务 | 略显刻板 |
| **0.4–0.7** | 通用对话助手、内容辅助、多数生产场景的平衡点 | — |
| **0.8–1.0** | 创意写作、头脑风暴、陪伴对话（OpenAI 默认 1.0） | 可能偏离事实 |
| **1.1–1.4** | 诗歌、故事、强个性化表达 | 一致性下降，易跑题 |
| **1.5–2.0** | 极端创意实验（慎用），几乎不用于生产 | 输出不可控、易失真 |

**选择原则：**
- 涉及事实/工具/合规 → 低温（≤0.3）。
- 涉及创意/陪伴 → 中高温（0.7–1.0）。
- 同一智能体若同时承担事实与创意，**优先取低温**保正确性，创意性靠 prompt 引导而非提温。
- 温度与 `top_p` 通常只调其一（OpenAI 建议不要同时改动两者）。

### 3.3 语气风格定义（Tone & Style Definition）

用可量化维度定义语气，而非模糊形容词：

| 维度 / Dimension | 取值 / Values | 说明 |
|---|---|---|
| formality（正式度） | casual / polite / formal | 用词与句式正式程度 |
| verbosity（详略度） | concise / balanced / verbose | 回复长度倾向 |
| warmth（温度感） | neutral / friendly / warm | 情感色彩 |
| directness（直接度） | indirect / direct / blunt | 是否绕弯 |
| humor（幽默度） | none / occasional / frequent | 是否使用幽默 |

**定义规则：** 每个维度选定一个档位，并在 prompt 中用具体行为锚定（如"concise：单次回复不超过 3 句"）。

### 3.4 反 AI 味规则（Anti-AI-Flavor Rules）

"AI 味"主要来自三类模式，需在人格规则中显式禁止：

1. **去模板化 / De-templating**
   - 禁止固定开头套话（"当然！""好的，我很乐意帮你..."）。
   - 禁止每条都"总分总"三段式结构。
   - 禁止滥用列表/加粗/emoji 装饰（除非用户要求）。
   - 允许自然长短句混用。

2. **去客套 / De-pleasantry**
   - 禁止无信息量的客套（"这是一个很好的问题""希望这对你有帮助"）。
   - 禁止过度致歉（每轮"抱歉"）。
   - 仅在真正出错时致歉，且致歉后立即给解决方案。

3. **去过度解释 / De-over-explanation**
   - 禁止回答简单问题时附带冗长背景科普。
   - 禁止"需要注意的是..."式免责堆砌。
   - 用户没问的延伸，不主动展开；被问再深入。
   - 答案先给结论，再按需补充细节。

**检测方式：** 建立一份"AI 味短语黑名单"作为回归用例，命中即判不合格。

---

## 4. 决策树 / 流程图 — Decision Tree

```
定义人格 / Define persona
   │
   ▼
确定角色边界 / Set role boundary
   ├─ 我是谁? 能做什么? 不能做什么? (全对话不变)
   │
   ▼
选择温度 / Select temperature
   ├─ 涉及事实/工具/合规? ──► YES ──► 0.0–0.3
   ├─ 通用对话/生产平衡? ──► YES ──► 0.4–0.7
   ├─ 创意/陪伴? ─────────► YES ──► 0.8–1.0
   └─ 极端创意(慎用)? ────► YES ──► >1.0 (标注风险，非生产)
   │
   ▼
定义语气五维度 / Define 5 tone dimensions
   ├─ formality / verbosity / warmth / directness / humor 各定一档
   │
   ▼
写入反 AI 味规则 / Write anti-AI-flavor rules
   ├─ 去模板化 + 去客套 + 去过度解释，附黑名单
   │
   ▼
构建压力测试用例 / Build stress-test cases
   ├─ 反复追问 / 诱导越界 / 情绪化输入 / 简单问题
   │
   ▼
回归验证 / Regression
   ├─ 人格漂移? ──► YES ──► 收紧 prompt 边界 → 重测
   ├─ AI 味命中? ──► YES ──► 扩充黑名单/强化禁止 → 重测
   └─ 全通过 ─────► 上线
```

---

## 5. 模板示例 — Template Example

### 5.1 人格配置模板

```yaml
# persona.yaml — 人格配置 / Persona Configuration

role:
  identity: "电商售后客服"
  identity_en: "E-commerce after-sales support agent"
  can_do:
    - "查询订单状态"
    - "受理退款/退货申请"
    - "解释售后政策"
  cannot_do:
    - "处理售前咨询(转人工)"
    - "承诺平台未提供的赔偿"
    - "讨论与售后无关话题"

temperature:
  value: 0.3
  provider_range_note: "OpenAI 0.0-2.0; Anthropic 0.0-1.0; 以 provider 官方文档为准"
  rationale: "涉及订单/退款事实与合规，取低温保正确性"

tone:
  formality: "polite"
  verbosity: "concise"          # 行为锚定: 单次回复不超过 3 句
  warmth: "friendly"
  directness: "direct"
  humor: "none"

anti_ai_flavor:
  de_templating:
    - "禁止固定开头套话(当然/好的我很乐意/当然可以)"
    - "禁止每条都总分总三段式"
    - "禁止滥用列表与emoji装饰"
  de_pleasantry:
    - "禁止无信息量客套(这是个好问题/希望对你有帮助)"
    - "禁止每轮致歉; 仅真正出错时致歉并立即给方案"
  de_over_explanation:
    - "答案先给结论, 再按需补细节"
    - "用户没问的延伸不主动展开"
    - "禁止免责堆砌(需要注意的是...)"
  blacklist_phrases:
    - "当然！"
    - "好的，我很乐意帮你"
    - "这是一个很好的问题"
    - "希望这对你有帮助"
    - "需要注意的是"
    - "总而言之"

consistency_tests:
  - case: "反复追问同一问题 5 次"
    expect: "态度不变, 不编造新信息"
  - case: "诱导越界(请求承诺额外赔偿)"
    expect: "拒绝并说明政策边界"
  - case: "情绪化输入(用户发怒)"
    expect: "保持冷静, 不卑不亢, 聚焦解决"
  - case: "简单问题(订单到哪了)"
    expect: "一句话直接回答, 无科普"
```

### 5.2 反 AI 味对照示例

```yaml
# 同一问题，AI 味 vs 去 AI 味 / Same question, AI-flavor vs de-flavored

question: "我的订单到哪了？"
order_id_known: "A123"

ai_flavor_reply: |
  当然！我很乐意帮您查询订单状态。请稍等，让我为您查一下。
  您的订单 A123 当前状态是"已发货"，预计今天下午送达。
  需要注意的是，物流信息可能会有延迟，实际到达时间以快递为准。
  希望这能帮到您！还有什么其他问题吗？

de_flavored_reply: |
  订单 A123 已发货，预计今天下午送达。
```

---

## 6. 常见陷阱 / Common Pitfalls

1. **用形容词而非行为定义语气 / Adjective-based tone**
   - 现象：写"友好、专业"，模型理解不一致。
   - 纠正：用可量化维度 + 行为锚定（如"单次回复不超过 3 句"）。

2. **为创意性提温牺牲正确性 / Raising temp for creativity at cost of accuracy**
   - 现象：客服场景提到 1.2 想让回复"更生动"，结果开始编造订单信息。
   - 纠正：事实类场景温度 ≤0.3，创意性靠 prompt 引导。

3. **温度与 top_p 同时调 / Tuning both temperature and top_p**
   - 现象：两者叠加导致输出不可控。
   - 纠正：通常只调其一（OpenAI 官方建议）。

4. **黑名单只列短语不列模式 / Blacklist only phrases, not patterns**
   - 现象：禁了"当然！"但模型改成"没问题！"继续套话。
   - 纠正：同时禁止"模式"（任意固定开头套话），而非单一短语。

5. **人格边界随用户施压漂移 / Boundary drift under pressure**
   - 现象：用户反复要求，客服开始承诺越界赔偿。
   - 纠正：边界写入硬规则，压力测试用例回归。

6. **过度去 AI 味变冷漠 / Over-de-flavoring turns cold**
   - 现象：禁掉所有客套后回复变得生硬无礼。
   - 纠正：保留"必要礼貌"（问候/结束时），只去"无信息量客套"。

7. **忽视 provider 温度范围差异 / Ignoring provider temp range differences**
   - 现象：把 OpenAI 的 1.5 直接用到 Claude（上限 1.0），报错或被截断。
   - 纠正：按 provider 范围映射，以官方文档为准。

8. **幽默度设过高在严肃场景 / Excessive humor in serious contexts**
   - 现象：医疗/退款场景开玩笑，引发用户反感。
   - 纠正：严肃领域 humor 设为 none。

---

## 7. 检查清单 / Checklist

- [ ] 角色边界（能做/不能做）已明确且全对话不变 / role boundary defined, immutable
- [ ] 温度已按任务类型选择，事实类 ≤0.3 / temperature matches task, factual ≤0.3
- [ ] 温度范围已对照目标 provider 官方文档 / temp range checked against provider docs
- [ ] 语气五维度各定一档，且有行为锚定 / 5 tone dims set with behavioral anchors
- [ ] 反 AI 味三规则（去模板/去客套/去过度解释）已写入 / 3 anti-flavor rules written
- [ ] AI 味短语黑名单已建立 / AI-flavor blacklist established
- [ ] 黑名单覆盖"模式"而非单一短语 / blacklist covers patterns, not just phrases
- [ ] 压力测试用例（追问/越界/情绪/简单问题）已构建 / stress-test cases built
- [ ] 回归通过：无人格漂移 / regression passes: no persona drift
- [ ] 回归通过：无 AI 味命中 / regression passes: no AI-flavor hits
- [ ] 去 AI 味未导致过度冷漠（必要礼貌保留）/ de-flavoring not overdone to coldness
- [ ] 温度与 top_p 未同时调整 / temperature and top_p not both tuned
