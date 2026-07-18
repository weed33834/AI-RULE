# 故事知识图谱 (Story Knowledge Graph)

> 故事知识图谱是 AGENTS.md §6.3 的详细实施指南。
> 图谱将角色、情节、世界观信息结构化为可查询的知识网络，支持一致性检查、伏笔追踪和全局查询。

## §1 图谱构建流程

### 1.1 初始化
```
.ai-memory/story-graph/
├── nodes/          # 实体节点
│   ├── characters.jsonl    # Character 节点
│   ├── locations.jsonl     # Location 节点
│   ├── events.jsonl        # Event 节点
│   ├── items.jsonl         # Item 节点
│   ├── concepts.jsonl      # Concept 节点（世界观规则）
│   └── plot-threads.jsonl  # PlotThread 节点
├── edges/          # 关系边
│   └── relations.jsonl     # 所有关系边
└── timeline.jsonl  # 时态信息
```

### 1.2 节点创建时机
| 节点类型 | 创建时机 | 创建方式 |
|----------|----------|----------|
| Character | 角色首次出场时 | 从角色卡自动导入 |
| Location | 新地点出现时 | 手动或从场景描述提取 |
| Event | 重大事件发生时 | 写作后手动记录 |
| Item | 重要道具出现时 | 手动记录 |
| Concept | 世界观规则确立时 | 从 `.ai-memory/worldbuilding.md` 导入 |
| PlotThread | 伏笔埋设时 | 自动从 plot-threads.md 同步 |

## §2 实体 Schema

### Character
```json
{
  "id": "char_001",
  "type": "Character",
  "name": "林默",
  "aliases": ["默哥", "老林"],
  "age": 28,
  "personality_tags": ["冷静", "固执", "重情义"],
  "abilities": ["剑术-中级", "观察力-高级"],
  "faction": "游侠",
  "status": "alive",
  "arc_stage": "挣扎期",
  "first_appearance": "ch1"
}
```

### Event
```json
{
  "id": "evt_005",
  "type": "Event",
  "name": "仓库对峙",
  "participants": ["char_001", "char_003"],
  "timeline_position": "ch3-scene2",
  "cause": "evt_003",
  "effects": ["evt_008"],
  "impact_scope": "主角与反派首次正面冲突"
}
```

### PlotThread
```json
{
  "id": "pt_002",
  "type": "PlotThread",
  "name": "灰鸦左手缺失之谜",
  "status": "pending",
  "planted_chapter": "ch3",
  "expected_payoff": "ch8",
  "actual_payoff": null,
  "related_characters": ["char_003"]
}
```

## §3 关系边 Schema

```json
{
  "from": "char_001",
  "to": "char_003",
  "type": "rival-of",
  "since": "ch3",
  "until": null,
  "note": "仓库对峙后结为对手"
}
```

### 关系类型详表
| 关系 | 含义 | 时态变化示例 |
|------|------|-------------|
| `knows` | 认识 | ch1 相识 → ch5 深交 |
| `related-to` | 亲属 | 永久（除非揭示非亲属） |
| `rival-of` | 对手 | ch3 结仇 → ch10 化解 |
| `allied-with` | 盟友 | ch5 结盟 → ch8 背叛 |
| `located-at` | 位于 | 场景定位 |
| `participates-in` | 参与 | 事件角色追踪 |
| `owns` | 持有 | ch2 获得 → ch7 丢失 |
| `causes` | 导致 | 事件因果链 |
| `foreshadows` | 伏笔指向 | ch3 埋设 → ch8 回收 |
| `contradicts` | 矛盾 | **P0 警报** |

## §4 图谱查询

### 常用查询
```python
# 1. 角色关系网络
def get_character_relations(char_id, chapter=None):
    """返回角色在指定章节时的所有关系"""
    # 如果指定 chapter，按时态过滤

# 2. 未回收伏笔
def get_pending_foreshadowing():
    """返回所有 status=pending 的 PlotThread"""

# 3. 事件因果链
def trace_causal_chain(event_id):
    """从事件 A 追溯到根因"""

# 4. 信息传播路径
def what_character_knows(char_id, at_chapter):
    """返回角色在指定章节时应知道的所有信息"""

# 5. 角色出场统计
def character_appearance_stats():
    """返回每个角色的出场章节和频率"""
```

## §5 一致性自动检查

### `contradicts` 边生成规则
- 角色行为与性格标签不符 → 生成 `contradicts` 边，标记为 P0。
- 角色能力超出设定上限 → 生成 `contradicts` 边，标记为 P0。
- 世界观规则被违反 → 生成 `contradicts` 边，标记为 P0。
- 时间线矛盾（角色在第 3 章知道第 5 章的信息）→ 生成 `contradicts` 边，标记为 P0。

### 检查触发时机
- 章节写入后（PostToolUse hook）。
- 手动触发 `/consistency` 命令。

## §6 与 GraphRAG 的关系

> 故事知识图谱是存储层（实体+关系+时态），GraphRAG 是检索策略层。
> 详见 `creative-evaluation.md` 模式 11（创意 GraphRAG / Agentic RAG）：
> - **GraphRAG**：基于图谱的全局查询（"所有角色关系网络""所有未回收伏笔"）。
> - **CRAG**：检索结果质量评估 + 补充。
> - **Self-RAG**：写到角色 A 遇到 B 时，自主决定是否查询他们的历史关系。

## §7 图谱维护

### 增量更新
- 写作过程中每新增一个角色/事件/伏笔，自动创建对应节点。
- 关系变化时，不删除旧边，而是设置 `until` 字段，添加新边。
- 图谱数据持久化在本地，跨会话可用。

### 定期检查
- 每完成一个章节后，检查图谱完整性：
  - [ ] 本章新出场的角色是否已创建节点？
  - [ ] 本章新发生的事件是否已记录？
  - [ ] 本章新增的伏笔是否已同步到 PlotThread？
  - [ ] 本章回收的伏笔是否已更新状态？
  - [ ] 角色关系变化是否已添加新边？

## 核心原则
- 图谱服务于一致性——矛盾是小说仓库的"谎言"。
- 图谱是活的数据——随写作进度持续更新。
- 查图谱优于读全文——大幅降低上下文窗口消耗。
