# Profile Router（Profile 选择器）

> 本文件定义如何从用户意图或项目锚点确定唯一主 Profile，以及可叠加的能力包白名单。
> 每次会话只能有一个主 Profile；`novel` 与 `interactive-novel` 互斥；`agent-builder` 仅用于构建/评估/部署智能体。

## 1. 主 Profile 一览

| Profile ID | 来源仓库 | 适用场景 | 互斥 |
|---|---|---|---|
| `coding` | AI | 软件开发、Bug 修复、重构、测试、代码审查 | novel、interactive-novel |
| `conversation` | universal | 通用问答、调研、方案对比、信息检索 | novel、interactive-novel、agent-builder |
| `novel` | novel | 小说写作、章节创作、角色/世界观维护 | interactive-novel、coding、agent-builder |
| `interactive-novel` | interactive-novel | 互动小说游戏、分支叙事、状态机驱动 | novel、coding、agent-builder |
| `agent-builder` | AgentCreater | 设计/评估/部署智能体，产出 config、工具、测试 | novel、interactive-novel |

## 2. 选择优先级

```text
1. 用户或项目配置显式指定 active_profile → 绝对优先
2. 目录锚点自动识别（仅在未指定时）
3. 用户当前意图关键词匹配
4. 识别不唯一时必须澄清，只问一个最小问题，不重复已确认项。
```

## 3. 目录锚点自动识别

| 锚点信号 | 推断 Profile |
|---|---|
| `pyproject.toml`、`package.json`、`requirements.txt` + 源码/测试目录 | `coding` |
| `.game-state/`、`game-state-machine.md`、`save-slot-*.json` | `interactive-novel` |
| `.ai-memory/creative-blueprint.md`、`chapters/`、`outline.md` | `novel` |
| `config.yaml` + `tools.json` + `test-cases.md` 的智能体资产目录 | `agent-builder` |
| 无上述锚点 | `conversation` |

## 4. 意图关键词匹配

| 关键词 | 推断 Profile |
|---|---|
| 修复/重构/测试/部署/接口/Bug/CI | `coding` |
| 写一章/续写/人物/伏笔/文风/世界观 | `novel` |
| 开始一局/分支/存档/NPC/回合/状态 | `interactive-novel` |
| 设计 Agent/智能体配置/工具权限/评估 | `agent-builder` |
| 查询/对比/分析/调研/总结 | `conversation` |

## 5. 能力包叠加白名单

| 主 Profile | 可叠加能力包 | 禁止默认叠加 |
|---|---|---|
| `coding` | `research`、`testing`、`review`、`agent-governance` | `game-engine`、`worldbuilding`、`npc-simulation` |
| `conversation` | `research` | `engineering`、`creative`、`game-engine` 的强制行为 |
| `novel` | `research`（真实背景时）、`worldbuilding`、`creative` | `game-engine`、`state-machine` |
| `interactive-novel` | `creative`、`research`、`state-machine`、`npc-simulation`、`adaptive-difficulty` | `novel-chapter-deliverable-mode`、`engineering` |
| `agent-builder` | `research`、`agent-governance`、`engineering`、`testing` | `novel-chapter-deliverable-mode`、`game-engine` |

## 6. 冲突解决

```text
P0：core/ 安全与权限
> P1：用户当前明确确认
> P2：主 Profile 规则
> P3：能力包规则
> P4：模型默认行为
```

同一优先级出现相反约束时：
- 若一方是 P0，P0 胜出。
- 若同属 P2 但分属不同 Profile，主 Profile 胜出，能力包让位。
- 若仍无法裁决，停止并向用户说明冲突，请求裁决。

## 7. Profile 切换

- 用户可在会话中显式切换：`switch profile to <id>`。
- 切换时必须清除前一 Profile 的上下文状态标记，避免状态污染。
- `novel` → `interactive-novel` 或反向切换时，必须询问是否保留共享素材（角色、世界观）。
