# context-engineering.md — 上下文工程 / Context Engineering

---

## 1. 一句话描述 / One-sentence Description

**中文：** 把有限的上下文窗口当作一种稀缺资源来预算、压缩、保活与溢出治理，确保关键信息（目标、决策、护栏）在任何时刻都留在模型视野内。

**English:** Treat the limited context window as a scarce resource to be budgeted, compressed, kept-alive, and overflow-governed, ensuring critical information (goals, decisions, guardrails) always stays within the model's view.

---

## 2. 适用场景 / Applicable Scenarios

| 场景 / Scenario | 说明 / Description |
|---|---|
| 长任务多轮对话 / Long multi-turn tasks | 任务跨越数十轮，早期信息容易被挤出窗口 |
| 工具密集型智能体 / Tool-heavy agents | 工具描述 + 返回结果占用大量 token |
| 记忆依赖型应用 / Memory-dependent apps | 需要引用用户偏好/历史决策的助手 |
| 受限模型部署 / Constrained-model deployment | 部署在上下文窗口较小的模型上 |
| 成本敏感场景 / Cost-sensitive scenarios | 上下文越长推理成本越高，需要精打细算 |

**不适用 / Not applicable：** 单轮、无状态、无工具的简单问答——此时上下文工程收益有限，直接拼接即可。

---

## 3. 核心方法论 / Core Methodology

### 3.1 预算分配（Budget Allocation）

将上下文窗口按固定比例预算给五类内容。比例是默认起点，应按实际任务动态调整，但**总和必须 ≤ 窗口上限的 90%**（留 10% 安全余量）。

| 预算项 / Budget Item | 默认占比 / Default % | 内容 / Content |
|---|---|---|
| 系统提示 / System prompt | 20% | 人格、角色、全局规则、护栏 |
| 工具描述 / Tool descriptions | 15% | 函数签名、参数 schema、使用说明 |
| 用户输入 / User input | 30% | 当前用户消息 + 本轮附加上下文 |
| 记忆注入 / Memory injection | 20% | 历史摘要、关键决策、用户偏好 |
| 输出预留 / Output reservation | 15% | 为模型回复与工具调用预留的生成空间 |

> **关键原则：** 输出预留**不可被挤占**。若其它预算膨胀，先压缩记忆与历史，绝不动输出预留——否则模型回复被截断。

### 3.2 压缩策略（Compression Strategy）

当记忆注入预算即将超支，按"保留决策、丢弃中间"原则压缩：

**保留（高信息密度）：**
- 用户明确表达的目标与约束
- 已做出的关键决策及其理由
- 已收集的必要信息（如订单号、用户身份）
- 护栏相关的事实（已确认/已拒绝的事项）

**丢弃（低信息密度）：**
- 工具调用的原始返回长文本（仅保留提取后的结论）
- 礼貌性来回（"好的"、"明白了"）
- 已被后续决策覆盖的中间尝试
- 重复确认的内容

**压缩手法：**
1. **摘要化 / Summarization**：用一段话概括"N 轮内发生了什么、决定了什么"。
2. **结构化提取 / Structured extraction**：将散落信息收敛为键值对（如 `collected: {order_id: "X", reason: "Y"}`）。
3. **引用替代复述 / Reference instead of repeat**：用"见上文第3步的退款理由"代替重复粘贴长文本。

### 3.3 保活机制（Keep-Alive）

长对话中，目标与护栏会随轮次推移被"推远"，模型逐渐偏离。保活机制周期性重注入关键信息：

- **触发条件：** 每 5 轮对话（可配置），或在检测到话题切换/阶段转换时触发。
- **重注入内容：**
  1. 原始任务目标（一句话）
  2. 当前所处阶段
  3. 不可违反的护栏红线
- **注入位置：** 作为系统/开发者消息追加到上下文尾部（靠近输出端，注意力权重更高）。
- **去重：** 重注入时移除上一轮的旧保活块，避免累积膨胀。

### 3.4 溢出处理优先级（Overflow Handling Priority）

