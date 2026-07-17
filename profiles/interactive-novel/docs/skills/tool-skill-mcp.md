# 工具与 MCP（Tool & Skill & MCP）

> 本文档定义互动小说游戏引擎中工具和库的授权白名单、工具描述格式规范、MCP 安全红线，以及创意工具的优先级配置，确保工具使用安全可控且服务于游戏体验。

## 1. 设计目标

工具与 MCP 管理的核心目标：

1. **安全可控**：只使用经授权的工具和库，杜绝未授权代码执行。
2. **描述规范**：工具描述精炼且信息完整，便于引擎正确调用。
3. **MCP 隔离**：MCP 配置权限严格隔离，AI 不可自行安装或配置。
4. **创意优先**：游戏需要的创意工具（随机数、名称生成、地图）优先保障。

## 2. 授权白名单

### 2.1 允许的基础工具

基础功能必须优先使用标准库，以下为允许的工具和库：

| 类别 | 允许的工具/库 | 用途 | 备注 |
|------|--------------|------|------|
| Python 标准库 | json, os, sys, random, math, datetime, pathlib, re, csv | 状态文件读写、随机数、数据处理 | 无需安装 |
| 文件操作 | Read, Write, Edit, Glob, Grep | 文件读取/写入/搜索 | 使用专用工具 |
| Shell | bash（Linux/macOS）、PowerShell（Windows） | 脚本执行、Git 操作 | 需 OS 检测 |
| 版本控制 | git | 代码版本管理 | 遵循 git-sop.md |

### 2.2 允许的第三方库（需审核）

| 库名 | 用途 | 许可证 | 安装前检查 |
|------|------|--------|------------|
| pip | 包管理 | MIT | 内置 |
| pip-audit | 漏洞扫描 | Apache-2.0 | 安装后必须运行 |
| numpy | 数值计算 | BSD | 可选 |
| faker | 名称/数据生成 | MIT | 名称生成工具可用 |

### 2.3 禁止的依赖

```text
禁止引入的依赖类型：

[ ] GPL/AGPL 许可证依赖（传染性开源协议）
[ ] 无明确许可证的依赖
[ ] 已知有未修复高危漏洞的依赖（pip-audit 报警后）
[ ] 来源不明的 GitHub 脚本（未经用户确认）
[ ] 需要 root/管理员权限安装的依赖
[ ] MCP 服务端程序（见 §4 红线）
```

### 2.4 依赖安装流程

```text
第三方依赖安装流程：

1. 确认必要性：是否真的需要这个库？标准库能否替代？
2. 查阅白名单：库是否在授权白名单中？
3. 检查许可证：禁止 GPL/AGPL，禁止无许可证。
4. 安装：pip install <package>
5. 漏洞扫描：pip-audit 扫描已知漏洞。
6. 记录：将依赖记入 requirements.txt 并注释用途。
7. 若从 GitHub 下载脚本：
   ├─ 展示 URL 和 Star 数
   ├─ 经用户同意
   └─ 下载至临时目录（/data/user/work/）
```

## 3. 工具描述格式规范

### 3.1 格式要求

工具描述必须精炼且信息完整，包含以下要素：

| 要素 | 说明 | 必需 |
|------|------|------|
| 工具名称 | 简洁明了的标识符 | 是 |
| 用途说明 | 一句话说明工具做什么 | 是 |
| 参数列表 | 参数名 + 类型标注 + 说明 | 是 |
| 返回值 | 返回值类型 + 说明 | 是 |
| 使用示例 | 至少一个调用示例 | 推荐 |
| 错误处理 | 可能的错误及处理方式 | 推荐 |

### 3.2 参数类型标注规范

```text
参数类型标注格式：

参数名: 类型  — 参数说明

类型对照表：
  str    → 字符串
  int    → 整数
  float  → 浮点数
  bool   → 布尔值
  list   → 列表
  dict   → 字典
  optional → 可选参数（用括号标注默认值）

示例：
  name: str — NPC 名称
  count: int — 数量
  rare_chance: float — 稀有掉落概率（0.0-1.0）
  stackable: bool — 是否可堆叠
  effects: list — 效果列表
  metadata: dict — 元数据
  (optional) note: str — 备注（默认空字符串）
```

### 3.3 工具描述模板

