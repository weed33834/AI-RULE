# Memory Systems Architecture / 记忆系统架构设计

---

## 一句话描述 / One-Sentence Description

**中文：** 记忆系统是智能体在时间维度上保持信息连续性的架构层，通过分层存储、优先注入和主动遗忘机制，使智能体在单次对话和跨会话场景中都能做出上下文一致的决策。

**English:** A memory system is the architectural layer that maintains information continuity over time for an agent, enabling context-consistent decisions within a single conversation and across sessions through tiered storage, priority-based injection, and active forgetting mechanisms.

---

## 适用场景 / Applicable Scenarios

| 场景 / Scenario | 记忆类型 / Memory Type | 说明 / Description |
|---|---|---|
| 多轮对话上下文保持 / Multi-turn dialogue context | 短期记忆 / Short-term | 对话窗口内的消息历史 |
| 用户个性化偏好 / User personalization | 情景记忆 / Episodic | 跨会话记住用户习惯、偏好、历史交互 |
| 知识库问答 / Knowledge base QA | 长期记忆 / Long-term | 持久化的领域知识，通过 RAG 检索 |
| 任务连续性 / Task continuity | 长期记忆 + 情景记忆 | 跨会话恢复未完成的任务状态 |
| 多智能体协作 / Multi-agent collaboration | 共享长期记忆 / Shared long-term | 多个智能体共享同一记忆存储 |
| 复杂实体关系推理 / Complex entity-relationship reasoning | 知识图谱记忆 / Knowledge Graph | 跨时间的多实体关系查询（谁依赖什么、何时变更） |
| 用户心智模型 / User mental model | 用户深度建模 / User Deep Modeling | 跨会话推导用户是什么样的人（偏好/习惯/水平） |

---

## 核心方法论 / Core Methodology

### 1. 三层记忆架构（+ 可选知识图谱层）/ Three-Tier Memory Architecture (+ optional KG tier)

#### 1.1 短期记忆（Short-Term Memory / Working Memory）

- **定义：** 当前对话窗口内的上下文信息，存在于 LLM 的上下文窗口中。
- **生命周期：** 单次会话内有效，会话结束后清除（或归档到长期记忆）。
- **实现方式：**
  - 直接将对话历史拼接到 prompt 中。
  - LangChain 中的对应模块：
    - `ConversationBufferMemory`：存储完整对话历史，不做压缩。
    - `ConversationBufferWindowMemory`：只保留最近 N 轮对话，控制 token 消耗。
    - `ConversationSummaryMemory`：使用 LLM 将历史对话压缩为摘要，适合长对话。
    - `ConversationSummaryBufferMemory`：混合策略，保留近期原文 + 旧对话摘要。
- **容量限制：** 受模型上下文窗口大小限制（如 GPT-4o 为 128K tokens，Claude 3.5 Sonnet 为 200K tokens — 需验证最新值）。

#### 1.2 长期记忆（Long-Term Memory / Persistent Memory）

- **定义：** 跨会话持久化存储的信息，不直接存在于上下文窗口中，需要时通过检索注入。
- **生命周期：** 永久存储，除非被遗忘策略主动清除。
- **实现方式：**
  - 向量数据库存储 + 语义检索（RAG）。
  - 常用向量数据库：Pinecone、Weaviate、Chroma、Qdrant、Milvus、FAISS。
  - LangChain 中的对应模块：`VectorStoreRetrieverMemory`，将对话历史存入向量存储，按语义相关性检索。
- **存储内容：** 领域知识、事实数据、历史交互摘要、用户画像。

#### 1.3 情景记忆（Episodic Memory / User-Specific Memory）

- **定义：** 记录与特定用户、特定时间、特定事件绑定的记忆，包含时间戳和上下文元数据。
- **生命周期：** 持久化存储，带有有效期和衰减机制。
- **实现方式：**
  - 结构化存储（如 JSON/数据库记录），包含 `user_id`、`timestamp`、`event_type`、`content`、`metadata` 字段。
  - 可与向量检索结合，实现"该用户上次提到的 X"这类查询。
- **典型应用：** "您上次说喜欢吃辣，今天想吃川菜吗？"

