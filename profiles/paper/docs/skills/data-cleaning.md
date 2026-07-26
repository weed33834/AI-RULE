---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # raw data 进入统计分析/论文写作前，需检查完整性/一致性/异常值并决定是否可进入分析 / Before raw data enters analysis or paper writing, check completeness/consistency/outliers and decide whether data is analysis-ready
terminates_when: T    # 三维清洗检查完成、Data_Quality 已计算、清洗记录已存档、不达标项已有处置 / Three-dimension cleaning done, Data_Quality computed, cleaning log archived, sub-threshold items handled
provides: π           # 数据清洗三维框架（完整性/一致性/异常值）、Data_Quality 公式（w1×Completeness+w2×Consistency+w3×Outlier_Clean）、清洗记录模板、与 truth-protocol §8 Calibration 联动
interface: R          # 输入=原始数据集 + 字段说明 + 分析目标；输出=Data_Quality 分数 + 清洗记录 + 可否进入分析的判定
---

# Data Cleaning Quality（数据清洗质量门槛）

> 本文档定义论文撰写场景下"数据清洗"的质量门槛：三维框架（完整性/一致性/异常值）、Data_Quality 公式、清洗记录模板。
> AI 无法直觉判断"数据够不够干净"，必须用公式量化——这是 Garbage In Garbage Out 的前置防线。
> 与通用 `Search_Quality`（`deep-search.md` §6）互补——Search_Quality 评检索质量，本公式评数据质量。
> 与 `truth-protocol.md` §8 Confidence Calibration 联动——Data_Quality 分数作为置信度校准的客观输入之一。

## §1 核心理念

数据清洗三原则：

- **Garbage In Garbage Out**：脏数据进入分析，再严谨的统计方法也只能产出错误结论。清洗是分析的前置条件，不是可选步骤。
- **清洗可追溯**：每一次删除、修正、填充都必须留记录。无记录的清洗等同于篡改数据，违反学术诚信。
- **不达标不进入分析**：Data_Quality 低于阈值时禁止进入下一阶段，必须重清洗或重采集。这是硬门槛，不允许"先分析再说"。

## §2 Data_Quality 公式

```
Data_Quality = w1 × Completeness + w2 × Consistency + w3 × Outlier_Clean
```

| 维度 | 计算方式 | 数据来源 | 默认权重 |
|------|----------|----------|----------|
| **Completeness（完整性）** | `1 - 缺失值数 / 总单元格数`（按字段加权） | 原始数据集缺失值扫描 | w1 = 0.4 |
| **Consistency（一致性）** | `1 - 跨字段/跨表冲突记录数 / 总记录数` | 类型/范围/外键一致性检查 | w2 = 0.3 |
| **Outlier_Clean（异常值清洗度）** | `1 - 未处理异常值数 / 检测到的异常值数` | IQR 或 Z-score 检测结果 | w3 = 0.3 |

权重满足 `w1 + w2 + w3 = 1.0`。论文领域默认权重反映"完整性优先"——缺失值直接影响样本量与统计效力，故权重最高。

## §3 维度详解

### §3.1 Completeness（完整性）

```
Completeness = 1 - (Σ field_i_weight × missing_count_i) / (Σ field_i_weight × total_count_i)
```

- **按字段加权**：关键字段（如主键、因变量、干预变量）权重高，辅助字段（如备注、元数据）权重低。
- **关键字段缺失**：因变量或主键缺失的记录通常应整行剔除，而非填充。
- **辅助字段缺失**：可保留记录，在分析时按需处理。
- **填充需标注**：任何填充（均值/中位数/插值/模型预测）必须在清洗记录中写明方法与依据。

### §3.2 Consistency（一致性）

```
Consistency = 1 - conflict_records / total_records
```

一致性检查覆盖三类冲突：

| 冲突类型 | 示例 | 检测方式 |
|----------|------|----------|
| 类型一致性 | 数值字段出现字符串 | schema 校验 |
| 范围一致性 | 年龄 = -5 或 200 | 字段域约束 |
| 外键一致性 | 引用了不存在的主键 | join 完整性检查 |

跨表数据需额外检查：同一实体在不同表中的属性是否一致（如患者年龄在基线表与随访表不一致）。

### §3.3 Outlier_Clean（异常值清洗度）

```
Outlier_Clean = 1 - unhandled_outliers / detected_outliers
```

