# conversation-design.md — 对话流程设计 / Conversation Flow Design

---

## 1. 一句话描述 / One-sentence Description

**中文：** 用显式状态机管理多轮对话的"阶段—已收集—待确认"三元组，配合意图归一化、话题切换、对话修复与结束信号，让智能体在长对话中始终知道"现在在哪、下一步做什么"。

**English:** Manage multi-turn dialogue with an explicit state machine over the triple "stage–collected–pending-confirmation", paired with intent normalization, topic switching, conversation repair, and end-signals, so the agent always knows "where we are and what's next."

---

## 2. 适用场景 / Applicable Scenarios

| 场景 / Scenario | 说明 / Description |
|---|---|
| 任务型对话 / Task-oriented dialogue | 需要多步收集信息才能完成的目标（下单、退款、预约） |
| 多意图交错 / Multi-intent interleaving | 用户在一轮里提到多个诉求，或中途切换话题 |
| 高容错要求 / High fault-tolerance | 用户表述模糊/口误，需澄清与修复 |
| 长会话 / Long sessions | 跨数十轮仍需保持任务进展一致 |
| 交接与结束 / Handoff & closure | 需判断何时任务完成、何时转人工 |

**不适用 / Not applicable：** 单轮问答（如查天气、翻译一句）——状态管理开销大于收益，直接处理即可。

---

## 3. 核心方法论 / Core Methodology

### 3.1 多轮状态管理（Multi-turn State Management）

对话状态由三元组构成，每轮更新：

```
State = ( Stage, Collected, Pending )
```

- **Stage（任务阶段）**：当前处于流程的哪一步。阶段构成有向图（非严格线性），如：
  `greeting → intent_collecting → info_gathering → confirming → executing → closing`
- **Collected（已收集信息）**：键值对，记录已确认的事实（如 `order_id: "A123"`）。仅"已确认"才进入；未确认的放 Pending。
- **Pending（待确认项）**：模型推断出但尚未被用户确认的信息，或流程要求下一步必须澄清的缺失项。

**更新规则：**
1. 每轮根据意图与用户输入，更新 Stage（可能前进/回退/保持）。
2. 用户明确确认的信息从 Pending 移入 Collected。
3. Collected 中的值若被用户更正，旧值标记为 `superseded`（保留可追溯，但不再生效）。

### 3.2 意图识别归一化（Intent Normalization）

将自由表述归一为结构化三元组，避免依赖关键词匹配：

```
Intent = ( action, target, constraints )
```

- **action**：用户想做什么（`query` / `create` / `cancel` / `update` / `confirm` / `unknown`）。
- **target**：作用对象（`order` / `refund` / `appointment` / `account` / ...）。
- **constraints**：限定条件（`time=today` / `amount≤500` / `channel=app` / ...）。

**归一化原则：**
- 多意图：一轮中拆出多个 Intent 元组，按用户语序排序，主意图置顶。
- 模糊意图：当 action 或 target 无法确定，标记 `unknown` 并进入澄清流程（加入 Pending）。
- 归一化结果写入状态，驱动 Stage 转移。

### 3.3 话题切换处理（Topic Switch Handling）

用户中途切换话题时，不能丢失原任务进展：

1. **检测切换：** 新一轮 Intent 的 target 与当前 Stage 所属 target 不同，且用户未表达"继续原任务"。
2. **挂起原任务：** 将当前 `(Stage, Collected, Pending)` 快照存入 `suspended_tasks` 栈/列表，标记 `paused_at` 时间。
3. **开启新任务：** 初始化新任务状态，进入新任务的 `intent_collecting` 阶段。
4. **恢复机制：**
   - 用户主动说"回到刚才那个"→ 弹出栈顶恢复。
   - 新任务完成后主动询问"要继续之前的 {原任务} 吗？"。
5. **限制：** 同时挂起的任务不超过 2–3 个，超过则提示用户先完成其一。

### 3.4 对话修复（Conversation Repair）

智能体主动发现并纠正错误，而非被动等用户指出：

- **检测信号：**
  - 用户说"不是"、"我说的是..."、"搞错了" → 触发更正检测。
  - 模型置信度低 / Collected 中存在矛盾（如同一 order_id 两种状态）。
  - 工具返回与 Collected 假设不符。
- **修复动作：**
  1. 暂停推进 Stage。
  2. 明确指出"我之前理解的是 X，是否应为 Y？"（给出具体更正选项，非开放式提问）。
  3. 用户确认后更新 Collected，标记旧值为 `superseded`。
  4. 重新评估受影响的后续步骤。
