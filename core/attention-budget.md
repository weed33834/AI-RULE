# Attention Budget Allocation (ABA)

基于 Microsoft Research "Attention Budget Allocation (2025)" 与
Tsinghua "Instruction Priority Decay Model" 方案，对规则集按注意力需求分级。

## 三级标记体系

| 级别 | 标记 | 含义 | 行为 |
|------|------|------|------|
| **Full Attention (FA)** | `<!-- ABA:FA -->` | 不可压缩的安全核心 | 永不压缩、永不丢弃，置于 cache_control breakpoint 前 |
| **High Priority (HP)** | `<!-- ABA:HP -->` | Profile 核心约束 | 可摘要不可丢弃，长对话中由 LLMLingua 保留关键句 |
| **Compressible (CP)** | `<!-- ABA:CP -->` | 示例/详细说明/工具列表 | 超长上下文时可压缩为要点 |

## 分级原则

1. P0 安全规则 → FA
2. P1 确认规则 → FA 或 HP（视严重性）
3. P2 Profile 特定约束 → HP
4. P3 能力包说明 → HP 或 CP（视是否关键）
5. P4 skills 详细示例 → CP
6. 模板层（templates）→ CP

## 与 I-Hierarchy 锚定的关系

FA 标记的段必须在 ANCHOR REPRISE 中也出现（首尾锚定效应），
确保 Attention Budget 分配时不会因位置而遗漏。

## RT 推理深度标记（Reasoning Tier）

与 ABA 的注意力预算正交，RT 标记用于控制智能体推理深度（thinking budget），不参与压缩优先级的判断。

| 标记 | 含义 | 典型场景 | 上下文占用 |
|------|------|----------|-----------|
| `RT:QUICK` | 轻量推理 | 格式转换、数据提取、FAQ 问答 | 最小，不触发 thinking 模式 |
| `RT:STANDARD` | 标准推理 | 常规编码、方案对比、文档编写 | 中等，常规 thinking |
| `RT:DEEP` | 深度推理 | 架构重构、多步规划、自主纠偏 | 最大，扩展 thinking + CoT |

### RT 与 ABA 的关系

- ABA 控制"注意力分配"（哪些规则该看、该记住），RT 控制"推理投入"（一个问题该想多深）。
- 两者独立计算，互不占用对方预算。
- 示例：一个 CP（可压缩）级规则在 DEEP 模式下仍可被深度思靠；一个 FA（全注意力）级规则在 QUICK 模式下只做快速对照。

### RT 与 Agent 模式映射

| Agent 模式 | 默认 RT | 升级路径 |
|-----------|---------|---------|
| `task` | QUICK 或 STANDARD | 用户可强制 DEEP |
| `project` | STANDARD 或 DEEP | 计划阶段 DEEP，执行阶段 STANDARD |
| `autonomous` | DEEP | 不可降级 |

### sync 参数

`sync_rules.py` 新增 `--rt` 参数：
- `--rt QUICK`：仅注入 RT:QUICK 段
- `--rt STANDARD`：注入 RT:QUICK + STANDARD 段（默认）
- `--rt DEEP`：注入全部 RT 段

## 与 Prompt Caching 的关系

FA 段天然适合放在 Anthropic cache_control breakpoint 之后的前 4 个 breakpoint 中。
sync_rules.py 的 `--cache` 模式自动处理此映射。


## Agent 可执行指令

以下指令供 Agent 在运行时解析和执行，非文档性描述。

### ABA 压缩指令

当上下文窗口用量超过 70% 时：
1. 扫描所有 `ABA:CP` 标记的段，压缩为要点列表（每段 1-2 句）
2. `ABA:HP` 段保留关键句，删除示例和详细说明
3. `ABA:FA` 段完整保留，不得压缩
4. 压缩后重新计算窗口用量，若仍超 85%，请求用户清理对话

### RT 推理控制指令

读取 `<!-- RT:QUICK/STANDARD/DEEP MODE:xxx -->` 标记后：
- RT:QUICK → thinking/reasoning_content 不超过 20 tokens，禁止展开分析
- RT:STANDARD → thinking 正常使用，每步 1-2 句
- RT:DEEP → thinking 充分展开，允许 CoT、多方案对比、自我质疑

### 模式切换指令

读取 MODE 标记后：
- task → 只输出用户要求的单一产出，拒绝功能蔓延
- project → 先输出计划概览再执行，每阶段确认后继续
- autonomous → 主动检查关联文件、发现隐藏问题、在回复末尾列出"⚠️ 待办建议"
