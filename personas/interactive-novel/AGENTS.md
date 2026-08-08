> 本文件是规则唯一源头。其他工具配置文件（CLAUDE.md、GEMINI.md 等）由 `python scripts/sync_rules.py` 从本文件同步生成，请勿直接编辑它们。

# Interactive Novel Protocol & Safety (互动小说游戏场景协议)

## 1. Workflow & Communication (工作流)
- 先确认游戏设计定位：类型（AVG/RPG/文字冒险）、题材、玩家目标、结局数量，再进入构建。
- 流程：世界观模拟 → 分支叙事架构 → 状态机设计 → 章节节点编写 → 对白/NPC → 测试与难度校准。
- 每次任务先读取本文件及 @personas/interactive-novel/prompts/system-prompt.md。

## 2. 玩家自主性 (Player Agency) — 核心原则
- 玩家选择必须真实影响后续状态与结局，禁止假选择（见 @personas/interactive-novel/skills/player-agency.md。
- 分支叙事保证可达性与回溯可理解性（见 @personas/interactive-novel/skills/branching-narrative.md。

## 3. 状态机与存档
- 所有游戏状态由状态机统一管理（见 @personas/interactive-novel/skills/game-state-machine.md。
- 会话/存档必须可恢复：中断后能按上次状态继续（见 @personas/interactive-novel/skills/session-management.md 与 `state-management.md`，按需 Read）。
- 状态变更写入存档前必须序列化校验，避免脏状态。

## 4. 世界模拟与叙事一致性
- 世界模型遵循 @personas/interactive-novel/skills/world-simulation.md：场景、NPC、物品、时令互相自洽。
- 叙事连贯性检查见 @personas/interactive-novel/skills/narrative-coherence.md；与前文冲突必须显式处理。

## 5. NPC 与对白
- NPC 行为遵循 @personas/interactive-novel/skills/npc-ai.md：性格、记忆、关系网可感知。
- 对白系统遵循 @personas/interactive-novel/skills/dialogue-system.md：选项、好感度、分支触发。

## 6. 系统机制（战斗/难度/物品/结局）
- 战斗与数值遵循 @personas/interactive-novel/skills/combat-system.md。
- 难度引擎遵循 @personas/interactive-novel/skills/difficulty-engine.md：自适应但不欺骗玩家。
- 物品/背包遵循 @personas/interactive-novel/skills/inventory-system.md。
- 结局系统遵循 @personas/interactive-novel/skills/ending-system.md：达成条件可查、奖励可感。

## 7. 质量与防 AI 味
- 游戏文本同样受 Anti-AI-Flavor 约束（见 @personas/interactive-novel/skills/anti-dumb-ai.md。
- 每轮交付用 @personas/interactive-novel/skills/game-evaluation.md量化自评：代入感、选择质量、状态一致性。

## 8. 边界与安全
- 游戏内虚构不受真实性限制，但须内部自洽；现实世界断言仍受 governance P0 约束。
- 安全清单见 @personas/interactive-novel/skills/security-checklist.md；MCP 配置权在用户手里（P0 红线）。

## References
- 系统提示词: @personas/interactive-novel/prompts/system-prompt.md
- 游戏主持人: @personas/interactive-novel/prompts/game-master.md
- 叙事引擎: @personas/interactive-novel/prompts/narrator-engine.md
- NPC 引擎: @personas/interactive-novel/prompts/npc-engine.md
- 新手指引: @personas/interactive-novel/skills/onboarding-system.md
- 重玩系统: @personas/interactive-novel/skills/replay-system.md
- 记忆系统: @personas/interactive-novel/skills/memory-system.md
- 能力演进策略: @personas/interactive-novel/skills/evolution-policy.md
