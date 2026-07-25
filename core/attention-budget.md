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

## 与 Prompt Caching 的关系

FA 段天然适合放在 Anthropic cache_control breakpoint 之后的前 4 个 breakpoint 中。
sync_rules.py 的 `--cache` 模式自动处理此映射。