```text
=== 工具描述模板 ===

工具名称：generate_npc_name
用途说明：根据游戏世界观生成 NPC 名称。
参数：
  - genre: str — 游戏类型（fantasy/scifi/wuxia/...）
  - gender: str — 性别（male/female/neutral）
  - (optional) count: int — 生成数量（默认 1）
返回值：
  - str（count=1 时）或 list[str]（count>1 时）— 生成的名称
示例：
  generate_npc_name(genre="fantasy", gender="female")
  → "Elindra Moonwhisper"
错误处理：
  - 未知 genre：返回错误提示并使用默认 fantasy 类型。
```

### 3.4 返回值说明规范

```text
返回值说明要求：

1. 明确类型：str / int / list / dict / bool
2. 复杂返回值需说明结构：
   示例：
   返回值：dict — 物品信息
   结构：{
     "id": str,        — 物品ID
     "name": str,      — 物品名称
     "rarity": str,    — 稀有度
     "value": int      — 基础价值
   }
3. 错误返回：说明错误时的返回值（None / 错误对象 / 异常）
```

### 3.5 描述质量检查清单

- [ ] 工具名称是否简洁且无歧义？
- [ ] 用途说明是否一句话讲清楚？
- [ ] 每个参数是否有类型标注和说明？
- [ ] 返回值类型和结构是否说明？
- [ ] 是否有至少一个使用示例？
- [ ] 边界情况和错误处理是否覆盖？

## 4. MCP 安全红线

### 4.1 绝对红线（P0）

MCP（Model Context Protocol）相关操作是最高安全等级，以下行为绝对禁止：

```text
MCP 安全红线（绝对禁止）：

[禁止] AI 自行下载 MCP 服务端程序
[禁止] AI 自行安装 MCP 依赖
[禁止] AI 自行启动 MCP 服务
[禁止] AI 自行修改 MCP 配置文件
[禁止] AI 自行注册新的 MCP 工具
[禁止] AI 绕过用户确认使用 MCP 功能
[禁止] AI 将 MCP 配置写入游戏状态文件
```

### 4.2 AI 在 MCP 场景中的允许行为

AI 在 MCP 相关事务中**只可**做以下事情：

| 允许行为 | 说明 |
|----------|------|
| 输出配置 JSON | 生成 MCP 配置 JSON 供用户审阅（不自动应用） |
| 解释配置含义 | 向用户说明某项 MCP 配置的作用 |
| 建议配置方案 | 提出建议但必须由用户执行 |
| 报告当前状态 | 读取并报告当前 MCP 配置状态（只读） |

### 4.3 MCP 配置流程

```text
MCP 配置的正确流程（用户主导）：

1. 用户提出 MCP 需求
2. AI 输出建议的配置 JSON（仅文本，不执行）
3. 用户审阅配置 JSON
4. 用户自行决定是否应用
5. 用户自行安装/启动/配置 MCP
6. AI 仅在用户确认后使用已配置的 MCP 工具

关键原则：
  - AI 的角色是"顾问"，不是"执行者"
  - 所有 MCP 变更必须由用户手动完成
  - AI 不得以任何理由绕过此流程
```

### 4.4 MCP 工具使用约束

即使 MCP 已由用户正确配置，使用时仍遵循：

- 每次调用 MCP 工具前，确认该工具在授权白名单中。
- MCP 工具的返回结果不直接回灌到游戏决策链（动作隔离原则）。
- MCP 工具执行的外部操作结果，需经引擎校验后才影响游戏状态。
- MCP 工具调用记录写入审计日志。

## 5. 创意工具优先级

### 5.1 创意工具清单

游戏引擎需要的创意工具按优先级排列：

| 优先级 | 工具 | 用途 | 实现方式 |
|--------|------|------|----------|
| P1 | 随机数生成 | 判定掷骰、掉落概率、NPC 反应 | Python random |
| P1 | 名称生成 | NPC 名称、地名、物品名 | 基于词库的组合生成 |
| P2 | 地图工具 | 区域连接、距离计算、路径生成 | 图结构 + 邻接矩阵 |
| P2 | 属性计算 | 伤害公式、社交判定、经验计算 | 标准数学运算 |
| P3 | 时间工具 | 时间推进、日程管理、事件调度 | datetime |
| P3 | 文本工具 | 摘要压缩、关键词提取 | 正则 + 规则 |

