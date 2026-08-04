# Knowledge Injection Strategy / 知识注入策略

---

## 一句话描述 / One-Sentence Description

**中文：** 知识注入策略是控制外部知识何时、以何种形式、按何种优先级进入智能体上下文的规则体系，通过来源分级、时效管理和冲突裁决，确保智能体在有限的上下文窗口内获得最准确、最相关的知识支撑。

**English:** A knowledge injection strategy is a rule system that controls when, in what form, and at what priority external knowledge enters an agent's context, ensuring the agent receives the most accurate and relevant knowledge support within a limited context window through source tiering, freshness management, and conflict adjudication.

---

## 适用场景 / Applicable Scenarios

| 场景 / Scenario | 说明 / Description |
|---|---|
| 领域知识问答 / Domain knowledge QA | 智能体需要特定行业或产品知识才能回答用户问题 |
| 实时信息获取 / Real-time information | 知识可能随时变化（如价格、库存、新闻），需要联网搜索 |
| 多来源知识整合 / Multi-source integration | 同一问题可能有多份文档提供不同角度的知识 |
| 技能增强 / Skill augmentation | 智能体需要学习特定操作流程（如 API 调用步骤、工具使用方法） |
| 合规约束注入 / Compliance constraints | 智能体必须遵守特定规则（如法律条款、公司政策） |

---

## 核心方法论 / Core Methodology

### 1. 来源分级（Source Tiering）

知识来源按可信度和优先级从高到低分为四个层级：

```
层级 1（最高优先级）：系统提示内置（System Prompt）
  - 内容：角色定义、行为规则、核心约束、不可变指令
  - 特点：始终存在于上下文中，不可被低层级覆盖
  - 适用：安全边界、身份设定、绝对约束
  - Token 成本：每次调用都消耗，需精简

层级 2：知识库（Knowledge Base / Curated Documents）
  - 内容：经过人工审核的文档（产品手册、FAQ、政策文档）
  - 特点：可信度高、结构化、可版本管理
  - 注入方式：按需检索后注入，或全量嵌入 system prompt（仅当体量小时）
  - 适用：稳定不变的领域知识

层级 3：RAG 检索（Retrieval-Augmented Generation）
  - 内容：从向量数据库中检索的相关文档片段
  - 特点：动态检索、语义匹配、覆盖面广但可能有噪声
  - 注入方式：query embedding → top-k 检索 → 注入到 user/assistant 消息中
  - 适用：大规模文档库、知识频繁更新

层级 4（最低优先级）：联网搜索（Web Search）
  - 内容：通过搜索引擎获取的实时网页内容
  - 特点：时效性最强但可信度最低，内容未经验证
  - 注入方式：搜索 → 抓取网页 → 提取正文 → 注入
  - 适用：实时信息（新闻、天气、股价）、知识库未覆盖的问题
  - 注意：必须标注来源和获取时间，用户应被告知信息未经验证
```

### 2. 时效管理（Freshness Management）

每条知识应携带时效元数据：

| 字段 / Field | 说明 / Description | 示例 / Example |
|---|---|---|
| `valid_from` | 知识生效起始时间 | `2025-01-01T00:00:00Z` |
| `valid_until` | 知识失效时间（null 表示永久有效） | `2025-12-31T23:59:59Z` |
| `last_verified` | 最后一次人工验证时间 | `2025-06-15T10:00:00Z` |
| `source_version` | 来源文档版本号 | `v2.3.1` |
| `freshness_score` | 新鲜度评分（0.0-1.0，由系统计算） | `0.85` |

**时效处理规则：**
- `valid_until` 已过期的知识：标记为 `stale`，不注入或降低优先级注入并附加警告。
- `last_verified` 超过 N 天（如 90 天）的知识：标记为 `needs_review`，提醒维护人员更新。
- 同一主题有多版本知识时：优先注入 `valid_until` 最晚的版本。

### 3. 冲突裁决规则（Conflict Adjudication Rules）

当多个来源对同一问题提供矛盾知识时：

