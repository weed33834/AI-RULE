# 游戏状态机技能 (Game State Machine)

> 游戏与聊天机器人的根本区别在于状态：状态是游戏世界的"真实之源"，叙事必须与状态一致，不可矛盾。
> NPC 状态结构详见 `npc-ai.md`；世界状态结构详见 `world-simulation.md`；状态持久化与存档详见 `session-management.md`。

## §1 架构总览

本技能参考 AI Dungeon 的 `Story` / `StoryManager` 双层架构，将游戏状态拆分为"数据层"与"管理层"：

- **Story（数据层）**：以 JSON 文件持久化的全部游戏状态，包括玩家、世界、NPC 三大域。
- **StoryManager（管理层）**：负责状态读取、写入、验证、回滚的规则引擎，是叙事与数据之间的唯一桥梁。

```
┌─────────────────────────────────────────────┐
│              StoryManager                   │
│   (读取 → 验证 → 更新 → 写回 → 校验)         │
├──────────┬──────────┬───────────────────────┤
│ 玩家状态  │ 世界状态  │      NPC 状态         │
│ player   │ world    │   npcs/{name}.json   │
│ .json    │ -map.json│                      │
└──────────┴──────────┴───────────────────────┘
       ↑ 叙事引擎只能通过 StoryManager 访问状态
```

**核心原则**：叙事引擎不得直接读写状态文件，一切状态变更必须经由 StoryManager 的更新规则，并在变更后通过验证机制。

## §2 玩家状态数据结构

玩家状态存放于 `.game-state/player.json`，结构如下：

```json
{
  "identity": {
    "name": "Roland",
    "alias": ["退役骑士", "铁壁"],
    "race": "人类",
    "class": "骑士",
    "level": 7,
    "background": "退役皇家卫队成员，因一场冤案流落江湖"
  },
  "vitals": {
    "hp": { "current": 78, "max": 120 },
    "mp": { "current": 15, "max": 40 },
    "stamina": { "current": 60, "max": 100 },
    "hunger": 35,
    "fatigue": 20
  },
  "attributes": {
    "strength": 16,
    "agility": 12,
    "intelligence": 10,
    "charisma": 14,
    "perception": 13,
    "willpower": 11
  },
  "skills": [
    { "id": "sword_mastery", "name": "剑术精通", "level": 4, "exp": 120 },
    { "id": "shield_block", "name": "盾牌格挡", "level": 3, "exp": 45 }
  ],
  "inventory_ref": ".game-state/inventory.json",
  "status_effects": [
    { "id": "bleeding", "name": "流血", "duration": 3, "severity": "minor" }
  ]
}
```

### 物品栏结构（inventory.json）

```json
{
  "slots": {
    "weapon": { "id": "iron_longsword", "name": "铁制长剑", "durability": 85 },
    "armor": { "id": "chainmail", "name": "锁子甲", "durability": 60 },
    "accessory": null
  },
  "backpack": [
    { "id": "health_potion", "name": "治疗药水", "quantity": 3, "stackable": true },
    { "id": "rusty_key", "name": "生锈的钥匙", "quantity": 1, "stackable": false,
      "metadata": { "acquired_from": "地牢守卫", "quest_related": "crypt_of_shadows" } }
  ],
  "capacity": 20,
  "weight": { "current": 45.5, "max": 80.0 }
}
```

## §3 世界状态数据结构

世界状态分散于多个文件，统一由世界状态域管理。

### 世界地图（world-map.json）

```json
{
  "regions": {
    "kingsport": {
      "name": "王港城",
      "type": "city",
      "state": "plague_quarantine",
      "explored": true,
      "connections": ["old_forest", "harbor_district"],
      "current_hazards": ["疫病封锁", "夜间宵禁"],
      "npcs_present": ["guard_captain_marcus", "healer_elena"]
    },
    "old_forest": {
      "name": "古森林",
      "type": "wilderness",
      "state": "bandit_infested",
      "explored": false,
      "connections": ["kingsport", "abandoned_mine"]
    }
  },
  "player_location": "kingsport"
}
```

### 时间线（timeline.json）

```json
{
  "current_time": { "day": 14, "hour": 21, "phase": "night" },
  "total_elapsed_hours": 320,
  "season": "autumn",
  "milestones": [
    { "day": 1, "event": "玩家抵达王港城", "timestamp": "game_start" },
    { "day": 8, "event": "疫病爆发", "timestamp": "plague_outbreak" },
    { "day": 14, "event": "玩家进入封锁区", "timestamp": "quarantine_entry" }
  ]
}
```

### 派系（factions.json）