#### 1.4 知识图谱记忆（Knowledge Graph Memory / 可选第4层）

> **可选层**：知识图谱是长期记忆的高级形态，并非替代三层记忆，而是叠加其上。简单 FAQ 场景不需要；涉及多实体、跨时间推理的场景才启用。启用前必须评估存储与检索成本。
>
> **Optional tier**: The knowledge graph is an advanced form of long-term memory — it does NOT replace the three tiers, it layers on top. Enable only for multi-entity, cross-time reasoning. Assess storage and retrieval cost before enabling.

- **定义：** 以图结构存储实体及其关系，并给每条事实打上时间戳，支持"何时为真"的时间推理。
- **来源：** Zep / Graphiti 时序知识图谱架构。
- **核心能力：**
  - **实体记忆（Entity Memory）**：自动从对话/工具返回中提取实体（人名、项目名、概念、文档、API），并维护实体间关系（`depends_on`、`belongs_to`、`references`、`conflicts_with`、`authored_by` 等）。
  - **时态记忆（Temporal Memory）**：每条事实带 `valid_at`（何时开始为真）和 `invalid_at`（何时失效，可为 null 表示当前仍为真）。支持查询"X 在 2026-03 时是不是 Y"或"X 现在还是 Y 吗"。
  - **三层子图结构**：
    ```
    Episode 子图（原始交互日志）
        │  抽取/归一化
        ▼
    语义实体子图（实体 + 关系 + 时态）
        │  聚类
        ▼
    社区子图（实体聚类形成主题，支持高层摘要）
    ```

##### 1.4.1 架构图 / Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    知识图谱记忆层 / KG Memory Tier              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐   提取    ┌────────────────┐             │
│  │ Episode 子图    │ ────────▶│ 语义实体子图     │             │
│  │ (raw episodes)  │  extract │ (entities +     │             │
│  │ 原始对话/工具日志│          │  relations +    │             │
│  └────────────────┘          │  timestamps)    │             │
│                              └────────┬────────┘             │
│                                       │ 聚类 cluster          │
│                                       ▼                       │
│                              ┌────────────────┐               │
│                              │ 社区子图         │               │
│                              │ (communities)   │               │
│                              │ 主题级摘要       │               │
│                              └────────────────┘               │
│                                                              │
│  时态字段 / Temporal fields:                                  │
│    valid_at:   <datetime>   何时开始为真 / when it became true│
│    invalid_at: <datetime|null>  何时失效 / when it ceased   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

##### 1.4.2 数据模型 / Data Model

```json
// 实体节点 / Entity node
{
  "entity_id": "ent_proj_AgentCreater",
  "type": "project",
  "name": "AgentCreater",
  "attributes": { "repo": "gitcode.com/badhope/AI-RULE" },
  "valid_at": "2026-07-12T00:00:00Z",
  "invalid_at": null,
  "source_episode_id": "ep_20260712_001"
}

// 关系边 / Relation edge
{
  "edge_id": "rel_owner_001",
  "from": "ent_proj_AgentCreater",
  "to": "ent_person_user",
  "relation": "owned_by",
  "valid_at": "2026-07-12T00:00:00Z",
  "invalid_at": null,
  "source_episode_id": "ep_20260712_001"
}

// 时态查询示例 / Temporal query example:
// "2026-03 时 AgentCreater 的 owner 是谁？"
//   → 匹配 valid_at <= 2026-03 且 (invalid_at is null OR invalid_at > 2026-03) 的 owned_by 边
```

##### 1.4.3 检索策略 / Retrieval Strategy

```
知识图谱检索流程:
1. 用户输入 → 识别查询中的实体与时间限定词
2. 在语义实体子图中定位种子实体（可结合向量检索做实体链接）
3. 沿关系边做 1-2 跳扩展（避免全图遍历，控制成本）
4. 应用时态过滤：valid_at <= query_time AND (invalid_at IS NULL OR invalid_at > query_time)
5. （可选）从社区子图取主题级摘要作为高层背景
6. 将命中的实体+关系序列化为自然语言或 JSON 注入上下文
```

