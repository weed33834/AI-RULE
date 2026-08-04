# agent-observability.md — 智能体可观测性 / Agent Observability

---

## 1. 一句话描述 / One-sentence Description

**中文：** 通过结构化 JSON 日志与贯穿全链路的 trace ID，记录智能体每一步的工具调用与模型推理，结合延迟、token 消耗、错误率与用户满意度等监控指标及告警阈值，实现生产环境的实时洞察与高效调试。

**English:** Achieve real-time production insight and efficient debugging through structured JSON logs and an end-to-end trace ID that records every tool call and model inference step, combined with monitoring metrics (latency, token consumption, error rate, user satisfaction) and alerting thresholds.

---

## 2. 适用场景 / Applicable Scenarios

| 场景 / Scenario | 说明 / Description |
|---|---|
| 生产监控 / Production monitoring | 持续观察智能体在线运行的健康度与成本 |
| 故障排查 / Incident debugging | 出现异常回复或工具失败时，快速定位是哪一步出了问题 |
| 性能优化 / Performance tuning | 识别延迟瓶颈（哪个工具/哪次模型调用最慢）与成本热点 |
| 质量持续评估 / Continuous quality eval | 采集用户反馈与自动指标，追踪质量趋势 |
| 合规审计 / Compliance audit | 留存可追溯的调用链路记录，满足审计需求 |

**不适用 / Not applicable：** 一次性脚本、无生产流量且无迭代需求的实验——可观测性基础设施的搭建成本可能不划算。

---

## 3. 核心方法论 / Core Methodology

### 3.1 日志标准 / Logging Standards

#### 结构化 JSON 日志

每条日志为一条 JSON 对象，包含固定字段，便于机器解析与聚合查询：

```json
{
  "timestamp": "2026-07-12T10:23:45.123Z",
  "level": "INFO",
  "trace_id": "trc_8f3a2b1c",
  "span_id": "spn_4d2e",
  "parent_span_id": "spn_1a2b",
  "agent": "customer-service-agent",
  "version": "v1.3.0",
  "event": "tool_call",
  "tool_name": "query_order",
  "tool_input": {"order_id": "A123"},
  "tool_output": {"status": "shipped"},
  "duration_ms": 320,
  "input_tokens": 0,
  "output_tokens": 0,
  "status": "success",
  "user_id": "usr_5566"
}
```

#### Trace ID 贯穿

- 每个用户请求生成唯一 `trace_id`，贯穿该请求触发的所有模型调用、工具调用、子智能体调用。
- 采用 span 树结构（`span_id` + `parent_span_id`），还原调用层级与因果关系。
- trace_id 透传到下游服务（HTTP header / 消息队列 metadata），实现跨服务追踪。

### 3.2 监控指标 / Monitoring Metrics

| 指标类别 / Category | 指标 / Metric | 说明 / Description |
|---|---|---|
| **延迟 / Latency** | 首字延迟 TTFT | 请求发出到首字返回 |
| | 总响应时间 | 端到端完成时间 |
| | 工具调用延迟 | 单个工具执行耗时（定位慢工具） |
| | P50 / P95 / P99 | 分位数，P95/P99 反映尾部体验 |
| **成本 / Cost** | 输入 token 消耗 | 每次请求的输入 token |
| | 输出 token 消耗 | 每次请求的输出 token |
| | 估算费用 | 按模型定价换算的单次/累计费用 |
| | API 调用次数 | 单次任务触发的模型调用计数 |
| **可靠性 / Reliability** | 错误率 | 失败请求 / 总请求 |
| | 工具失败率 | 工具调用失败次数 / 总工具调用 |
| | 超时率 | 超时请求占比 |
| | 重试次数 | 平均重试次数 |
| **质量 / Quality** | 用户满意度 | 用户反馈评分（1–5 星 / 赞踩） |
| | 任务完成率 | 端到端任务成功达成比例 |
| | 护栏触发率 | 输入/输出护栏被触发的比例 |

### 3.3 追踪方法 / Tracing Method

记录智能体执行链路的每一步，形成 span 树：

```
trace_id: trc_8f3a2b1c
└─ span: agent_run (1200ms)                    ← 整次智能体运行
   ├─ span: llm_call_1 (450ms)                ← 第一次模型调用（决策）
   │    └─ input_tokens: 850, output_tokens: 60
   ├─ span: tool_call: query_order (320ms)    ← 工具调用
   │    └─ status: success
   ├─ span: llm_call_2 (380ms)                ← 第二次模型调用（基于工具结果生成回复）
   │    └─ input_tokens: 950, output_tokens: 120
   └─ guardrail_check (50ms)                  ← 输出护栏校验
        └─ status: passed
```