```json
{
  "factions": {
    "royal_guard": {
      "name": "皇家卫队",
      "power": 75,
      "attitude_to_player": 20,
      "goal": "维持秩序、控制疫病",
      "resources": ["兵力", "武器", "粮草"]
    },
    "thieves_guild": {
      "name": "盗贼公会",
      "power": 40,
      "attitude_to_player": -15,
      "goal": "趁乱掠夺、扩张势力",
      "resources": ["情报", "黑市渠道"]
    }
  },
  "relations": {
    "royal_guard__thieves_guild": "hostile"
  }
}
```

## §4 NPC 状态数据结构

每个 NPC 单独存放于 `.game-state/npcs/{name}.json`：

```json
{
  "identity": {
    "name": "Elena",
    "role": "治愈师",
    "location": "kingsport_chapel"
  },
  "emotion": {
    "trust": 45,
    "fear": 30,
    "affection": 10,
    "hostility": 0
  },
  "knowledge": {
    "knows": ["疫病源头在古森林", "玩家是退役军人"],
    "does_not_know": ["盗贼公会藏身处"],
    "rumors_heard": ["有人在黑市贩卖假药"]
  },
  "memory": [
    { "day": 12, "event": "玩家送来草药", "impact": "trust+10" },
    { "day": 13, "event": "玩家拒绝透露行踪", "impact": "trust-5, suspicion+10" }
  ],
  "schedule": {
    "morning": "chapel_prayer",
    "afternoon": "treat_patients",
    "night": "rest"
  }
}
```

## §5 状态更新规则

所有状态变更必须遵循以下规则，由 StoryManager 强制执行：

| 规则 | 说明 | 示例 |
|------|------|------|
| 原子性 | 一次行动引发的所有状态变更要么全部成功，要么全部回滚 | 攻击造成伤害+消耗体力+装备损耗必须一起写入 |
| 可追溯 | 每次变更记录原因、触发行动、变更前后值 | "好感度 10→25，原因：玩家救助其妹妹" |
| 上下文一致 | 叙事描述必须与状态文件数值吻合，不得叙事说"满血"而状态显示 HP 残缺 | 叙事提及流血时 status_effects 必须有 bleeding |
| 时间推进 | 涉及时间消耗的行动（战斗、旅行、休息）必须更新 timeline | 长途旅行推进 8 小时并切换昼夜阶段 |
| 信息隔离 | NPC 状态的 knowledge 字段只能通过合法传播渠道更新 | 玩家在 A 地的秘密不能凭空出现在 B 地 NPC 的 knows 中 |

### 更新流程示例

```
玩家行动："我用长剑攻击地精，瞄准它的腿部"
  ↓
1. StoryManager 读取 player.json（剑术等级、武器耐久）
2. 读取地精 NPC 状态（HP、敏捷用于闪避）
3. 判定命中与伤害 → 更新地精 HP
4. 扣减玩家体力、武器耐久 -2
5. 若击杀：更新地精状态为 dead，更新区域 npc 清单
6. 推进时间（战斗耗时 ~15 分钟）
7. 写回所有变更文件
8. 运行验证（见 §6）
```

## §6 状态验证机制

每次状态更新后，StoryManager 执行三层验证：

### 第一层：完整性校验
- 所有必填字段存在且类型正确（HP 不为字符串、等级为非负整数）。
- 数值在合法区间内（HP 不超过 max，好感度在 -100~100）。

### 第二层：一致性校验
- 玩家当前位置与 world-map.json 的 `player_location` 一致。
- 在场 NPC 列表与区域 `npcs_present` 一致。
- 叙事文本中提及的数值与状态文件吻合（如叙事说"你只剩半条命"，HP 应在 50% 以下）。

### 第三层：逻辑校验
- 知识边界：NPC 是否知道了无合法传播渠道的信息？
- 时间线：事件顺序是否自洽（不可"先到 B 地再从 A 地出发"）？
- 因果链：状态变更是否有合理的触发行动？

```json
{
  "validation_log": {
    "timestamp": "day14_night",
    "checks_run": 18,
    "violations": [],
    "warnings": ["Elena 的 trust 值单轮变化 30，超出常规阈值，请确认剧情合理性"]
  }
}
```

## §7 状态回滚

- `/rewind` 指令撤销最近一次行动引发的状态变更，依赖变更前的状态快照。
- 快照保留最近 5 步，超过后不再可回滚。
- 回滚后叙事需重新生成，并明确告知玩家"时间倒流至你做出上一个选择之前"。

> 状态机不是叙事的枷锁，而是叙事的地基——只有地基稳固，剧情的大厦才能盖得高而不倒。