- **与三层记忆的关系**：知识图谱命中结果作为长期记忆的一种"高结构化"注入源，参与 §2 注入优先级排序（通常位于 RAG 检索结果附近，按相关性打分）。
- **成本控制**：图遍历深度建议 ≤ 2 跳；每次注入的实体数建议 ≤ 20；社区摘要按需加载，不全量预载。

### 2. 注入策略（Injection Strategy / Priority-Based Retrieval）

当可用记忆超过上下文容量时，按优先级排序注入：

```
优先级排序规则（从高到低）:
1. 系统提示（System Prompt）        — 始终最高优先级，不可被记忆覆盖
2. 当前对话上下文（最近 N 轮）       — 短期记忆，保持连贯性
3. 用户画像与偏好（User Profile）    — 情景记忆，个性化基础
4. RAG 检索结果（按相关性得分排序）   — 长期记忆，补充知识
5. 历史摘要（Conversation Summary）  — 长期记忆，背景信息
```

**注入量控制：** 单次注入的记忆总量应控制在上下文窗口的 20%-30% 以内，为用户输入和模型生成预留空间。

### 3. 遗忘策略（Forgetting Strategy）

| 策略 / Strategy | 触发条件 / Trigger | 行为 / Action |
|---|---|---|
| 过时降权 / Decay | 记忆超过有效期或长时间未被访问 | 降低检索权重（如时间衰减因子），不立即删除 |
| 冲突取新 / Conflict Resolution | 新记忆与旧记忆矛盾 | 保留新记忆，归档或删除旧记忆，记录冲突日志 |
| 敏感即删 / Sensitive Deletion | 检测到 PII、凭证、敏感数据 | 立即删除，不可恢复 |
| 容量淘汰 / Capacity Eviction | 记忆条数超过上限 | 淘汰权重最低的记忆（LRU + 重要性评分） |
| 用户主动删除 / User-Initiated | 用户请求删除特定记忆 | 立即删除，记录审计日志 |

**时间衰减公式（参考）：**
```
score_final = score_relevance * decay_factor
decay_factor = exp(-lambda * days_since_last_access)
# lambda 为衰减速率，典型值 0.01-0.1（需根据场景调优）
```

### 3.1 用户深度建模（User Deep Modeling / 可选层）

> **可选层**：与知识图谱记忆并列的可选高级层。跨会话构建用户心智模型，从"用户发生了什么"（情景记忆）推导"用户是什么样的人"。
>
> **Optional tier**: An optional advanced tier alongside the knowledge graph. Builds a cross-session user mental model, inferring "what kind of person the user is" from "what happened to the user" (episodic memory).

- **与情景记忆的区别**：
  | 维度 | 情景记忆 / Episodic | 用户建模 / User Modeling |
  |------|--------------------|--------------------------|
  | 回答的问题 | 用户发生了什么 | 用户是什么样的人 |
  | 数据形态 | 事件记录（带时间戳） | 推导出的画像（带置信度） |
  | 示例 | "用户这次说要用 TypeScript" | "该用户偏好静态类型语言（推测，置信度 0.7）" |
  | 更新方式 | 追加新事件 | 新事件触发现有画像的重估 |
  | 来源 | Hermes Agent + Honcho 用户建模 | 同左 |

- **建模维度 / Modeling Dimensions**：
  1. **技术栈偏好 / Tech-stack preference**：用户倾向使用的语言、框架、库（如偏好 React 而非 Vue）。
  2. **代码风格偏好 / Code-style preference**：命名风格、注释详略、错误处理风格、模块化程度。
  3. **沟通详略偏好 / Communication-detail preference**：用户希望简洁结论还是详细解释；偏代码还是偏文字。
  4. **常见错误模式 / Common error patterns**：用户反复犯的错误（如忘记 await、混淆 == 和 ===），用于主动提醒。
  5. **知识水平估计 / Knowledge-level estimate**：在哪些领域是新手、在哪些领域是专家，用于调整解释深度。