```
冲突裁决优先级（从高到低）:
1. 系统提示中的显式规则     — 不可被覆盖
2. 时效性更高的知识         — valid_until 更晚的优先
3. 来源层级更高的知识       — 知识库 > RAG > 联网搜索
4. 人工标注可信度更高的知识 — importance_score 更高的优先
5. 检索相关性得分更高的知识 — similarity_score 更高的优先

如果仍然无法裁决:
→ 注入冲突双方，标注 [CONFLICT] 标记，由 LLM 自行判断或转人工
→ 记录冲突日志，供后续审核
```

### 4. 注入量控制（Injection Volume Control）

```
单次注入 token 预算分配建议（假设总上下文窗口为 128K tokens）:

┌─────────────────────────────────────┬──────────────┬───────────┐
│ 组成部分 / Component                │ Token 预算   │ 占比      │
├─────────────────────────────────────┼──────────────┼───────────┤
│ System Prompt（层级 1）             │ 500-1500     │ ~1%       │
│ 知识库注入（层级 2，按需）           │ 500-2000     │ ~1.5%     │
│ RAG 检索结果（层级 3）              │ 1000-3000    │ ~2.3%     │
│ 联网搜索结果（层级 4，按需）         │ 500-1500     │ ~1.2%     │
│ ─── 知识注入总量上限 ───            │ < 3000       │ < 2.3%    │
│ 对话历史（短期记忆）                 │ 2000-8000    │ ~6%       │
│ 用户当前输入                        │ 变长          │ 变长      │
│ 模型生成预留                        │ 1000-4000    │ ~3%       │
│ ─── 剩余空间留空 ───                │              │           │
└─────────────────────────────────────┴──────────────┴───────────┘

关键原则:
- 单次知识注入总量 < 3000 tokens（硬上限）
- 超过上限时：按优先级截断，保留高分文档
- 每个文档片段建议 200-500 tokens，避免过长片段降低检索精度
```

---

## 决策树 / Decision Tree

```
用户发送消息
    │
    ├─ 消息是否需要外部知识？
    │   ├─ 否（闲聊/通用知识）→ 仅使用 system prompt + 对话历史
    │   └─ 是 → 继续
    │
    ├─ 检查知识库（层级 2）是否有匹配文档
    │   ├─ 是 → 检查时效性
    │   │   ├─ valid_until 未过期 → 注入，标记来源
    │   │   └─ valid_until 已过期 → 标记 stale，降级注入或跳过
    │   └─ 否 → 继续
    │
    ├─ 检查 RAG 检索（层级 3）是否有相关文档
    │   ├─ 是 → 检查相似度得分
    │   │   ├─ score >= 阈值 → 注入，记录来源
    │   │   └─ score < 阈值 → 跳过
    │   └─ 否 → 继续
    │
    ├─ 是否需要实时信息？
    │   ├─ 是 → 执行联网搜索（层级 4）
    │   │   ├─ 获取结果 → 提取正文 → 注入，标注来源和时间
    │   │   └─ 搜索失败 → 降级为"我无法获取最新信息"回复
    │   └─ 否 → 继续
    │
    ├─ 检查注入的各来源之间是否有冲突
    │   ├─ 有冲突 → 执行冲突裁决规则
    │   │   ├─ 可裁决 → 保留胜出方，丢弃败方
    │   │   └─ 不可裁决 → 注入双方并标注 [CONFLICT]
    │   └─ 无冲突 → 继续
    │
    ├─ 检查注入总量是否超过 3000 token 上限
    │   ├─ 是 → 按优先级截断（先截层级 4，再截层级 3）
    │   └─ 否 → 继续
    │
    └─ 组装最终 prompt → 发送给 LLM
```

---

## 模板示例 / Template Examples

### 知识库结构模板 / Knowledge Base Structure Template

