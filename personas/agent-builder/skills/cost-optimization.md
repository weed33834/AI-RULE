# cost-optimization.md — Token 成本优化策略 / Token Cost Optimization Strategy

---

## 1. 一句话描述 / One-sentence Description

**中文：** 通过分层成本分析框架（输入/输出/缓存/嵌入分别核算）、按任务复杂度的模型路由、Prompt 压缩、语义缓存与批处理等组合手段，在不牺牲质量的前提下将智能体的 token 成本降至最低。

**English:** Minimize an agent's token cost without sacrificing quality through a layered cost-analysis framework (input / output / cache / embedding accounted separately), complexity-based model routing, prompt compression, semantic caching, and batch processing.

---

## 2. 适用场景 / Applicable Scenarios

| 场景 / Scenario | 说明 / Description |
|---|---|
| 高频调用 / High-volume calls | 智能体日均调用量大，token 成本成为主要运营支出 |
| 多轮对话 / Multi-turn conversations | 对话历史不断累积，输入 token 膨胀 |
| 大上下文 RAG / Large-context RAG | 每次注入大量检索文档，输入成本高 |
| 混合任务 / Mixed task complexity | 既有简单分类/提取，也有复杂推理，全用大模型浪费 |
| 预算受限 / Budget constrained | 需在固定预算下最大化吞吐与覆盖 |

**不适用 / Not applicable：** 调用量极低、成本不敏感的场景——优化投入可能超过节省。

---

## 3. 核心方法论 / Core Methodology

### 3.1 成本分析框架 / Cost Analysis Framework

一次智能体请求的真实成本由四类 token 独立累加：

```
总成本 = 输入 token 费 + 输出 token 费 + 缓存 token 费 + 嵌入 token 费
        （+ 工具/服务附加费，如 web search 按次计费）
```

| 成本类别 / Category | 说明 / Description | 优化杠杆 / Lever |
|---|---|---|
| **输入 token / Input** | 发送给模型的全部 prompt（system + history + tools + 用户输入） | 压缩、裁剪、缓存 |
| **输出 token / Output** | 模型生成的回复（通常单价高于输入数倍） | 限制 max_tokens、精简输出格式 |
| **缓存 token / Cache** | prompt caching 的写入/读取（命中后费率远低于标准输入） | 稳定前缀、显式缓存断点 |
| **嵌入 token / Embedding** | 向量化文档/查询用于 RAG 检索 | 精简文档、缓存向量、选廉价嵌入模型 |

> **关键洞察：** 输出 token 单价通常是输入 token 的 4–6 倍，因此"让模型少说"往往比"让模型少读"更省钱；但大上下文场景下输入 token 体积远大于输出，输入侧优化同样关键。

### 3.2 真实定价参考 / Real Pricing Reference

> 以下定价基于 OpenAI 与 Anthropic 官方定价页面（核实日期：2026-07）。**定价会随厂商调整而变化，使用前务必以官方页面为准。** 此处仅列出文档涉及的模型；厂商已有更新的模型系列，选型时应一并评估。

#### OpenAI（标准处理，<270K 上下文）

| 模型 / Model | 输入 / Input | 缓存输入 / Cached Input | 输出 / Output |
|---|---|---|---|
| GPT-4o | $2.50 / 1M | $1.25 / 1M | $10.00 / 1M |
| GPT-4o-mini | $0.15 / 1M | $0.075 / 1M | $0.60 / 1M |

- Batch API：输入与输出均 **−50%**（异步，24h 内完成）。
- 来源：https://openai.com/api/pricing/ 与 https://platform.openai.com/docs/pricing

#### Anthropic Claude（标准处理）

| 模型 / Model | 输入 / Input | 缓存写入(5m) / Cache Write 5m | 缓存写入(1h) / Cache Write 1h | 缓存读取 / Cache Hit | 输出 / Output |
|---|---|---|---|---|---|
| Claude Sonnet 4.5 | $3.00 / 1M | $3.75 / 1M | $6.00 / 1M | $0.30 / 1M | $15.00 / 1M |
| Claude Haiku 4.5 | $1.00 / 1M | $1.25 / 1M | $2.00 / 1M | $0.10 / 1M | $5.00 / 1M |

- 缓存读取费率 = 标准输入的 0.1×；缓存写入 5m = 1.25×、1h = 2×。
- Batch API：输入与输出均 **−50%**。
- 来源：https://docs.claude.com/en/docs/about-claude/pricing

#### 嵌入模型（OpenAI）

| 模型 / Model | 价格 / Price |
|---|---|
| text-embedding-3-small | $0.02 / 1M tokens |
| text-embedding-3-large | $0.13 / 1M tokens |