- **建模流程 / Modeling Process**：
  ```
  1. 事件采集：从情景记忆中读取该用户的近期交互（偏好声明、行为信号、反馈）
  2. 特征提取：从事件中提取可量化的特征（如"使用 TypeScript 的比例 = 0.8"）
  3. 画像推导：用规则或小模型从特征推导画像项，每项带置信度（0.0-1.0）
  4. 一致性校验：新画像与旧画像冲突时，保留置信度更高者，记录变更日志
  5. 注入使用：在响应生成前，将高置信度画像项作为"用户上下文"注入（低置信度不注入）
  6. 周期重估：每周/每月用最新事件重估全部画像项，置信度衰减过期画像
  ```

- **隐私约束（P0 级，不可例外）/ Privacy Constraints (P0, never excusable)**：
  - **不上传**：用户建模数据仅存本地（或用户自有存储），不上传到任何第三方服务。
  - **不共享**：用户 A 的画像绝不注入到用户 B 的上下文；跨用户聚合统计须先脱敏。
  - **可删除**：用户可随时查看全部画像项，并要求删除某项或全部；删除即立即生效并记录审计日志。
  - **推测标注**：所有画像结论注入上下文时必须带"推测："前缀和置信度，不得作为事实陈述给用户。
  - **合规适配**：画像数据按 GDPR / PIPL / CCPA 的"用户画像"条款处理，提供导出与删除接口。

- **来源**：Hermes Agent 用户建模 + Honcho（Plastic Labs）用户心智模型。

### 4. 索引机制（Indexing / RAG Retrieval）

```
检索流程:
1. 用户输入 → 生成 query embedding
2. 在向量数据库中进行 top-k 语义检索（k 通常为 3-10）
3. 可选：结合元数据过滤（如 user_id、time_range、event_type）
4. 可选：重排序（reranking）提升精度（如使用 Cohere Rerank、bge-reranker）
5. 按优先级注入到上下文中
```

**混合检索（Hybrid Retrieval）：** 语义检索 + 关键词检索（BM25）结合，提升召回率。LangChain 支持 `EnsembleRetriever` 实现混合检索。

---

## 决策树 / Decision Tree

```
用户发送消息
    │
    ├─ 是否包含敏感信息（PII/凭证）？
    │   ├─ 是 → 触发敏感即删策略，不存储该消息
    │   └─ 否 → 继续
    │
    ├─ 当前对话上下文是否超出窗口限制？
    │   ├─ 是 → 触发摘要压缩（旧消息 → 摘要），保留近期原文
    │   └─ 否 → 直接拼接到上下文
    │
    ├─ 是否需要跨会话记忆？
    │   ├─ 否 → 仅使用短期记忆
    │   └─ 是 → 继续
    │       │
    │       ├─ 提取可持久化信息（用户偏好、事实、决策）
    │       ├─ 检查是否与已有记忆冲突
    │       │   ├─ 冲突 → 冲突取新，归档旧记忆
    │       │   └─ 无冲突 → 存入长期/情景记忆
    │       └─ 为新记忆建立向量索引 + 元数据索引
    │
    ├─ 下一轮对话时，需要检索哪些记忆？
    │   ├─ 计算用户输入的 query embedding
    │   ├─ 向量检索 top-k 相关记忆
    │   ├─ 元数据过滤（user_id、时间范围）
    │   ├─ 应用时间衰减权重
    │   ├─ 是否启用知识图谱层？
    │   │   ├─ 是 → 识别查询中的实体与时间限定词
    │   │   │       ├─ 在语义实体子图定位种子实体（可结合向量检索做实体链接）
    │   │   │       ├─ 沿关系边 1-2 跳扩展
    │   │   │       ├─ 应用时态过滤（valid_at / invalid_at）
    │   │   │       ├─ （可选）取社区子图主题摘要
    │   │   │       └─ 将命中实体+关系序列化后参与注入排序
    │   │   └─ 否 → 跳过知识图谱检索
    │   └─ 按优先级排序后注入上下文
    │
    └─ 记忆总量是否超过容量上限？
        ├─ 是 → 淘汰权重最低的记忆
        └─ 否 → 无操作
```

---

## 模板示例 / Template Examples

### 记忆配置模板 / Memory Configuration Template