- **检测方法**：连续变量用 IQR（`Q1 - 1.5×IQR` 与 `Q3 + 1.5×IQR` 之外）或 Z-score（`|z| > 3`）；小样本优先 IQR。
- **处理方式**：保留并标注 / Winsorize 截断 / 剔除 / 修正（仅当有明确录入错误证据）。每条异常值的处置必须记录。
- **未处理 ≠ 不存在**：检测到但未处置的异常值会拉低分数。选择保留也必须在记录中说明理由（如"经核实为真实极端值，保留"）。

## §4 阈值与处置

| Data_Quality | 等级 | 处置 |
|---|---|---|
| **≥ 0.85** | 高质量 | 直接进入分析 |
| **0.7 – 0.85** | 中质量 | 需补清洗（针对最低分维度）后重算 |
| **< 0.7** | 低质量 | 禁止进入分析，必须重采集或重清洗 |

阈值是硬门槛：低于 0.7 时无论分析目标多紧迫，都不允许进入下一阶段。这是与 governance.md §9 Loop 上限对齐的强制约束。

## §5 强制自评流程

```
原始数据进入分析前，必须执行：

1. 算三维分量 — 分别计算 Completeness / Consistency / Outlier_Clean
2. 加权求和 — 按 §2 默认权重（或领域覆盖权重）计算 Data_Quality
3. 对照阈值 — 按 §4 表判定等级与处置
4. 不达标则清洗后重算 — 最多 3 轮（对齐 governance.md §9 Loop 上限）
   a. 识别最低分维度
   b. 针对该维度执行清洗（如 Completeness 低 → 补采集或剔除关键字段缺失行）
   c. 重算 Data_Quality，仍未达标则进入下一轮
   d. 3 轮后仍 < 0.7 → 禁止进入分析，触发重采集
5. 在论文 Methods 报告 — 报告最终 Data_Quality 分数与清洗措施
```

## §6 清洗记录模板

每次清洗必须产出以下 YAML 记录并归档（与论文 supplementary material 一同提交）：

```yaml
dataset_name: <数据集名称>
cleaning_date: <YYYY-MM-DD>
analyst: <负责人或 AI agent 标识>
analysis_goal: <本次分析目标，决定关键字段权重>

dimensions:
  completeness:
    score: <0.0-1.0>
    missing_total: <总缺失单元格数>
    missing_by_field: { <字段名>: <缺失数>, ... }
    imputation_methods: { <字段名>: <方法或null>, ... }
  consistency:
    score: <0.0-1.0>
    conflicts_total: <冲突记录数>
    conflicts_by_type: { type: <n>, range: <n>, foreign_key: <n> }
  outlier_clean:
    score: <0.0-1.0>
    detected: <检测到的异常值数>
    unhandled: <未处理异常值数>
    method: <IQR | Z-score | both>

final_score: <Data_Quality，0.0-1.0>
threshold_grade: <高 | 中 | 低>
actions_taken:
  - step: <清洗动作描述>
    target: <字段或记录范围>
    rationale: <依据>
    records_affected: <影响记录数>
admitted_to_analysis: <true | false>
```

## §7 失败信号

| 信号 | 描述 | 修复 |
|------|------|------|
| 跳过自评直接分析 | 未算 Data_Quality 就进入统计 | 强制执行 §5 五步，回退到清洗阶段 |
| 异常值未处理就进入分析 | 检测到异常值但 Outlier_Clean = 0 仍继续 | 必须处置或显式标注保留理由后重算 |
| 清洗记录缺失 | 删除/修正/填充未留 YAML 记录 | 补齐 §6 模板，无记录的清洗视为未发生 |
| 分数低却强行进入分析 | Data_Quality < 0.7 仍进入下一阶段 | 阻断流程，回到 §5 第 4 步重清洗或触发重采集 |

## §8 与其他文档的关系

- **`methodology-design.md`**：数据清洗是方法论可复现性的前提——无清洗记录的方法节无法被复现。
- **`data-presentation.md`**：只有通过清洗门槛的数据才可呈现；图表基于清洗后数据集，原始脏数据不进入图表。
- **`truth-protocol.md` §8**：Data_Quality 分数作为 Confidence Calibration 的客观输入——基于低质量数据的结论强制降级置信度。
- **`academic-integrity.md`**：清洗记录是学术诚信的硬性要求；无记录的清洗等同于不可追溯的数据操作，触碰诚信红线。