> **成本量级感知：** 以 GPT-4o-mini 处理 1M 输入 + 0.2M 输出为例：(0.15 × 1 + 0.60 × 0.2) = $0.27；同等量用 GPT-4o 则为 (2.50 × 1 + 10 × 0.2) = $4.50，相差约 16 倍。

### 3.3 模型选择决策树 / Model Selection Decision Tree

```
请求到达 / Request arrives
   │
   ▼
Q1: 任务是否仅需要向量化（检索/分类前置）？
   ├─ 是 ──► 嵌入模型（text-embedding-3-small），不走生成模型
   └─ 否 ──► Q2
   │
   ▼
Q2: 任务复杂度？
   ├─ 简单（分类/提取/改写/格式转换/简短问答）
   │     ──► 小模型：GPT-4o-mini 或 Claude Haiku 4.5
   ├─ 中等（多步工具调用/中等推理/RAG 问答）
   │     ──► 中型模型：按 provider 选 GPT-4o 或 Claude Sonnet 4.5
   └─ 复杂（深度推理/长链规划/高难度代码）
         ──► 强模型（必要时用推理模型）；用完即切回小模型
   │
   ▼
Q3: 该请求是否可容忍异步延迟（分钟级）？
   ├─ 是 ──► 走 Batch API（−50%）
   └─ 否 ──► 标准实时处理
   │
   ▼
Q4: prompt 中是否有稳定的大段前缀（system/工具定义/知识库）？
   ├─ 是 ──► 启用 prompt caching（命中后输入费率降至 0.1×）
   └─ 否 ──► 标准处理
```

### 3.4 Prompt 压缩技巧 / Prompt Compression

| 技巧 / Technique | 说明 / Description |
|---|---|
| **精简 system prompt** | 删除冗余客套与重复约束，用短指令替代长段落 |
| **历史裁剪 / 窗口管理** | 仅保留最近 N 轮；旧轮次做摘要后以压缩形式保留 |
| **工具定义精简** | 工具 description 简洁化；不在 prompt 中冗余重复 schema |
| **结构化输出** | 要求 JSON/表格而非自然语言长文，减少输出 token |
| **few-shot 精选** | 用 1–2 个高质量示例替代 5+ 个低质示例 |
| **指令去重** | 多处出现的相同约束合并为一处 |
| **上下文按需注入** | RAG 只注入 top-k 相关片段而非整篇文档 |

### 3.5 缓存策略 / Caching Strategy

| 策略 / Strategy | 机制 / Mechanism | 适用 / Best For |
|---|---|---|
| **Prompt Caching（精确缓存）** | 厂商原生：稳定前缀命中后按 0.1× 计费（Anthropic）/ 0.5×（OpenAI） | system prompt、工具定义、知识库等稳定大段前缀 |
| **语义缓存 / Semantic Cache** | 将查询向量化，命中语义相似的历史请求则直接返回缓存结果 | 高重复率问答（FAQ、客服） |

> **语义缓存注意：** 仅适用于"答案不随时间变化"的查询；涉及实时数据（订单状态、库存）的查询不可缓存，否则返回过期信息。命中阈值需调参——过低会返回错误答案，过高则命中率低。

### 3.6 批处理优化 / Batch Processing

- OpenAI Batch API 与 Anthropic Batch API 均提供 **−50%** 折扣，代价是异步（24h 内返回）。
- 适用场景：离线评估、批量标注、日志处理、非实时的内容生成。
- 不适用：用户实时对话、需要秒级响应的在线服务。

### 3.7 模型路由 / Model Routing

通过一个轻量路由层，按任务复杂度将请求分发到不同模型：

```
用户请求 ──► 路由层（规则/小分类器）
               ├─ 简单 ──► GPT-4o-mini / Claude Haiku（廉价快速）
               ├─ 中等 ──► GPT-4o / Claude Sonnet
               └─ 复杂 ──► 强模型（必要时推理模型）
```

路由判断依据：请求类型标签、输入长度、是否需要工具、历史轮数、用户分级等。先从规则路由起步，再逐步引入小分类器。

---

## 4. 决策树 / 流程图 — Decision Tree