```yaml
# memory_config.yaml — 记忆系统配置模板

memory_system:
  # 短期记忆配置 / Short-term memory
  short_term:
    type: "buffer_window"          # buffer | buffer_window | summary | summary_buffer
    window_size: 20                # 保留最近 N 条消息（buffer_window 模式）
    max_tokens: 4000               # 短期记忆最大 token 数
    summary_trigger: 3000          # 超过此 token 数时触发摘要压缩
    summary_model: "gpt-4o-mini"   # 用于生成摘要的模型

  # 长期记忆配置 / Long-term memory
  long_term:
    enabled: true
    vector_store:
      type: "chroma"               # chroma | pinecone | weaviate | qdrant | milvus | faiss
      collection_name: "agent_memory"
      embedding_model: "text-embedding-3-small"  # OpenAI embedding 模型
      # 对于 chroma：
      persist_path: "./data/chroma"
      # 对于 pinecone（需验证最新 API）：
      # api_key_env: "PINECONE_API_KEY"
      # environment: "us-east-1-aws"
    retrieval:
      top_k: 5                     # 检索返回的文档数量
      score_threshold: 0.7         # 相似度阈值，低于此值不注入
      reranker: "none"             # none | cohere | bge-reranker
      hybrid_search: true          # 是否启用混合检索（语义+BM25）

  # 情景记忆配置 / Episodic memory
  episodic:
    enabled: true
    storage:
      type: "sqlite"               # sqlite | postgres | mongodb
      path: "./data/episodic.db"
    schema:
      fields:
        - name: "memory_id"
          type: "uuid"
          primary_key: true
        - name: "user_id"
          type: "string"
          indexed: true
        - name: "timestamp"
          type: "datetime"
          indexed: true
        - name: "event_type"
          type: "string"           # preference | decision | interaction | fact
          indexed: true
        - name: "content"
          type: "text"
        - name: "metadata"
          type: "json"
        - name: "importance_score"
          type: "float"            # 0.0 - 1.0
        - name: "expiry_date"
          type: "datetime"
          nullable: true
        - name: "embedding_id"
          type: "string"           # 关联向量数据库中的 ID

  # 知识图谱记忆配置 / Knowledge graph memory（可选第4层）
  knowledge_graph:
    enabled: false                 # 默认关闭；仅多实体、跨时间推理场景启用
    backend: "neo4j"               # neo4j | memgraph | graphiti | zep | in-memory
    # 对于 neo4j（需验证最新 API）：
    # uri_env: "NEO4J_URI"
    # user_env: "NEO4J_USER"
    # password_env: "NEO4J_PASSWORD"
    entity_extraction:
      model: "gpt-4o-mini"         # 用于从对话/工具返回中抽取实体的模型
      entity_types:                # 需提取的实体类型
        - "person"
        - "project"
        - "concept"
        - "document"
        - "api"
      relation_types:              # 需维护的关系类型
        - "depends_on"
        - "belongs_to"
        - "references"
        - "conflicts_with"
        - "authored_by"
        - "owned_by"
    temporal:
      enabled: true                # 必须启用时态字段 valid_at / invalid_at
      default_valid_at: "now"      # 未明确时默认取当前时间
    subgraphs:
      episode: true                # Episode 子图（原始交互日志）
      semantic_entity: true        # 语义实体子图（实体+关系+时态）
      community: true              # 社区子图（实体聚类）
      community_algorithm: "louvain"  # louvain | leiden（需验证实现可用性）
    retrieval:
      max_hops: 2                  # 图遍历最大跳数（建议 ≤ 2）
      max_entities_per_injection: 20  # 单次注入最大实体数
      load_community_summary_on_demand: true  # 社区摘要按需加载，不全量预载
    cost_guard:
      warn_on_entities_above: 10000  # 实体数超此值告警
      warn_on_edges_above: 50000     # 关系数超此值告警

  # 用户深度建模配置 / User deep modeling（可选层）
  user_modeling:
    enabled: false                 # 默认关闭；启用须满足隐私约束
    storage:
      type: "sqlite"               # 仅本地存储；禁止上传第三方
      path: "./data/user_model.db"
    dimensions:                    # 建模维度
      - "tech_stack_preference"
      - "code_style_preference"
      - "communication_detail_preference"
      - "common_error_patterns"
      - "knowledge_level_estimate"
    recompute:
      interval: "weekly"           # weekly | monthly
      confidence_decay_per_week: 0.05  # 每周置信度衰减
    injection:
      min_confidence: 0.6          # 低于此置信度的画像项不注入
      prefix: "推测："             # 注入时强制前缀（中文）
      prefix_en: "Speculation:"    # 注入时强制前缀（英文）
    privacy:                       # P0 级约束，不可例外
      upload: false                # 永不上传
      cross_user_share: false      # 永不跨用户共享
      user_exportable: true        # 用户可导出
      user_deletable: true         # 用户可删除
      audit_log: true              # 删除/查看记录审计日志

  # 遗忘策略配置 / Forgetting strategy
  forgetting:
    decay:
      enabled: true
      lambda: 0.05                 # 时间衰减速率
      min_score: 0.1               # 低于此权重的记忆可被淘汰
    conflict_resolution: "newest_wins"  # newest_wins | merge | manual_review
    sensitive_deletion:
      enabled: true
      patterns:                    # 敏感信息检测模式
        - "credit_card"
        - "ssn"
        - "password"
        - "api_key"
        - "phone_number"
        - "email_address"
      action: "immediate_delete"   # immediate_delete | redact_and_store
    capacity_limit:
      max_memories: 10000          # 最大记忆条数
      eviction_policy: "lru_with_importance"  # lru | lru_with_importance | fifo

  # 注入策略配置 / Injection strategy
  injection:
    max_injection_tokens: 3000     # 单次注入最大 token 数
    priority_order:                # 优先级从高到低
      - "system_prompt"
      - "recent_context"           # 最近 N 轮对话
      - "user_profile"             # 用户画像
      - "rag_results"              # RAG 检索结果
      - "conversation_summary"     # 历史摘要
    include_metadata: true         # 注入时是否包含记忆元数据（时间戳等）
```

