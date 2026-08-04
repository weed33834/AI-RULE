---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 撰写 Results/Discussion/Conclusion 时需逐条检查声明是否有数据支撑，或投稿前自检过度概括 / Writing Results/Discussion/Conclusion and checking each claim has data backing, or pre-submission overgeneralization check
terminates_when: T    # 每条声明已分类（Fully/Partially/Unsupported）、Unsupported 已改写为推测或删除、Claim_Support_Score 已计算并报告 / All claims classified, Unsupported rewritten or removed, Claim_Support_Score computed and reported
provides: π           # 声明-数据对照表模板、Claim_Support 三级分类、Claim_Support_Score 公式、过度概括检测清单、与 academic-integrity 联动
interface: R          # 输入=论文草稿（含声明）+ 数据/结果；输出=声明分类表 + Claim_Support_Score + 修订建议
---

# Data-Claim Alignment（数据-声明一致性检查）

> AI 写论文时容易"数据说 X，结论说 Y"——Results 给出受限条件下的数据，Discussion/Conclusion 却以全称命题陈述。本文件强制每条声明对照数据，量化支撑度，防止过度概括。
> 本文件是 paper 领域专用；通用对话场景的置信度校准见 `truth-protocol.md` §8 Confidence Calibration Protocol，本文件产出的 Claim_Support_Score 作为其客观证据输入。
> 与 `academic-integrity.md` 联动——无数据支撑却作事实陈述等同于变相编造（P0 红线）。

## §1 核心理念 / Core Principles

三条原则：
- **每条声明可追溯**：任何"事实陈述句"必须能指回具体数据/统计结果（表/图/原始数据），否则不得作事实陈述。
- **推测必标注**：超出数据直接支撑范围的推断必须用"推测："/"基于...推测"前缀，不得伪装为事实。
- **过度概括即修正**：发现声明超出数据范围时立即改写或删除，不留"看起来更有贡献"的措辞。

### 1.1 什么算"声明"

| 句子类型 | 是否计入声明 | 说明 |
|----------|-------------|------|
| 事实陈述句（"X 优于 Y 5.3%"） | 是 | 必须有数据支撑 |
| 推测句（"我们推测..."） | 否 | 已显式标注，不计入 Total_claims |
| 引用他人结论（"Smith et al. 发现..."） | 否 | 由 academic-integrity.md 验证 |
| 方法描述、定义、公理 | 否 | 非结论性陈述 |

## §2 声明分类 / Claim Classification

每条声明按数据支撑程度分三级：

| 分类 | 定义 | 处置 |
|------|------|------|
| Fully Supported | 声明直接由数据/统计结果支撑（同变量、同范围、同条件） | 可作事实陈述 |
| Partially Supported | 部分维度有数据支撑，其他维度为推断 | 必须标注"基于...推测"，列出已支撑与推断部分 |
| Unsupported | 无任何数据支撑，纯由直觉/惯例/希望填充 | 必须删除，或改为明确的推测（加"推测："前缀） |

### 2.1 Partially vs Unsupported 的边界

- Partially：至少有一个维度由本研究数据直接支撑，其余维度推断。
- Unsupported：所有维度均无数据支撑（即便措辞看似有据）。
- 模糊难定时按保守原则归 Unsupported——宁可多改写，不可多放行。

## §3 Claim_Support_Score 公式 / Formula

```
Claim_Support_Score = (Fully×1.0 + Partially×0.5 + Unsupported×0) / Total_claims
```

| Score 区间 | 等级 | 含义 | 处置 |
|------------|------|------|------|
| = 1.0 | 高 | 全部声明有支撑 | 可送审 |
| ≥ 0.85 | 中 | 少量推测，已标注 | 可送审，需在 Limitations 披露 |
| < 0.85 | 低 | 过度概括严重 | 必须修订，重写或删除 Unsupported |

### 3.1 Total_claims 计数规则