每个 span 记录：起止时间、类型（llm_call / tool_call / guardrail / sub_agent）、输入输出摘要、token、状态、错误信息。

### 3.4 告警阈值 / Alert Thresholds

| 指标 / Metric | 建议告警阈值 / Suggested Threshold | 触发动作 / Action |
|---|---|---|
| 错误率 | > 5%（5 分钟窗口） | 立即告警，排查 |
| P95 总响应时间 | > SLA 的 1.5 倍 | 告警，查慢 span |
| 工具失败率 | > 10% | 告警，查外部依赖 |
| 单次请求 token | > 预算上限（如 8000） | 告警，查异常长上下文 |
| 护栏触发率 | 突增（环比 +50%） | 告警，可能有攻击或 prompt 退化 |
| 用户满意度均值 | < 3.5（1–5） | 告警，抽样人工复查 |

> 阈值为示例起点，应根据实际 SLA 与历史基线校准。告警需区分"瞬时抖动"与"持续恶化"——建议用滑动窗口 + 持续 N 分钟才触发，减少噪声。

### 3.5 推荐工具 / Recommended Tools

| 工具 / Tool | 维护方 / Maintainer | 定位 / Positioning | 核心能力 / Key Capabilities | 部署 / Deployment |
|---|---|---|---|---|
| **LangSmith** | LangChain | LangChain 生态原生可观测性平台 | trace 收集、会话回放、生产评估、数据集管理；与 LangChain/LangGraph 深度集成 | 云托管（SaaS） |
| **Langfuse** | Langfuse（开源） | 开源 LLM 可观测性 | 基于 OpenTelemetry 的 tracing、会话追踪、成本分析、prompt 管理、用户反馈采集；v4+ 支持本地 LLM 无侵入追踪 | 自托管（Docker）或云托管；GDPR 友好 |
| **Phoenix (Arize)** | Arize AI | 开源 LLM 评估与追踪 | 完整多步 agent trace 捕获、agent 决策评估、可扩展插件、自定义 evaluator；对 agent 评估支持较深 | 自托管或云托管 |
| **Weights & Biases (Weave)** | Weights & Biases | ML 实验追踪 + LLM 可观测性 | 实验追踪、trace 可视化、LLM 调用记录与回放、评估表格；适合需要将模型实验与线上追踪统一管理的团队 | 云托管（SaaS） |

> **选型速查：** 深度使用 LangChain/LangGraph → LangSmith；需自托管/数据私有/GDPR → Langfuse；重视 agent 多步决策评估 → Phoenix；已有 W&B 实验追踪体系 → Weave。多数工具支持 OpenTelemetry 标准，可降低厂商锁定。

---

## 4. 决策树 / 流程图 — Decision Tree

```
可观测性需求 / Observability needed
   │
   ▼
Q1: 是否已有编排框架？
   ├─ LangChain / LangGraph ──► 优先 LangSmith（原生集成最低成本接入）
   ├─ 自研框架 / 无框架 ──► Q2
   └─ 其他框架 ──► Q2
   │
   ▼
Q2: 是否需要自托管（数据私有/GDPR）？
   ├─ 是 ──► Langfuse（Docker 自托管）或 Phoenix（自托管）
   └─ 否 ──► Q3
   │
   ▼
Q3: 核心诉求是什么？
   ├─ agent 多步决策深度评估 ──► Phoenix
   ├─ 与模型实验追踪统一 ──► Weights & Biases (Weave)
   └─ 通用 tracing + prompt 管理 ──► Langfuse 云版
   │
   ▼
接入实施 / Instrumentation
   ├─ 为每个请求生成 trace_id（透传至下游）
   ├─ 每步（llm_call / tool_call / guardrail）创建 span，记录输入输出/token/耗时/状态
   ├─ 采集用户反馈（赞踩/评分）关联到 trace
   └─ 日志输出为结构化 JSON
   │
   ▼
监控与告警 / Monitoring & Alerting
   ├─ 配置仪表盘：延迟/token/错误率/满意度
   ├─ 配置告警阈值（带滑动窗口降噪）
   └─ 异常时凭 trace_id 快速定位 span 树
```

---

## 5. 模板示例 — Template Example

### 5.1 结构化日志输出（Python 概念示意）

```python
# logging_setup.py — 结构化 JSON 日志配置（概念示意）
import logging
import json
import time
import uuid

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # 合并 extra 字段（trace_id, span_id, tool_name 等）
        for key in ["trace_id", "span_id", "parent_span_id",
                    "agent", "event", "tool_name", "duration_ms",
                    "input_tokens", "output_tokens", "status", "error"]:
            if hasattr(record, key):
                log[key] = getattr(record, key)
        return json.dumps(log, ensure_ascii=False)

logger = logging.getLogger("agent")
handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### 5.2 Trace 贯穿与 span 记录（概念示意）

```python
# tracer.py — 概念示意，展示 trace_id 贯穿与 span 记录逻辑
import uuid
import time
import logging