### 情景记忆存储示例 / Episodic Memory Storage Example

```json
{
  "memory_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_12345",
  "timestamp": "2025-06-15T14:30:00Z",
  "event_type": "preference",
  "content": "用户表示偏好简洁的回复风格，不需要过多解释",
  "metadata": {
    "session_id": "sess_abc123",
    "confidence": 0.95,
    "source": "explicit_statement"
  },
  "importance_score": 0.85,
  "expiry_date": null,
  "embedding_id": "vec_mem_550e8400"
}
```

---

## 常见陷阱 / Common Pitfalls

### 1. 上下文窗口溢出 / Context Window Overflow
- **问题：** 将所有历史对话和检索结果全部注入，导致超出模型上下文窗口。
- **解决方案：** 设置注入 token 上限，使用摘要压缩和窗口限制。

### 2. 记忆幻觉 / Memory Hallucination
- **问题：** RAG 检索到语义相似但实际无关的记忆，导致智能体基于错误信息生成回复。
- **解决方案：** 设置相似度阈值，使用 reranker 提升精度，对检索结果进行相关性二次校验。

### 3. 用户记忆串扰 / Cross-User Memory Contamination
- **问题：** 检索时未按 `user_id` 过滤，导致 A 用户的记忆被注入到 B 用户的上下文中。
- **解决方案：** 检索时强制添加 `user_id` 元数据过滤条件。

### 4. 过期信息干扰 / Stale Information Interference
- **问题：** 旧的记忆未被遗忘或降权，与新的用户偏好冲突，导致回复不一致。
- **解决方案：** 实施时间衰减策略 + 冲突检测机制。

### 5. 敏感数据泄露 / Sensitive Data Leakage
- **问题：** 用户在对话中透露的敏感信息（密码、密钥）被持久化存储，存在泄露风险。
- **解决方案：** 在存储前进行敏感信息检测，匹配到的立即删除或脱敏处理。

### 6. 检索延迟影响体验 / Retrieval Latency Impact
- **问题：** 向量检索 + reranking 导致响应延迟增加。
- **解决方案：** 异步预检索（预测用户可能的后续问题），缓存高频检索结果，控制 top-k 数量。

### 7. 知识图谱全图遍历 / Full-Graph Traversal
- **问题：** 启用知识图谱层后，无深度限制的图遍历导致检索成本爆炸、响应超时。
- **解决方案：** 强制限制最大跳数（建议 ≤ 2 跳），限制单次注入实体数（建议 ≤ 20），社区摘要按需加载。