当总上下文逼近窗口上限，按以下优先级**逐级裁剪**（先裁剪低优先级）：

```
P0 绝不裁剪 / Never trim:
   ├─ 系统提示中的护栏红线
   ├─ 当前用户输入
   └─ 输出预留

P1 最后裁剪 / Trim last:
   ├─ 当前任务目标与阶段
   └─ 本轮刚产生的关键决策

P2 优先裁剪 / Trim first:
   ├─ 工具原始返回长文本 → 替换为摘要
   └─ 早期轮次的完整对话 → 替换为摘要

P3 立即裁剪 / Trim immediately:
   ├─ 礼貌性来回 / 冗余确认
   └─ 已被覆盖的中间尝试
```

---

## Unlimited Token Budget, Finite Context Window (Token 无限但上下文有限)

对应 AGENTS.md §10 新增规则。

- Token 用量不设上限，可以大胆使用。
- 但上下文窗口容量有限，必须有管理策略——关键信息保活、中间过程压缩、子智能体隔离。
- 不因 Token 充裕就放弃上下文管理。
- 核心原则：Token 是成本问题（可接受），上下文窗口是能力问题（影响质量）。

---

## 4. 决策树 / 流程图 — Decision Tree

```
每轮请求前 / Before each turn
   │
   ▼
计算各预算当前占用 / Compute current budget usage
   │
   ├─ 总占用 ≤ 90% 上限?
   │     └─ YES ──► 直接组装上下文 → 调用模型
   │
   ▼ NO (超预算)
触发压缩 / Trigger compression
   │
   ├─ 是否有 P3 冗余内容? ──► YES ──► 裁剪 P3 → 重新计算
   │                          └─ NO
   ├─ 是否有 P2 工具长文本/早期轮次? ──► YES ──► 摘要化 → 重新计算
   │                                      └─ NO
   ├─ 压缩后仍超限?
   │     └─ YES ──► 触发保活重注入(仅保留 P0 + 当前目标) → 截断 P2 全部
   │
   ▼
保活检查 / Keep-alive check
   │
   ├─ 距上次重注入 ≥ 5 轮? ──► YES ──► 追加保活块(目标+阶段+护栏)，移除旧块
   │                          └─ NO
   ▼
组装并调用模型 / Assemble & call
   │
   ▼
响应后 / After response
   │
   ├─ 更新记忆(提取决策, 丢弃中间) / Update memory
   └─ 记录本轮 token 消耗 / Log token usage
```

---

## 5. 模板示例 — Template Example

### 5.1 上下文预算配置模板

```yaml
# context_budget.yaml — 上下文预算配置 / Context Budget Configuration

model:
  context_window: 128000        # 需验证：以目标模型官方上下文窗口为准
  reserved_output: 4096         # 输出预留 token（绝对值下限）
  safety_margin_pct: 10         # 安全余量百分比

budget_pct:                     # 占比之和应 = 90（扣除安全余量后）
  system_prompt: 20
  tool_descriptions: 15
  user_input: 30
  memory_injection: 20
  output: 15                    # 取 max(占比计算值, reserved_output)

compression:
  enabled: true
  trigger_threshold_pct: 85     # 总占用达到此阈值触发压缩
  strategy: "decision_preserving"  # 保留决策丢弃中间
  keep:
    - "user_goals"
    - "key_decisions"
    - "collected_facts"
    - "guardrail_relevant_facts"
  discard:
    - "raw_tool_outputs_longer_than: 500_tokens"
    - "pleasantries"
    - "superseded_attempts"
    - "duplicate_confirmations"
  summary_method: "structured_extraction"  # summarization | structured_extraction

keep_alive:
  enabled: true
  interval_turns: 5             # 每 N 轮重注入
  trigger_on_stage_change: true # 阶段转换时也触发
  inject_block: |
    [任务目标] {goal}
    [当前阶段] {stage}
    [不可违反] {guardrails}
  dedup: true                   # 移除上一轮旧保活块

overflow_priority:
  never_trim:        ["guardrails", "current_user_input", "output_reservation"]
  trim_last:         ["current_goal", "current_stage", "recent_key_decisions"]
  trim_first:        ["raw_tool_outputs", "early_turns_full_text"]
  trim_immediately:  ["pleasantries", "superseded_attempts"]
```