logger = logging.getLogger("agent")

class Span:
    def __init__(self, trace_id, span_type, name, parent_span_id=None):
        self.trace_id = trace_id
        self.span_id = f"spn_{uuid.uuid4().hex[:8]}"
        self.parent_span_id = parent_span_id
        self.span_type = span_type   # llm_call | tool_call | guardrail
        self.name = name
        self.t0 = time.monotonic()

    def end(self, status="success", **fields):
        duration_ms = int((time.monotonic() - self.t0) * 1000)
        logger.info(
            f"{self.span_type}:{self.name} {status} {duration_ms}ms",
            extra={
                "trace_id": self.trace_id,
                "span_id": self.span_id,
                "parent_span_id": self.parent_span_id,
                "event": self.span_type,
                "tool_name": self.name if self.span_type == "tool_call" else None,
                "duration_ms": duration_ms,
                "status": status,
                **fields,
            },
        )

def new_trace():
    """每个用户请求生成唯一 trace_id。"""
    return f"trc_{uuid.uuid4().hex[:12]}"

# 使用示例
def handle_user_request(user_query):
    trace_id = new_trace()
    root = Span(trace_id, "agent_run", "customer-service")
    try:
        # 第一次模型调用
        llm1 = Span(trace_id, "llm_call", "decide_tool", root.span_id)
        result = call_llm(user_query)           # 你的 LLM 调用
        llm1.end(status="success", input_tokens=850, output_tokens=60)

        # 工具调用
        tool = Span(trace_id, "tool_call", "query_order", llm1.span_id)
        order = query_order("A123")             # 你的工具调用
        tool.end(status="success")

        # 第二次模型调用
        llm2 = Span(trace_id, "llm_call", "generate_reply", root.span_id)
        reply = call_llm(build_prompt(user_query, order))
        llm2.end(status="success", input_tokens=950, output_tokens=120)

        root.end(status="success")
        return reply
    except Exception as e:
        root.end(status="error", error=str(e))
        raise
```

### 5.3 Langfuse 接入示例（概念示意）

```python
# langfuse_setup.py — 概念示意，API 以 Langfuse 官方文档为准
from langfuse import Langfuse

langfuse = Langfuse()   # 读取环境变量 LANGFUSE_SECRET / LANGFUSE_PUBLIC_KEY

# 为一次请求创建 trace，自动贯穿所有 generation/span
trace = langfuse.trace(
    name="customer-service",
    user_id="usr_5566",
    metadata={"agent_version": "v1.3.0"},
)

# 记录一次 LLM 调用
generation = trace.generation(
    name="decide_tool",
    model="gpt-4o-mini",
    input=user_query,
    output=result,
    usage={"input": 850, "output": 60},
)
# Langfuse 自动聚合 trace 视图、成本、延迟，并提供仪表盘
```

### 5.4 监控仪表盘指标定义模板

```yaml
# dashboard_metrics.yaml — 仪表盘指标定义模板
dashboard:
  agent: "customer-service-agent"
  refresh_interval_seconds: 60

  panels:
    latency:
      - metric: "ttft_p95"
        query: "histogram_quantile(0.95, rate(ttft_ms_bucket[5m]))"
        threshold_ms: 2000
      - metric: "total_response_p95"
        threshold_ms: 5000
    cost:
      - metric: "avg_input_tokens"
      - metric: "avg_output_tokens"
      - metric: "estimated_cost_per_request_usd"
    reliability:
      - metric: "error_rate"
        window: "5m"
        threshold: 0.05
      - metric: "tool_failure_rate"
        threshold: 0.10
    quality:
      - metric: "avg_user_rating"
        threshold: 3.5
      - metric: "guardrail_trigger_rate"
        spike_multiplier: 1.5    # 环比 +50% 告警

  alerts:
    - name: "high_error_rate"
      condition: "error_rate > 0.05 for 5m"
      severity: "critical"
    - name: "slow_p95"
      condition: "total_response_p95 > 7500 for 10m"
      severity: "warning"
    - name: "low_satisfaction"
      condition: "avg_user_rating < 3.5 for 30m"
      severity: "warning"
