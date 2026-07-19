# Capabilities（能力包索引）

> 能力包是按需加载的可组合工作方法，不定义智能体身份。每个能力包有明确的输入、输出契约和适用条件。
> 主 Profile 决定身份，能力包只提供方法。一次可叠加多个能力包，但必须在主 Profile 的白名单内（见 `core/profile-router.md`）。

## 能力包清单

| ID | 适用场景 | 输入 | 输出 |
|---|---|---|---|
| `research` | 需要事实支撑、数据验证、最新信息 | 问题、搜索深度 | 带来源标注的结论、置信度 |
| `testing` | 需要编写或验证测试 | 代码、接口、验收标准 | 测试用例、覆盖率、通过报告 |
| `review` | 代码或内容审查 | 待审文件、审查维度 | 问题清单、严重度、修复建议 |
| `engineering` | 工程实现、架构落地 | 需求、技术栈 | 代码、配置、部署方案 |
| `creative` | 创意生成、文风、修订 | 主题、约束、样本 | 创意文本、修订稿 |
| `worldbuilding` | 世界观、角色、时间线维护 | 设定素材、历史节点 | 一致性校验后的设定集 |
| `state-machine` | 状态机治理、分支可达性 | 状态迁移表、不变量 | 合法迁移序列、冲突报告 |
| `npc-simulation` | NPC 自主性、记忆、关系 | NPC 设定、玩家行为 | NPC 状态更新、反应 |
| `adaptive-difficulty` | 难度自适应 | 玩家表现、难度曲线 | 难度参数调整 |
| `game-engine` | 游戏回合、存档、命令 | 玩家输入、当前状态 | 下一状态、可选分支 |
| `agent-governance` | 智能体评估、观测、安全对齐 | Agent 配置、日志 | 评估报告、风险项 |
| `orchestration` | 多智能体编排、委派 | 子任务、委派条件 | 编排图、上下文边界 |
| `novel-chapter-deliverable-mode` | 小说章节交付模式 | 大纲、人物设定 | 章节稿件、修订记录 |
| `dar` | 域权威注册表——权威源名录、打分公式、检索路由 | 问题、领域 | 排序后的权威源、打分结果 |

## 加载规则

1. 能力包由用户显式请求或任务匹配触发，不默认加载。
2. 加载前必须检查主 Profile 的白名单；禁止的不得加载。
3. 能力包之间无互斥；但不得与主 Profile 冲突。
4. 冲突时优先级：P0 core > P1 用户确认 > P2 主 Profile > P3 能力包 > P4 默认。

## 详细定义

- [research](research.md)
- [testing](testing.md)
- [review](review.md)
- [engineering](engineering.md)
- [creative](creative.md)
- [worldbuilding](worldbuilding.md)
- [state-machine](state-machine.md)
- [npc-simulation](npc-simulation.md)
- [adaptive-difficulty](adaptive-difficulty.md)
- [game-engine](game-engine.md)
- [agent-governance](agent-governance.md)
- [orchestration](orchestration.md)
- [novel-chapter-deliverable-mode](novel-chapter-deliverable-mode.md)
- [dar (Domain Authority Registry)](dar/README.md) — 6 个领域配置（paper/coding/conversation/novel/interactive-novel/agent-builder）