```yaml
# knowledge_base_config.yaml — 知识库配置模板

knowledge_base:
  # 元数据配置 / Metadata configuration
  metadata_schema:
    required_fields:
      - doc_id            # 文档唯一标识
      - title             # 文档标题
      - source            # 来源（manual | policy | faq | external）
      - source_url        # 原始链接（如有）
      - tier              # 来源层级（1-4）
      - valid_from        # 生效时间
      - valid_until       # 失效时间（null = 永久）
      - last_verified     # 最后验证时间
      - version           # 版本号
      - importance_score  # 重要性评分（0.0-1.0）
    optional_fields:
      - tags              # 标签列表
      - category          # 分类
      - language          # 语言
      - author            # 作者/维护者
      - related_docs      # 关联文档 ID 列表

  # 文档分块策略 / Document chunking strategy
  chunking:
    strategy: "recursive"         # recursive | fixed_size | semantic | markdown_header
    chunk_size: 400               # 每块目标 token 数
    chunk_overlap: 50             # 块间重叠 token 数
    separators:                   # recursive 模式的分隔符优先级
      - "\n\n"                    # 段落
      - "\n"                      # 行
      - ". "                      # 句子
      - " "                       # 词

  # 索引配置 / Indexing configuration
  indexing:
    embedding_model: "text-embedding-3-small"
    vector_store: "chroma"
    collection_name: "knowledge_base"
    # 混合索引
    keyword_index: true           # BM25 关键词索引
    metadata_index: true          # 元数据过滤索引

  # 检索配置 / Retrieval configuration
  retrieval:
    top_k: 5
    score_threshold: 0.75
    reranker: "none"              # none | cohere | bge-reranker
    metadata_filter:
      enabled: true
      default_filters:
        valid_until: "not_expired"  # 默认过滤已过期文档
    hybrid_search:
      enabled: true
      semantic_weight: 0.7        # 语义检索权重
      keyword_weight: 0.3         # 关键词检索权重

  # 冲突裁决配置 / Conflict adjudication
  conflict_resolution:
    enabled: true
    priority_order:
      - "tier"                    # 来源层级
      - "valid_until"             # 时效性
      - "importance_score"        # 重要性
      - "similarity_score"        # 检索相关性
    unresolved_action: "inject_both"  # inject_both | skip | human_review
    log_conflicts: true

  # 注入控制 / Injection control
  injection:
    max_tokens: 3000              # 单次注入硬上限
    per_chunk_max_tokens: 500     # 单个文档片段最大 token
    include_citation: true        # 是否注入引用信息
    citation_format: "[来源: {title}, 版本: {version}, 更新: {last_verified}]"

  # 时效管理 / Freshness management
  freshness:
    stale_threshold_days: 90      # 超过 N 天未验证标记为 needs_review
    auto_expire: true             # valid_until 过期后自动标记 stale
    stale_injection_warning: "[注意: 此信息可能已过时，最后验证于 {last_verified}]"
```

### 知识文档示例 / Knowledge Document Example

```json
{
  "doc_id": "kb_001",
  "title": "产品退货政策",
  "source": "policy",
  "source_url": "https://internal.example.com/policies/returns",
  "tier": 2,
  "valid_from": "2025-01-01T00:00:00Z",
  "valid_until": "2025-12-31T23:59:59Z",
  "last_verified": "2025-06-15T10:00:00Z",
  "version": "v2.1",
  "importance_score": 0.9,
  "tags": ["退货", "售后", "政策"],
  "category": "customer_service",
  "language": "zh-CN",
  "author": "customer_service_team",
  "related_docs": ["kb_002", "kb_015"],
  "chunks": [
    {
      "chunk_id": "kb_001_c1",
      "content": "退货政策：购买后 7 天内可无理由退货，15 天内可因质量问题退货。退货商品需保持原包装完好。",
      "metadata": {
        "section": "退货条件",
        "page": 1
      }
    },
    {
      "chunk_id": "kb_001_c2",
      "content": "退款方式：原路退回，到账时间 3-5 个工作日。如使用优惠券支付的部分，优惠券将返还。",
      "metadata": {
        "section": "退款方式",
        "page": 2
      }
    }
  ]
}
```

### 注入后的 Prompt 结构示例 / Injected Prompt Structure Example

