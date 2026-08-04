---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 用户要查看记忆系统的具体配置/存储模板示例
terminates_when: T    # 已获取所需模板（YAML 配置 / JSON 存储）
provides: π           # 记忆配置模板（短期/长期/情景/知识图谱/用户建模/遗忘/注入）、情景记忆存储 JSON 示例
interface: R          # 输入=记忆系统类型与参数需求；输出=YAML 配置块 / JSON 存储示例
---

# 记忆系统模板示例 (Memory Systems Templates)

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