- **原则：** 修复要"主动、具体、可确认"——主动发现、具体说明错在哪、让用户用最小成本确认。

### 3.5 对话结束信号（End Signals）

判断何时该收尾，避免无意义延长或过早中断：

- **任务完成信号：** 所有 Collected 满足完成条件 + 执行步骤成功 → 进入 `closing`。
- **用户结束信号：** 用户明确表达"没了/谢谢/再见" → 确认无 Pending 后 closing。
- **无法继续信号：** 连续 2 轮无法澄清关键信息 / 超出能力边界 → 主动建议转人工并 closing。
- **超时/超轮信号：** 超过 `max_turns` 仍卡在同一 Stage → 触发降级（转人工或给总结）。
- **closing 动作：** 输出一句话任务总结 + 确认下一步（如"退款已提交，3 工作日到账，还有别的需要吗？"）。

---

## 4. 决策树 / 流程图 — Decision Tree

```
接收用户输入 / Receive user input
   │
   ▼
意图归一化 → Intent(action, target, constraints) / Normalize intent
   │
   ├─ action == unknown 或 target == unknown?
   │     └─ YES ──► 加入 Pending → 澄清提问 → 等待下一轮
   │
   ▼ NO
话题切换检测 / Topic switch detection
   │
   ├─ target 与当前 Stage 不同 且 非延续? ──► YES ──► 挂起原任务 → 开启新任务
   │                                                │
   ├─ 检测到更正信号("不是"/"搞错了")? ──► YES ──► 进入对话修复
   │                                                │
   ▼ NO (正常推进)
更新状态三元组 (Stage, Collected, Pending) / Update state triple
   │
   ├─ Collected 是否满足当前阶段完成条件?
   │     ├─ NO  ──► 针对缺失项提问 → 等待下一轮
   │     └─ YES ──► Stage 前进
   │
   ▼
结束信号检查 / End signal check
   │
   ├─ 任务完成? ──► closing → 任务总结 → 确认无 Pending → 结束
   ├─ 用户结束? ──► 确认无 Pending → 结束
   ├─ 无法继续? ──► 建议转人工 → 结束
   └─ 超轮? ──────► 降级(转人工/总结) → 结束
   │
   ▼
无结束信号 → 执行本轮动作(调用工具/回复) → 等待下一轮
```

---

## Message Levels: notify vs ask (消息分级)

对应 AGENTS.md §9 新增规则。

| 级别 | 行为 | 使用场景 | 示例 |
|------|------|---------|------|
| notify | 非阻断通知，用户无需回复 | 进度更新、状态变更通知 | "已完成第3步，正在处理第4步" |
| ask | 阻断询问，用户必须回复 | 关键决策点、冲突确认 | "方案A和方案B各有优劣，选哪个？" |

原则：主动用 notify 更新进度，仅在必要需求时用 ask。严禁用 ask 确认非关键事项。

---

## 5. 模板示例 — Template Example

### 5.1 对话状态模板

```yaml
# conversation_state.yaml — 对话状态 / Dialogue State

session_id: "sess_20260712_001"
max_turns: 20
current_turn: 6

current_task:
  task_id: "task_refund_01"
  goal: "为订单 A123 办理退款"
  stage: "confirming"            # greeting|intent_collecting|info_gathering|confirming|executing|closing
  stage_graph:
    - { from: "greeting",          to: "intent_collecting" }
    - { from: "intent_collecting", to: "info_gathering" }
    - { from: "info_gathering",    to: "confirming" }
    - { from: "confirming",        to: "executing" }
    - { from: "executing",         to: "closing" }

  collected:                     # 已确认信息
    order_id: "A123"
    order_status: "delivered"
    refund_reason: "商品破损"
    refund_amount: 259.00

  pending:                       # 待确认项
    - { key: "refund_channel", question: "退款退到原支付账户还是其他账户?", options: ["原账户", "其他"] }

  superseded:                    # 被更正的旧值（可追溯）
    - { key: "refund_reason", old_value: "不喜欢", new_value: "商品破损", corrected_at_turn: 4 }

suspended_tasks: []              # 挂起的切换前任务

last_intent:
  action: "confirm"
  target: "refund"
  constraints: [ "amount=259.00" ]

end_conditions:
  task_complete: "collected.order_id && collected.refund_reason && executed==true"
  unable_to_continue: "consecutive_clarify_failures >= 2"
  max_turns_exceeded: "current_turn >= max_turns"
```