- 只计事实陈述句（见 §1.1）；推测句、引用句、方法/定义不计入。
- 复合声明（"X 优于 Y 且泛化到 Z"）拆为两条分别计数。
- 改写后总声明数变化时，Score 必须重算。

## §4 检查流程 / Check Workflow

```
1. 提取所有声明   → 通读 Results/Discussion/Conclusion，列出每个事实陈述句
2. 逐条找数据支撑 → 对每条声明指回具体表/图/统计结果；找不到则标 Unsupported
3. 分类           → 按 §2 分 Fully / Partially / Unsupported
4. 计算 Score     → 套 §3 公式，对照阈值表
5. 改写           → Unsupported 删除或改为"推测："；Partially 补标注
```

### 4.1 步骤说明

- 步骤 1 重点扫描 Discussion/Conclusion——这是过度概括高发区；Results 中的事实陈述通常有数据支撑但需复核范围。
- 步骤 2"指回"必须是可定位的（表号/图号/统计量），模糊指代（"我们的实验"）不算支撑。
- 步骤 5 改写一条后即返回步骤 4 重算 Score，直到 ≥ 0.85 或所有 Unsupported 处置完毕。

## §5 声明-数据对照表模板 / Claim-Data Alignment Table

每条声明填入下表，作为检查的可审计产物：

| 声明 | 位置（章节/段） | 数据/统计支撑 | 分类 | 处置 |
|------|----------------|---------------|------|------|
| 本方法在 X 数据集上 F1 提升 5.3% | §4.2 ¶3 | Table 2, paired t-test, d=0.42 | Fully | 保留 |
| 本方法优于所有 baseline | §5 ¶1 | 仅在 X 数据集，未跨域 | Partially | 改"在 X 上优于 baseline，跨域待验证" |
| 本方法是通用解决方案 | §6 ¶2 | 无跨域/跨任务数据 | Unsupported | 删除或改"推测：可能在相近分布上泛化" |

该表是检查的可审计产物：一行一条声明；处置列记录改写后的措辞或"已删除"；最终附于 Limitations 或内部审查记录。

## §6 过度概括检测清单 / Overgeneralization Checklist

| 模式 | 表现 | 修正 |
|------|------|------|
| 单样本推全体 | "本研究表明..."但只有一个实验/数据集 | 加限定词："在本数据集上..." |
| 相关当因果 | "X 导致 Y"但仅有相关系数 | 改"X 与 Y 相关"；因果需实验设计支撑 |
| 选择性引用 | 只提支持声明，略去反例 | 报告全部条件（含 null 结果） |
| 超范围外推 | 实验室结果推到现实场景 | 加"在实验条件下..."限定，外推标"推测：" |
| 模糊量词 | "显著提升"但无效应量 | 报告 d / η² / r + CI，量化"显著" |

## §7 失败信号 / Failure Signals

| 信号 | 描述 | 修复 |
|------|------|------|
| 跳过对照直接交稿 | 未填 §5 表格就交付草稿 | 强制走 §4 流程，产出对照表 |
| Unsupported 声明保留 | 把无支撑声明当作事实保留 | 删除或改为"推测：" |
| Score 低却送审 | Score < 0.85 仍提交 | 阻断，强制修订后再送审 |
| 部分改写后未重算 | 改写后未更新 Score | 改写一条即重算一次 |

## §8 与其他文档的关系 / Relationship to Other Documents

- **`academic-integrity.md`**：无数据支撑的声明作事实陈述，等同变相编造，触发 P0 红线；Unsupported 处置结果回流到该文档的违规清单。
- **`peer-review-simulation.md`**：Skeptical 评审角色专查本项；本文件产出的对照表与 Score 作为其评审输入。
- **`truth-protocol.md` §8 Confidence Calibration Protocol**：Claim_Support_Score 作为客观证据校准模型自评置信度——Score=高才允许在通用对话中以"高置信"陈述该项发现。
- **`data-presentation.md`**：图表必须能支撑所引声明；图表自身的报告标准（效应量、CI）是本文件判 Fully 的前提。