```
成本优化需求 / Cost optimization needed
   │
   ▼
Step 1: 量化现状 / Measure baseline
   ├─ 分别统计 输入/输出/缓存/嵌入 token 量与费用
   └─ 定位最大成本项（通常输入或输出）
   │
   ▼
Step 2: 按最大成本项对症下药 / Target the biggest bucket
   ├─ 输入最大 ──► Q-A
   ├─ 输出最大 ──► Q-B
   └─ 嵌入最大 ──► Q-C
   │
   ▼
Q-A(输入): 是否有稳定大前缀？
   ├─ 是 ──► 启用 prompt caching
   └─ 否 ──► 压缩 prompt + 历史裁剪 + 按需注入 RAG
   │      ├─ 仍高 ──► 简单任务路由到小模型
   │
   ▼
Q-B(输出): 是否可改结构化输出减少长度？
   ├─ 是 ──► 要求 JSON/精简格式 + 限制 max_tokens
   └─ 否 ──► 简单任务路由到输出更便宜的小模型
   │
   ▼
Q-C(嵌入): 是否可缓存向量避免重复嵌入？
   ├─ 是 ──► 向量缓存 + 文档去重
   └─ 否 ──► 换 text-embedding-3-small（若精度允许）
   │
   ▼
Step 3: 是否有可异步的批量任务？
   ├─ 是 ──► 迁移到 Batch API（−50%）
   └─ 否 ──► 保持实时
   │
   ▼
Step 4: 是否有高重复率查询？
   ├─ 是 ──► 加语义缓存（注意时效性）
   └─ 否 ──► 跳过
   │
   ▼
Step 5: 回测验证 / Validate
   ├─ 成本下降 + 质量未退化 ──► 上线
   └─ 质量退化 ──► 回退，调整阈值/路由策略
```

---

## 5. 模板示例 — Template Example

### 5.1 成本分析模板

```yaml
# cost_analysis.yaml — 单日成本分析模板
date: "2026-07-12"
agent: "customer-service-agent"

cost_breakdown:
  input_tokens:
    count: 48000000          # 48M
    rate_per_million: 2.50   # GPT-4o
    cost_usd: 120.00
  cached_input_tokens:
    count: 12000000          # 12M（缓存命中）
    rate_per_million: 1.25
    cost_usd: 15.00
  output_tokens:
    count: 9000000           # 9M
    rate_per_million: 10.00
    cost_usd: 90.00
  embedding_tokens:
    count: 30000000          # 30M
    rate_per_million: 0.02   # text-embedding-3-small
    cost_usd: 0.60
  total_usd: 225.60

optimization_opportunities:
  - area: "input"
    finding: "system prompt + 工具定义占输入 60%，且稳定不变"
    action: "启用 prompt caching"
    est_saving: "输入费用从 $120 降至约 $82（含缓存写入）"
  - area: "output"
    finding: "客服回复偏冗长，可改结构化"
    action: "要求简洁分点回复 + max_tokens 限制"
    est_saving: "输出减少约 30%，节省 $27"
  - area: "model_routing"
    finding: "70% 请求为简单 FAQ，全用 GPT-4o"
    action: "FAQ 路由到 GPT-4o-mini"
    est_saving: "简单请求成本降至约 1/16"
```

### 5.2 模型路由实现示例（概念示意）

```python
# router.py — 概念示意，路由逻辑需按实际业务校准
from enum import Enum

class ModelTier(Enum):
    SMALL = "gpt-4o-mini"      # 简单任务
    MEDIUM = "gpt-4o"          # 中等任务
    # 强模型按需扩展

def route_model(query: str, has_tools: bool, history_turns: int) -> str:
    """按任务复杂度选择模型。规则示例，需按实际调优。"""
    # 简单：短查询、无工具、少历史
    if not has_tools and len(query) < 50 and history_turns <= 2:
        return ModelTier.SMALL.value
    # 默认中等
    return ModelTier.MEDIUM.value

# 成本对比（示意）
# 假设 100 万次简单请求：全用 GPT-4o 约 $4.50/M-req-set；路由后简单部分用 mini 约 $0.27/M-req-set
```

### 5.3 Prompt Caching 启用示例（Anthropic）

```python
# anthropic_cache.py — 概念示意，API 以 Anthropic 官方文档为准
import anthropic

client = anthropic.Anthropic()

# 自动缓存：在请求顶层加 cache_control，系统自动管理断点
response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=512,
    system=[
        {
            "type": "text",
            "text": LARGE_SYSTEM_PROMPT,   # 稳定的大段前缀
            "cache_control": {"type": "ephemeral"}  # 显式缓存断点
        }
    ],
    messages=[{"role": "user", "content": user_query}],
)
# 首次：按 1.25× 写入缓存；后续 5 分钟内命中按 0.1× 计费
```

### 5.4 语义缓存实现示例（概念示意）

```python
# semantic_cache.py — 概念示意，需引入向量库（如 FAISS/Chroma）
import numpy as np

class SemanticCache:
    def __init__(self, embed_fn, store, similarity_threshold=0.92):
        self.embed_fn = embed_fn
        self.store = store              # 向量库实例
        self.threshold = similarity_threshold

    def get(self, query: str):
        q_vec = self.embed_fn(query)
        hit = self.store.search(q_vec, top_k=1)
        if hit and hit[0]["score"] >= self.threshold:
            # 命中：直接返回缓存结果，跳过 LLM 调用
            return hit[0]["answer"]
        return None                     # 未命中，走正常 LLM 调用

    def put(self, query: str, answer: str):
        q_vec = self.embed_fn(query)
        self.store.add(q_vec, {"query": query, "answer": answer})

# 注意：仅缓存"答案不随时效变化"的查询；订单状态等实时查询需设 TTL 或不缓存
```