### 5.2 随机数生成工具

```text
工具名称：roll_dice
用途说明：生成游戏判定用的随机数，支持多面骰和修正值。
参数：
  - sides: int — 骰子面数（如 20 表示 d20）
  - count: int — 骰子数量（默认 1）
  - (optional) modifier: int — 修正值（默认 0）
  - (optional) advantage: bool — 是否优势骰（取较高，默认 false）
返回值：dict — {"rolls": list[int], "modifier": int, "total": int}
示例：
  roll_dice(sides=20, modifier=5, advantage=true)
  → {"rolls": [14, 8], "modifier": 5, "total": 19}
说明：游戏判定必须使用此工具，不可由 AI 心算决定结果，
      确保随机性的可信度和可审计性。
```

### 5.3 名称生成工具

```text
工具名称：generate_name
用途说明：根据游戏世界观生成符合风格的名称。
参数：
  - genre: str — 游戏类型（fantasy/scifi/wuxia/cyberpunk/steampunk）
  - type: str — 名称类型（person/place/item/faction）
  - (optional) gender: str — 性别（仅 person 类型，male/female/neutral）
  - (optional) count: int — 生成数量（默认 1）
返回值：str 或 list[str] — 生成的名称
示例：
  generate_name(genre="wuxia", type="person", gender="male")
  → "陆寒霜"
  generate_name(genre="fantasy", type="place", count=3)
  → ["暗影谷", "银月城", "龙骨荒原"]
说明：名称生成基于各类型的词库组合，确保名称风格统一且
      不与已有名称重复（需检查 world-map.json 和 npcs/）。
```

### 5.4 地图工具

```text
工具名称：map_navigate
用途说明：在游戏世界地图中计算路径和距离。
参数：
  - from_location: str — 起始地点ID
  - to_location: str — 目标地点ID
  - (optional) mode: str — 移动方式（walk/ride/fly，默认 walk）
返回值：dict — {
    "path": list[str],     — 经过的地点ID序列
    "distance": float,     — 总距离
    "estimated_time": str, — 预计耗时
    "passable": bool       — 路径是否可通行
  }
示例：
  map_navigate(from_location="riverwood", to_location="capital", mode="ride")
  → {"path": ["riverwood", "crossroads", "capital"], "distance": 45.2,
     "estimated_time": "6小时", "passable": true}
说明：路径计算基于 world-map.json 的区域连接图，若路径中有
      被封锁/摧毁的区域，passable 返回 false 并提示障碍。
```

### 5.5 创意工具使用原则

| 原则 | 说明 |
|------|------|
| 工具优先 | 有工具可用时必须使用，禁止手工模拟 |
| 结果可信 | 工具结果是不可篡改的真实之源，叙事必须遵循 |
| 可审计 | 工具调用记录写入审计日志，可回溯 |
| 不越权 | 创意工具不涉及文件系统或外部操作 |
| 降级方案 | 工具不可用时，记录降级并使用简化逻辑 |

## 6. 工具调用审计

### 6.1 审计记录格式

```text
工具调用审计记录：

[时间戳] [工具名称] [参数摘要] [返回值摘要] [调用结果]

示例：
[Round 15] [roll_dice] [sides=20, modifier=5, advantage=true]
  → [total=19] [成功]
[Round 16] [generate_name] [genre=fantasy, type=person, gender=female]
  → ["Elindra Moonwhisper"] [成功]
[Round 17] [map_navigate] [from=riverwood, to=ruined_tower]
  → [passable=false] [路径被封锁]
```

### 6.2 审计目的

- 确保随机判定可回溯（玩家质疑结果时可查证）。
- 监控工具使用频率（评估工具必要性）。
- 检测异常调用模式（如频繁重试随机数）。
- 为技能策展器提供数据支撑。

## 7. 检查清单

- [ ] 使用的工具/库是否在授权白名单中？
- [ ] 第三方依赖是否通过了 pip-audit 扫描？
- [ ] 工具描述是否符合格式规范（参数标注/返回值说明）？
- [ ] MCP 相关操作是否严格遵循"只建议不执行"原则？
- [ ] 创意工具是否有可用时优先使用？
- [ ] 随机判定是否使用工具而非 AI 心算？
- [ ] 工具调用是否记录到审计日志？
- [ ] 从 GitHub 下载脚本是否经过用户确认？
