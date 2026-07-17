# 状态管理原则 (State Management Principles)

> 本文档定义互动小说中游戏状态的管理原则——标志 vs 变量的选型、单一写入权威、合并函数。
> 与 `branching-narrative.md` 互补——后者定义分支结构，本文档定义支撑分支的状态数据如何管理。

## §1 核心原则：数据与逻辑分离

对话和状态属于数据文件（JSON/YAML），绝不硬编码在代码中。

```
对话逻辑 → docs/skills/dialogue-system.md（叙事脚本）
状态数据 → .game-state/state.json（游戏运行时状态）
规则引擎 → 引用状态数据做门控判断
```

**反模式**：在 C#/Python/GDScript 里用嵌套 if-else 管理对话分支——"Big O If/Else"是头号杀手，3选项×5对话=243条路径，10层深=1024端点。

## §2 标志 vs 变量：选型原则

| 维度 | 标志（Flags） | 变量（Variables） |
|------|---------------|-------------------|
| 数据类型 | 布尔（true/false） | 数值（整数/浮点） |
| 适用场景 | 二元门控：门开没开、任务完没完 | 渐变情感：声望、好感度、信任度 |
| 优势 | 简单、易理解、易调试 | 可扩展、可分级、支持阈值触发 |
| 劣势 | proliferation 难审计、二选一无灰度 | 阈值调参易产生跳变 |
| 使用原则 | 用于"是否发生过" | 用于"程度有多深" |

### 混合使用模式

```json
{
  "flags": {
    "met_npc_merchant": true,
    "completed_quest_rats": true,
    "spared_bandit_leader": false
  },
  "variables": {
    "trust_npc_merchant": 45,
    "reputation_town": 30,
    "fear_player": 15
  }
}
```

**设计规则**：
- 标志用于门控：`if (flags.met_npc_merchant) → 显示对话选项`
- 变量用于渐变：`if (variables.trust_npc_merchant >= 50) → NPC 提供折扣`
- 同一关系不要同时用标志和变量——选择一种，避免双真值源

## §3 单一写入权威（Single Source of Truth）

每个状态字段只有一个系统有权修改。

| 状态领域 | 写入权威 | 读取者 |
|----------|----------|--------|
| 任务状态 | 任务系统 | 对话系统、UI、结局计算 |
| 关系值 | 对话系统 | 任务系统、结局计算、NPC AI |
| 物品库存 | 物品系统 | 对话系统、任务系统、UI |
| 世界标志 | 事件系统 | 所有系统 |
| 玩家属性 | 角色系统 | 战斗系统、技能检查、UI |

**反模式**：对话系统直接修改任务状态 → 任务系统和对话系统都认为自己是权威 → 冲突。

**修复**：对话系统通过事件通知任务系统，任务系统决定是否接受修改。

## §4 汇合点合并函数

当多条分支在瓶颈点汇合时，需要合并函数将冗余标志整合为规范记录。

```python
def merge_branch_states(branch_a_state, branch_b_state, merge_rules):
    """
    汇合点状态合并函数
    
    branch_a_state: 分支A结束时状态
    branch_b_state: 分支B结束时状态
    merge_rules: 合并规则（每个字段的合并策略）
    """
    merged = {}
    for field, rule in merge_rules.items():
        if rule == "max":
            merged[field] = max(branch_a_state.get(field, 0), branch_b_state.get(field, 0))
        elif rule == "min":
            merged[field] = min(branch_a_state.get(field, 0), branch_b_state.get(field, 0))
        elif rule == "sum":
            merged[field] = branch_a_state.get(field, 0) + branch_b_state.get(field, 0)
        elif rule == "or":
            merged[field] = branch_a_state.get(field, False) or branch_b_state.get(field, False)
        elif rule == "and":
            merged[field] = branch_a_state.get(field, False) and branch_b_state.get(field, False)
        elif rule == "last_write":
            # 最后写入的分支胜出（需指定优先级）
            merged[field] = branch_b_state.get(field, branch_a_state.get(field))
    return merged
```

**合并规则示例**：
```json
{
  "merge_rules": {
    "trust_npc_merchant": "max",
    "reputation_town": "sum",
    "spared_bandit_leader": "or",
    "met_secret_npc": "or",
    "current_weapon": "last_write"
  }
}
```

## §5 状态设计检查清单

- [ ] 每个状态字段是否有明确的写入权威？
- [ ] 标志和变量是否正确选型（二元用标志，渐变用变量）？
- [ ] 是否有双真值源冲突（两个字段表达同一信息）？
- [ ] 汇合点是否有合并函数？
- [ ] 状态变更是否在2场内有显化反应？（见 `narrative-coherence.md`）
- [ ] 是否有状态爆炸风险？（标志数 > 50 时考虑合并为变量）

## §6 与其他文档的关系

- **`branching-narrative.md`**: 分支结构需要状态管理支撑——深分支预算依赖状态分类。
- **`narrative-coherence.md`**: 后果显化规则检查状态变更是否在2场内被引用。
- **`dialogue-system.md`**: 对话系统是关系变量的写入权威。
- **`difficulty-engine.md`**: 难度调整依赖玩家属性和世界状态。
- **`context-management.md`**: 状态数据是上下文注入的重要组成部分。