---

## 6. 常见陷阱 / Common Pitfalls

1. **只看总成本不看结构 / Ignoring cost structure**
   - 危害：不知道钱花在输入还是输出，优化无的放矢。
   - 纠正：按四类 token 分别核算，定位最大成本项再对症下药。

2. **全用大模型"图省事" / Using only the biggest model**
   - 危害：简单任务也用 GPT-4o / Sonnet，成本远超必要。
   - 纠正：引入模型路由，简单任务用 mini / Haiku。

3. **语义缓存返回过期/错误答案 / Semantic cache returning stale answers**
   - 危害：相似但不相同的查询命中缓存，返回错误信息。
   - 纠正：设合理相似度阈值；实时性查询（订单、库存、价格）不缓存或设短 TTL。

4. **忽略输出成本 / Overlooking output cost**
   - 危害：输出单价是输入的 4–6 倍，冗长回复烧钱。
   - 纠正：限制 max_tokens、要求结构化/精简输出。

5. **缓存未命中却一直付写入费 / Paying cache writes with no hits**
   - 危害：前缀频繁变动导致永远只写不读，缓存反而更贵。
   - 纠正：确保缓存的前缀足够稳定；监控命中率，命中率低则调整断点。

6. **Batch API 用于实时场景 / Batch API for real-time**
   - 危害：用户等待 24h，体验崩坏。
   - 纠正：Batch 仅用于离线/异步任务。

7. **压缩 prompt 损失关键信息 / Over-compressing prompts**
   - 危害：为省 token 删掉了关键约束，导致质量退化。
   - 纠正：压缩后必须回归测试，确认质量未降。

---

## 7. 检查清单 / Checklist

- [ ] 已按四类 token（输入/输出/缓存/嵌入）分别核算成本 / cost broken down by 4 categories
- [ ] 已定位最大成本项并制定针对性优化 / biggest cost bucket identified & targeted
- [ ] 稳定大前缀已启用 prompt caching，命中率可监控 / prompt caching enabled with hit-rate monitoring
- [ ] 简单任务已路由到小模型（mini / Haiku）/ simple tasks routed to small models
- [ ] 输出已限制 max_tokens 并倾向结构化 / output capped & structured
- [ ] prompt 已做精简压缩且回归测试通过 / prompts compressed, regression passed
- [ ] 高重复查询已加语义缓存，时效性查询已排除 / semantic cache added, real-time queries excluded
- [ ] 离线任务已迁移到 Batch API（−50%）/ offline tasks moved to Batch API
- [ ] 嵌入已用 text-embedding-3-small（若精度允许）且向量已缓存 / embeddings minimized & cached
- [ ] 优化后已回测：成本下降且质量未退化 / post-optimization validated: cost down, quality stable
- [ ] 定价已与官方页面最新值核对 / pricing verified against official pages

---

## 真实性要求 / Authenticity Requirements

- 文中定价数据来源于 OpenAI 官方定价页面（openai.com/api/pricing、platform.openai.com/docs/pricing）与 Anthropic 官方定价页面（docs.claude.com/en/docs/about-claude/pricing），核实日期为 2026-07。**厂商定价会随时调整**，使用前必须以官方页面当前值为准；本文不保证定价的持续准确性。
- Prompt caching、Batch API 的折扣机制（Anthropic 缓存读取 0.1×、写入 1.25×/2×；双方 Batch −50%）均来自上述官方文档。OpenAI 的缓存折扣比例（cached input 约为标准输入的 0.5×）以官方定价页为准。
- 文档涉及 GPT-4o / GPT-4o-mini / Claude Sonnet 4.5 / Claude Haiku 4.5 等模型均为真实存在的产品模型。**厂商持续推出新模型系列**（如更新的旗舰与 mini 模型），选型时应评估最新可用模型，而非局限于本文列出的型号。
- 代码示例（模型路由、prompt caching、语义缓存）为**概念示意**，展示了真实 API 的调用形态，但需对照目标厂商 SDK 当前版本文档校准字段名与参数。语义缓存需自行引入向量库（如 FAISS、Chroma 等真实开源项目）。
- 成本估算数字为基于公开定价的算术示例，非真实账单；实际成本取决于真实 token 用量。
- 任何标注"需验证"的信息，使用前必须通过官方文档二次确认，不得直接用于生产决策。
