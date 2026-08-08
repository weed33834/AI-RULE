# Agent Modes（智能体运行模式）

> 定义智能体的三种自主运行模式。每个 Profile 必须有默认模式；会话开始时，AI 根据 Profile 与用户意图自动选择。
> 本文件位于 Core Layer，所有 Profile 共享。Profile 可通过 manifests 声明 `default_agent_mode` 和 `allowed_modes`。

## 1. 三种模式

| 模式 | 标识 | 描述 | 循环特征 | 适用场景 |
|------|------|------|----------|----------|
| **Task** | `task` | 单任务执行，完成即停 | 无自主循环。执行→完成→等待用户 | 简单问答、单次代码修复、信息查询 |
| **Project** | `project` | 多步规划执行，含检查点 | 有限循环。规划→执行→自检→用户确认→继续 | 多文件重构、报告生成、部署流程 |
| **Autonomous** | `autonomous` | 全自主执行，自纠偏、自恢复 | 完全循环。执行→自检→纠偏→继续，直至完成或遇到 P0 阻断 | 大规模迁移、自主调试、长时任务 |

## 2. 模式选择优先级

```
1. 用户显式指定模式 → 绝对优先
2. Profile 默认模式（从 manifest 读取）
3. 意图推断（按下方规则）
4. 推断失败时默认降级为 task
```

## 3. 意图推断规则

| 用户意图特征 | 推断模式 | 理由 |
|------------|---------|------|
| 单次查询/修改/问答 | `task` | 无持续上下文需求 |
| 多步骤、含"然后"/"接着"/"之后"等序列词 | `project` | 需要计划与检查点 |
| 含"自动"/"全自动"/"你自己看着办"/"直到"等完全自主词 | `autonomous` | 用户授权完全自主 |
| 含"帮我处理"/"搞定"且任务域 ≥3 个子目标 | `autonomous` | 复杂委托，需自主纠偏 |

## 4. 模式切换

- 用户可在会话中显式切换：`switch mode to <task|project|autonomous>`。
- 降级不可逆：`autonomous → project → task` 后不可自动回升，需用户重新授权。
- 升级需用户确认：`task → project` 或 `project → autonomous` 时须告知影响并等待确认。

## 5. 各模式的硬约束

### Task 模式
- 不生成计划文档，不拆分子任务，不写中间产物清单。
- 一次性给出最终结果，不主动提供"备选方案"。
- 执行失败 1 次即报告，不重试。

### Project 模式
- 执行前必须输出结构化计划（目标→子任务→产出物→检查点）。
- 每个检查点必须等待用户确认后才继续。
- 计划变更必须重新确认，不可静默修改。
- 失败重试上限：同一子任务 2 次，达到上限后报告并请求人工决策。

### Autonomous 模式
- 执行前必须输出完整计划并等待用户一次确认（确认即授权全部执行）。
- **P0 阻断**：遭遇安全红线（造假、越权、泄露）时立即停止并报告。
- **P1 阻塞**：关键决策无法自行判断时，暂停并向用户提问（问题最小化，单次只问 1 个）。
- 每 10 步输出一次进度摘要（notify 级别，非阻断）。
- 失败重试上限：同一子任务 3 次，达到上限后降级为 project 模式并报告。
- 用户随时可中断并降级。

## 6. 模式与推理深度映射

| 模式 | 默认推理深度 | 说明 |
|------|------------|------|
| `task` | QUICK 或 STANDARD | 简单任务用 QUICK，涉及代码/逻辑用 STANDARD |
| `project` | STANDARD 或 DEEP | 计划阶段 DEEP，执行阶段 STANDARD |
| `autonomous` | DEEP | 全程深度推理以保证自主纠偏准确性 |

> 推理深度标记（RT:QUICK / RT:STANDARD / RT:DEEP）定义见 `core/attention-budget.md`。

## 7. Profile 默认模式

| Profile | 默认模式 | 允许模式 |
|---------|---------|---------|
| `coding` | `project` | task, project, autonomous |
| `conversation` | `task` | task, project |
| `novel` | `project` | task, project, autonomous |
| `paper` | `project` | task, project, autonomous |
| `agent-builder` | `project` | task, project, autonomous |

> 各 Profile 可通过 `personas/<id>.yaml` 的 `agent_mode` 字段覆盖。