```

---

## 6. 常见陷阱 / Common Pitfalls

1. **日志非结构化 / Unstructured logs**
   - 危害：纯文本日志无法机器解析，难以聚合查询与告警。
   - 纠正：统一输出结构化 JSON，固定字段名。

2. **trace_id 未贯穿下游 / trace_id not propagated**
   - 危害：跨服务调用断裂，无法还原完整链路。
   - 纠正：trace_id 通过 HTTP header / 消息 metadata 透传到所有下游服务。

3. **记录完整明文 prompt 泄露敏感信息 / Logging full prompts leaks PII**
   - 危害：用户隐私/敏感数据进入日志与可观测性平台。
   - 纠正：对 PII 脱敏后再记录；或只记录摘要与 token 数，按需采样完整内容。

4. **只看平均值不看分位数 / Averages only, no percentiles**
   - 危害：平均值掩盖尾部延迟，少数用户体验极差却不可见。
   - 纠正：监控 P95/P99，关注尾部体验。

5. **告警无降噪导致告警疲劳 / Alert fatigue from noisy alerts**
   - 危害：瞬时抖动频繁告警，团队逐渐忽视。
   - 纠正：用滑动窗口 + 持续 N 分钟才触发；区分 critical/warning 级别。

6. **未关联用户反馈与 trace / Feedback not linked to trace**
   - 危害：知道"用户不满意"但无法定位是哪次调用的问题。
   - 纠正：用户反馈（赞踩/评分）必须关联到 trace_id。

7. **可观测性数据无限增长 / Unbounded observability data growth**
   - 危害：存储成本失控。
   - 纠正：设保留策略（如 trace 保留 30 天，摘要指标长期保留）；采样高频低价值请求。

---

## 7. 检查清单 / Checklist

- [ ] 日志统一为结构化 JSON，字段名固定 / structured JSON logs with fixed schema
- [ ] 每个请求生成唯一 trace_id 并贯穿所有下游服务 / unique trace_id propagated end-to-end
- [ ] 每步（llm_call / tool_call / guardrail）创建 span，记录输入输出/token/耗时/状态 / span per step with full metadata
- [ ] 已配置延迟（TTFT/总响应/P95）、成本（token/费用）、可靠性（错误率）、质量（满意度）仪表盘 / dashboards for latency/cost/reliability/quality
- [ ] 告警阈值已设置并带滑动窗口降噪 / alert thresholds set with windowed de-noise
- [ ] 用户反馈已关联到 trace_id / user feedback linked to traces
- [ ] PII 已在记录前脱敏 / PII masked before logging
- [ ] 已选定可观测性工具并完成接入（LangSmith/Langfuse/Phoenix/W&B）/ tool selected & integrated
- [ ] trace 数据有保留策略，避免无限增长 / retention policy in place
- [ ] 可凭 trace_id 快速定位 span 树进行调试 / trace_id-based debugging works end-to-end

---

## 真实性要求 / Authenticity Requirements

- 推荐工具（LangSmith、Langfuse、Phoenix/Arize、Weights & Biases）均为真实存在的产品/开源项目。其维护方与核心能力基于公开官网与文档信息核实：LangSmith 为 LangChain 官方平台；Langfuse 为开源项目（支持 OpenTelemetry、可自托管、GDPR 友好）；Phoenix 为 Arize AI 开源的 LLM 追踪与评估工具；Weights & Biases 为知名 ML 实验追踪平台（其 LLM 可观测能力对应 Weave）。**各工具的具体 API、功能集与定价会随版本演进**——接入前务必以官方文档为准。
- 结构化日志、trace/span 模型、OpenTelemetry 均为业界真实通用的可观测性标准与概念。OpenTelemetry 是 CNCF 旗下的真实开源可观测性标准。
- 代码示例为**概念示意**，展示了结构化日志、span 记录、Langfuse 接入的真实写法形态，但具体 SDK 方法名与参数需对照目标工具当前版本文档校准。仪表盘查询语句（如 `histogram_quantile`）为 Prometheus 真实查询语法示例。
- 告警阈值（如错误率 > 5%、P95 > SLA 1.5 倍）为**示例起点**，应根据实际 SLA 与历史基线校准。
- 任何标注"需验证"的信息，使用前必须通过官方文档二次确认，不得直接用于生产决策。

## 进阶：12 项高级架构模式 / Advanced: 12 Architecture Patterns

> 本文档的可观测性设计在 `advanced-patterns.md` 中有进一步的工业级扩展：
> - **模式 5（六类 span 模型）**：root / agent / subagent / transfer / rule / tool 六类 span，每类含 span_id / parent_span_id / name / start_time / end_time / attributes / status，可可视化优先级链裁决全过程。来源 OpenTelemetry GenAI semantic conventions。
> - **模式 6（可观测性架构设计）**：三层架构——采集层（OTel SDK）→ 存储层（Langfuse 自部署）→ 分析层（trace→dataset→experiment 闭环）。事故记录结构化为 JSONL trace。高敏感场景自部署。来源 Langfuse / Phoenix(Arize) / OTel GenAI。