### 5.2 记忆注入结构示例

```yaml
# 注入到上下文的结构化记忆 / Structured memory injected into context
memory_snapshot:
  goal: "用户要为订单 #A123 办理退款"
  stage: "collecting_reason"          # 当前阶段
  collected:
    order_id: "A123"
    order_status: "delivered"
    refund_reason: null               # 待收集
  decisions:
    - { turn: 2, decision: "确认订单已签收，符合退款条件", reason: "物流状态为已签收" }
  guardrail_facts:
    - "已告知用户退款将在 3 个工作日内到账（平台规则）"
  discarded_summary: "第1轮用户寒暄；第3轮工具返回的完整物流轨迹已摘要为'已签收'"
```

---

## 6. 常见陷阱 / Common Pitfalls

1. **挤占输出预留 / Encroaching on output reservation**
   - 现象：为塞更多历史，压缩输出预算，导致回复被截断、工具调用 JSON 不完整。
   - 纠正：输出预留是硬下限，永不裁剪。

2. **保活块累积膨胀 / Keep-alive block accumulation**
   - 现象：每 5 轮追加一块却不去重，保活内容自身变成上下文负担。
   - 纠正：重注入前必须移除旧保活块（`dedup: true`）。

3. **摘要丢失决策 / Summaries that lose decisions**
   - 现象：压缩时把"为什么做这个决定"也摘要掉了，模型后续无法自洽。
   - 纠正：压缩模板必须显式保留 `key_decisions` 及其 `reason`。

4. **用固定 token 数而非比例 / Fixed token counts instead of ratios**
   - 现象：换模型（窗口大小不同）后预算失配。
   - 纠正：以比例为基准，按实际窗口换算绝对值；`reserved_output` 作为绝对下限补充。

5. **工具返回原样进上下文 / Raw tool outputs straight into context**
   - 现象：一个搜索工具返回 3000 token 原文，迅速吃光预算。
   - 纠正：工具层先做提取/截断，只把结论送入上下文。

6. **忽视话题切换的重注入 / Ignoring re-injection on topic switch**
   - 现象：用户切换话题后，旧目标仍占据保活块，新目标缺失。
   - 纠正：检测到话题切换时立即触发保活重注入，更新 goal/stage。

7. **把护栏放进可裁剪区 / Putting guardrails in trimmable zone**
   - 现象：溢出时连护栏一起裁剪，导致越界。
   - 纠正：护栏始终在 P0，永不裁剪。

---

## 7. 检查清单 / Checklist

- [ ] 五类预算占比之和 ≤ 90%，安全余量已预留 / budget sum ≤ 90%, safety margin reserved
- [ ] 输出预留设为硬下限，不可被挤占 / output reservation is a hard floor
- [ ] 压缩策略配置了"保留决策、丢弃中间"规则 / compression keeps decisions, discards intermediates
- [ ] 工具长文本在进入上下文前已提取/截断 / long tool outputs extracted/truncated before entering context
- [ ] 保活机制已启用，间隔与触发条件已配置 / keep-alive enabled with interval & triggers
- [ ] 保活块去重逻辑已实现，不会累积 / keep-alive dedup implemented, no accumulation
- [ ] 溢出优先级分级清晰，护栏在 P0 / overflow priorities clear, guardrails in P0
- [ ] 话题切换/阶段转换会触发保活重注入 / topic/stage switch triggers re-injection
- [ ] 预算以比例为基准，换模型后可重算 / budget ratio-based, recalculable on model change
- [ ] 每轮 token 消耗有日志，可用于调参 / per-turn token usage logged for tuning
- [ ] 模型上下文窗口数值已对照官方文档确认（标注需验证处） / context window value confirmed against official docs