```text
[System Prompt — 层级 1]
你是一个客服助手。你的职责是帮助用户解决售后问题。
你必须遵守以下规则：
1. 不得承诺超出政策范围的补偿
2. 涉及退款金额超过 5000 元时，需转人工处理

[Knowledge Base — 层级 2]
[来源: 产品退货政策, 版本: v2.1, 更新: 2025-06-15]
退货政策：购买后 7 天内可无理由退货，15 天内可因质量问题退货。退货商品需保持原包装完好。
退款方式：原路退回，到账时间 3-5 个工作日。

[RAG Results — 层级 3]
[来源: 售后FAQ, 相似度: 0.89]
Q: 退货时需要提供什么凭证？
A: 需要提供订单号和购买凭证（电子发票或纸质发票均可）。

[Conversation History]
User: 我买了三天的东西想退货
Assistant: 您好，请问商品包装是否完好？

[User Input]
User: 包装没拆过，但是找不到发票了
```

---

## 常见陷阱 / Common Pitfalls

### 1. 过度注入导致上下文稀释 / Over-Injection Causing Context Dilution
- **问题：** 注入过多知识文档，导致关键信息被稀释，模型反而难以找到正确答案。
- **解决方案：** 严格控制 top-k 数量（建议 3-5），设置相似度阈值，使用 reranker 提升精度。

### 2. 忽略时效性导致错误回答 / Ignoring Freshness Leading to Wrong Answers
- **问题：** 注入了已过期的知识（如旧版价格表），用户得到错误信息。
- **解决方案：** 强制时效检查，过期知识标记 `stale` 并降级或拒绝注入。

### 3. 来源冲突未处理 / Unhandled Source Conflicts
- **问题：** 知识库和 RAG 检索到矛盾信息，模型随机选择一个，导致回答不一致。
- **解决方案：** 实施冲突裁决规则，记录冲突日志，不可裁决时标注 [CONFLICT] 或转人工。

### 4. 联网搜索结果未验证 / Unverified Web Search Results
- **问题：** 直接将搜索结果注入上下文，可能包含错误信息或恶意内容。
- **解决方案：** 标注来源和时间，提示用户信息未经验证，对搜索结果做基本内容安全检查。

### 5. 注入格式混乱 / Messy Injection Format
- **问题：** 知识文档以不同格式注入，模型难以区分来源和边界。
- **解决方案：** 使用统一的注入模板（如 `[来源: {title}] ... [END]`），明确标注文档边界。

### 6. Token 预算未硬性限制 / No Hard Token Budget
- **问题：** 没有设置注入上限，RAG 返回大量文档耗尽上下文窗口。
- **解决方案：** 设置 `max_tokens` 硬上限（建议 < 3000），超限时按优先级截断。

---

## 检查清单 / Checklist

### 设计阶段 / Design Phase
- [ ] 已定义四级来源层级及其优先级
- [ ] 已设计知识文档的元数据 schema（包含时效字段）
- [ ] 已制定冲突裁决规则
- [ ] 已设定注入 token 上限（< 3000）
- [ ] 已确定文档分块策略

### 实现阶段 / Implementation Phase
- [ ] 知识文档入库时自动填充时效元数据
- [ ] 检索时自动过滤已过期文档
- [ ] 联网搜索结果标注来源和时间
- [ ] 冲突检测逻辑已实现并记录日志
- [ ] 注入格式统一且有明确边界标记
- [ ] Token 计数器已实现，超限自动截断

### 测试阶段 / Testing Phase
- [ ] 已测试单来源注入的正确性
- [ ] 已测试多来源冲突场景的裁决
- [ ] 已测试过期知识被正确过滤
- [ ] 已测试注入 token 超限时的截断行为
- [ ] 已测试联网搜索结果的标注和提示
- [ ] 已测试知识库更新后旧版本被正确替换

### 运维阶段 / Operations Phase
- [ ] 知识文档有定期审核和更新流程
- [ ] `needs_review` 标记的知识有提醒机制
- [ ] 冲突日志有定期分析和处理
- [ ] 注入 token 消耗有监控
- [ ] 知识库版本变更有审计记录
