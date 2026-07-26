---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 用户要设计智能体的可观测性架构（span 模型、采集存储、trace→dataset 闭环）
terminates_when: T    # 可观测性两项模式（Pattern 5-6）的设计已落地为 config.yaml 接入方案
provides: π           # 可观测性设计模式（六类 span 模型 / 三层可观测性架构）、config 模板、检查清单
interface: R          # 输入=智能体可观测性需求与隐私约束；输出=span 模型 + 接入方案 + 检查清单
---

# 可观测性设计模式 (Observability Design Patterns)

---

## Category 2: Observability Design / 第二类：可观测性设计

### Pattern 5: Six-Type Span Model / 六类 span 模型

#### 核心概念 / Core Concept

OpenTelemetry GenAI semantic conventions 定义了智能体可观测性的 span（追踪单元）标准。一个智能体的执行不是单次调用，而是多类 span 组成的树。我们定义六类 span，覆盖智能体执行的完整生命周期：

| span 类型 | 含义 | 何时产生 |
|-----------|------|---------|
| `root` | 用户请求根 span | 每次用户请求开始时 |
| `agent` | 每个智能体处理 | 主智能体或子智能体开始处理时 |
| `subagent` | 子智能体调用 | 编排者调用子智能体时 |
| `transfer` | 转介事件 | 智能体把任务转介给另一智能体或人工时 |
| `rule` | 规则触发 | 某条规则（如护栏、优先级裁决）被触发时 |
| `tool` | 工具调用 | 智能体调用工具时 |

每类 span 的标准 attributes：`span_id` / `parent_span_id` / `name` / `start_time` / `end_time` / `attributes`（类型特定字段）/ `status`。

核心价值：**可可视化优先级链裁决全过程**。当 P0 与 P1 冲突时，`rule` span 记录"哪条规则触发了、裁决结果是什么、为什么"，让优先级裁决从黑盒变白盒。生产事故复盘时，span 树能还原"智能体为什么做了这个决定"。

#### 设计指南 / Design Guidelines

1. **智能体设计必须定义 span 模型**：在 config.yaml 的 `observability` 段声明哪些操作产生哪类 span，标注哪些操作需要追踪（不是所有操作都要 span，过度追踪也有成本）。
2. **`rule` span 是安全可观测性的核心**：每条 P0/P1 规则的触发都要产生 `rule` span，记录规则 ID、触发条件、裁决结果。这是审计和事故复盘的关键证据。
3. **`transfer` span 必须记录转介原因**：转介给人工或另一智能体时，span 记录"为什么转介"（超出能力边界/需要人工确认/冲突无法裁决），不只是"转介了"。
4. **span 关系要形成树而非图**：每个 span 有且仅有一个 parent_span_id，避免多父 span 导致可视化混乱。

#### 集成模式 / Integration Patterns

```json
// 六类 span 示例 / six-type span example
{"span_id":"spn_root","parent_span_id":null,"name":"user_request","type":"root","start_time":"...T10:00:00Z","end_time":"...T10:00:05Z","attributes":{"user_id":"u1","intent":"refund_query"},"status":"ok"}
{"span_id":"spn_agent","parent_span_id":"spn_root","name":"cs_agent_run","type":"agent","start_time":"...T10:00:00Z","end_time":"...T10:00:05Z","attributes":{"agent":"customer-service","version":"v1.5.0"},"status":"ok"}
{"span_id":"spn_rule1","parent_span_id":"spn_agent","name":"rule:pii_check","type":"rule","start_time":"...T10:00:01Z","end_time":"...T10:00:01Z","attributes":{"rule_id":"P0-4","triggered":false,"evaluated":true},"status":"ok"}
{"span_id":"spn_tool1","parent_span_id":"spn_agent","name":"tool:query_order","type":"tool","start_time":"...T10:00:02Z","end_time":"...T10:00:02Z","attributes":{"tool":"query_order","side_effect":"read-only","args":{"order_id":"A123"}},"status":"ok"}
{"span_id":"spn_transfer","parent_span_id":"spn_agent","name":"transfer:human","type":"transfer","start_time":"...T10:00:04Z","end_time":"...T10:00:04Z","attributes":{"reason":"refund_amount_exceeds_auto_limit","to":"human_agent"},"status":"ok"}
```