### 5.2 意图归一化与修复示例

```yaml
# 用户原话: "那个不对，不是不喜欢，是收到的时候坏了，退款吧"
# 归一化结果:
normalized_intents:
  - action: "correct"            # 更正
    target: "refund_reason"
    constraints: [ "new_value=商品破损" ]
  - action: "create"
    target: "refund"
    constraints: []

# 修复流程触发:
repair:
  triggered: true
  signal: "用户更正(那个不对/不是)"
  acknowledge: "我之前理解退款原因是'不喜欢'，应为'商品破损'，对吗?"
  on_confirm:
    - move refund_reason to superseded
    - set collected.refund_reason = "商品破损"
    - re-evaluate stage (仍可推进到 confirming)
```

### 5.3 话题切换示例

```yaml
# 用户在第5轮突然问: "对了，你们客服电话多少?"
# 当前任务是退款，新意图 target=contact_info
topic_switch:
  detected: true
  reason: "new target 'contact_info' differs from current task target 'refund'"
  suspend:
    task_id: "task_refund_01"
    snapshot:
      stage: "info_gathering"
      collected: { order_id: "A123", refund_reason: "商品破损" }
  new_task:
    task_id: "task_query_contact_01"
    goal: "查询客服电话"
    stage: "intent_collecting"
  resume_prompt_after_new_task: "已为您查到客服电话。要继续办理刚才的退款吗？"
```

---

## 6. 常见陷阱 / Common Pitfalls

1. **未确认即当作已收集 / Treating unconfirmed as collected**
   - 现象：模型从用户模糊表述推断的信息直接写入 Collected，后续基于错误前提推进。
   - 纠正：推断值先进 Pending，明确确认后才进 Collected。

2. **Stage 只进不退 / Stage only moves forward**
   - 现象：信息被更正后仍停留在已推进的阶段，导致逻辑矛盾。
   - 纠正：Stage 支持回退；更正后重新评估应处阶段。

3. **澄清提问太开放 / Open-ended clarification**
   - 现象：问"你想怎么样？"，用户无法高效回答。
   - 纠正：给出具体选项（如"退原账户还是其他账户？"）。

4. **话题切换丢失原任务 / Losing original task on switch**
   - 现象：切换后原任务状态被覆盖，无法恢复。
   - 纠正：用 suspended_tasks 栈保存快照。

5. **被动等待用户指出错误 / Passive error handling**
   - 现象：模型已发现矛盾却不主动修复，继续推进。
   - 纠正：检测到矛盾/更正信号立即暂停并主动澄清。

6. **结束信号过晚或过早 / End signals too late or too early**
   - 现象：任务已完成却继续追问，或 Pending 未清就强行结束。
   - 纠正：严格按 end_conditions 判断；closing 前确认 Pending 为空。

7. **意图归一化依赖关键词 / Keyword-based intent matching**
   - 现象：用户换种说法就识别失败。
   - 纠正：归一化为结构化三元组，由模型语义理解驱动，非关键词字典。

8. **挂起任务无限堆积 / Unbounded suspended tasks**
   - 现象：用户频繁切换，挂起栈无限增长，上下文爆炸。
   - 纠正：限制同时挂起 2–3 个，超出提示先完成其一。

---

## 7. 检查清单 / Checklist

- [ ] 状态三元组（Stage/Collected/Pending）每轮更新 / state triple updated each turn
- [ ] Collected 仅含已确认信息，推断值先进 Pending / collected holds only confirmed; inferences go to pending
- [ ] Stage 支持回退，更正后重新评估 / stage supports rollback, re-evaluated after correction
- [ ] 意图归一化为 (action, target, constraints) 三元组 / intent normalized to triple
- [ ] 多意图按语序处理，主意图置顶 / multi-intent ordered, primary first
- [ ] 话题切换保存原任务快照，可恢复 / topic switch snapshots original task, resumable
- [ ] 对话修复主动、具体、可确认 / repair is proactive, specific, confirmable
- [ ] 澄清提问提供具体选项而非开放式 / clarifications offer specific options
- [ ] 结束条件明确（完成/用户结束/无法继续/超轮）/ end conditions defined
- [ ] closing 前确认 Pending 为空 / pending cleared before closing
- [ ] 挂起任务数有上限 / suspended tasks bounded
- [ ] max_turns 超限有降级策略 / max_turns overflow has fallback