### 8. 时态记忆失效未更新 / Stale Temporal Facts
- **问题：** 实体关系已变更（如负责人换了），但旧关系的 `invalid_at` 未填写，导致时态查询返回过期结论。
- **解决方案：** 提取新关系时，自动给冲突的旧关系补填 `invalid_at`；定期扫描 `invalid_at IS NULL` 但已有更新关系的边。

### 9. 用户画像当事实陈述 / User Profile Stated as Fact
- **问题：** 把推导出的用户画像（"该用户偏好简洁回复"）当作事实直接陈述给用户，侵犯隐私且可能冒犯。
- **解决方案：** 画像项注入上下文时强制带"推测："前缀与置信度；画像仅用于调整自身行为，不主动对用户复述。

### 10. 用户画像跨用户串扰 / Cross-User Profile Contamination
- **问题：** 用户 A 的画像被注入到用户 B 的上下文（如共享缓存未按 user_id 隔离）。
- **解决方案：** 画像存储与检索强制按 `user_id` 过滤；跨用户聚合统计须先脱敏；画像数据永不上传、永不共享。

---

## 检查清单 / Checklist

### 设计阶段 / Design Phase
- [ ] 已明确三层记忆（短期/长期/情景）的职责边界
- [ ] 已选择合适的向量数据库并验证其性能基准
- [ ] 已定义记忆的 schema（字段、类型、索引）
- [ ] 已制定注入优先级规则和 token 上限
- [ ] 已设计遗忘策略（衰减/冲突/敏感删除/容量淘汰）
- [ ] 是否启用知识图谱层已决策（默认关闭；多实体跨时间推理才启用）
- [ ] 是否启用用户深度建模层已决策（默认关闭；启用须满足隐私约束）
- [ ] 若启用知识图谱：实体/关系类型、时态字段、子图结构已定义
- [ ] 若启用用户建模：建模维度、置信度阈值、隐私约束已定义

### 实现阶段 / Implementation Phase
- [ ] 短期记忆已实现窗口限制或摘要压缩
- [ ] 向量检索已配置元数据过滤（至少包含 user_id）
- [ ] 敏感信息检测已在存储前生效
- [ ] 冲突检测逻辑已实现并记录日志
- [ ] 记忆注入总量已设置硬上限
- [ ] 检索结果已设置相似度阈值
- [ ] 若启用知识图谱：时态过滤（valid_at/invalid_at）已实现，图遍历深度已限制
- [ ] 若启用用户建模：画像项注入时已带"推测："前缀与置信度，低置信度不注入

### 测试阶段 / Testing Phase
- [ ] 已测试跨会话记忆连续性
- [ ] 已测试多用户场景下的记忆隔离
- [ ] 已测试上下文窗口溢出场景
- [ ] 已测试敏感信息删除逻辑
- [ ] 已测试冲突记忆的裁决逻辑
- [ ] 已测试检索延迟在可接受范围内
- [ ] 若启用知识图谱：已测试时态查询（历史时点 vs 当前）与图遍历成本
- [ ] 若启用用户建模：已测试用户画像删除接口与跨用户隔离

### 运维阶段 / Operations Phase
- [ ] 记忆存储容量有监控告警
- [ ] 记忆删除有审计日志
- [ ] 向量索引性能有定期评估
- [ ] 遗忘策略参数有定期调优
- [ ] 用户数据删除请求（如 GDPR）有处理流程

## 进阶：12 项高级架构模式 / Advanced: 12 Architecture Patterns

> 本文档的记忆系统设计在 `advanced-patterns.md` 中有进一步的架构扩展：
> - **模式 11（GraphRAG / Agentic RAG）**：三层进阶——GraphRAG（基于知识图谱跨文档全局查询）/ CRAG（检索质量评估→重新检索/网页搜索）/ Self-RAG（模型自主决定何时检索）。与知识图谱记忆的关系：检索策略 vs 记忆存储，可叠加使用。来源微软 GraphRAG 2024 / CRAG / Self-RAG。