集成到 AGENTS.md §10 上下文工程与可观测性技能 `agent-observability.md`：六类 span 是该技能追踪方法的标准化扩展，把原有 `llm_call / tool_call / guardrail / sub_agent` 四类细化为六类，新增 `root` 与 `rule` 两类。

#### 来源引用 / Source Citation

- OpenTelemetry GenAI semantic conventions：`https://opentelemetry.io/docs/specs/semconv/gen-ai/`
- OTel GenAI 工作组：`https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai`
- span 树思想：OpenTelemetry tracing 通用规范

---

### Pattern 6: Observability Architecture Design / 可观测性架构设计

#### 核心概念 / Core Concept

可观测性不是"加个日志"那么简单，而是三层架构：

- **采集层（OTel SDK）**：在智能体代码里埋点，按 Pattern 5 的六类 span 模型采集。用 OpenTelemetry SDK，跨语言、跨平台标准化。
- **存储层（Langfuse 自部署）**：trace 数据存到 Langfuse（开源、可自部署）。自部署是关键——高敏感场景数据不出本地。
- **分析层（trace → dataset → experiment 闭环）**：不只是看 trace 排查问题，而是把线上真实 case 沉淀为新 golden case。trace 变测试集：一个线上真实 case 跑通了，自动沉淀为评估数据集的一条；跑挂了，自动沉淀为一条失败 case。

三个进阶能力：

1. **trace 变测试集**：线上真实 case 自动沉淀为新 golden case，让评估数据集持续增长，覆盖人工想不到的边界情况。
2. **事故记录结构化**：从摘要式（"客服智能体今天挂了 3 次"）升级为结构化 trace（JSONL，含 `trace_id` / `parent_span_id` / `agent_name` / `input` / `output` / `rules_triggered` / `latency` / `tool_calls`）。事故复盘不再靠口述，直接看 trace。
3. **隐私约束**：高敏感场景（医疗、金融）必须自部署 Langfuse，数据不出本地。trace 中的 PII 在采集时脱敏。

#### 设计指南 / Design Guidelines

1. **智能体必须定义可观测性接入方案**：在 config.yaml 声明 trace 格式、存储位置（自部署/云）、隐私策略（脱敏字段列表）。
2. **采集与存储解耦**：OTel SDK 采集，Langfuse 存储，两者通过 OTLP 协议解耦。换存储后端不用改采集代码。
3. **trace → dataset 沉淀要有人工审核**：自动沉淀的 case 在进入正式 golden set 前要人工审核，避免把错误 case 当基准。
4. **隐私脱敏在采集时做，不是存储时**：PII 在 SDK 埋点时就脱敏，确保脱敏前的明文不进入网络传输和存储。

#### 集成模式 / Integration Patterns

```
[Agent code] --OTel SDK埋点--> [OTLP export] --https--> [Langfuse自部署]
                                                          │
                                                  ┌───────┴────────┐
                                                  ▼                ▼
                                          [trace 查询]      [trace→dataset沉淀]
                                          排查问题           新 golden case
                                                  │                │
                                                  └───────┬────────┘
                                                          ▼
                                                  [experiment 闭环]
                                                  线上 trace 驱动评估
```

```yaml
# config.yaml 可观测性接入方案 / observability接入
observability:
  span_model: six_type   # Pattern 5
  collector: opentelemetry-sdk
  storage:
    backend: langfuse
    deployment: self-hosted   # 高敏感场景必须自部署
    endpoint: https://langfuse.internal.corp
  privacy:
    pii_redaction_at_collect: true
    redact_fields: [phone, id_card, email, address]
  trace_to_dataset:
    auto_sediment: true
    human_review_before_golden: true
```

集成到 AGENTS.md §13 部署适配与 §16 隐私合规：可观测性接入方案纳入 config.yaml 第七域（在原六域基础上扩展），隐私策略与 §16 PII 脱敏要求对齐。trace → dataset 闭环与 §14 演进策略的对话日志分析衔接。

#### 来源引用 / Source Citation

- Langfuse：`https://langfuse.com/`，开源 LLM 可观测性，支持自部署
- Phoenix (Arize)：`https://github.com/Arize-ai/phoenix`，开源 LLM 可观测性
- OpenTelemetry GenAI：`https://opentelemetry.io/docs/specs/semconv/gen-ai/`
- trace → dataset 思想：Langfuse Datasets 功能

---
