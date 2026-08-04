---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 出现 bug/测试失败/异常行为，需定位根因并决定是否可修复时 / Bug/test failure/abnormal behavior occurs, need to locate root cause and decide if fixable
terminates_when: T    # 最小复现路径已建立、根因已定位、RCC 已计算、修复方案已验证 / Minimal reproduction path built, root cause located, RCC computed, fix verified
provides: π           # bug 排查五步流程、Root_Cause_Confidence 公式（RCC=0.5×Reproducibility+0.3×Locality+0.2×Fix_Verification）、最小复现模板、误诊检测清单
interface: R          # 输入=bug 现象 + 上下文；输出=根因 + RCC 分数 + 修复方案 + 复现路径
---

# Bug Investigation & Root Cause Confidence / Bug 排查与根因置信度

> AI 排查 bug 时倾向"猜一个原因就改"，本文件强制用公式量化根因置信度，未达阈值禁止修复。
> 与 `truth-protocol.md` §8 Confidence Calibration 联动——RCC 是 bug 修复场景下的置信度校准输入。

## §1 核心理念 / Core Principles

bug 排查三原则：

- **先复现再定位 / Reproduce before locate**：无稳定复现路径的根因都是猜测。
- **根因不猜测 / No guessing root cause**：根因必须落到具体代码行/函数，不得停在"可能是 X 模块"。
- **修复必验证 / Fix must be verified**：修复后必须回归测试，确认 bug 消失且无新 bug。

## §2 五步排查流程 / Five-Step Investigation

```
① 复现 Reproduce → ② 隔离 Isolate → ③ 假设 Hypothesize → ④ 验证 Verify → ⑤ 修复 Fix
```

1. **复现 / Reproduce**：建立最小复现路径（见 §5），记录环境与触发条件。无法复现则 Reproducibility=0.0，禁止进入修复。
2. **隔离 / Isolate**：用二分法（注释代码、切分支、缩输入）定位到最小触发范围。每轮二分缩小一半嫌疑代码。
3. **假设 / Hypothesize**：基于隔离结果提出根因假设，落到具体代码行/函数。假设必须可证伪。
4. **验证 / Verify**：用日志/断点/单测验证假设；假设证伪则回到 ② 重新隔离，不得在证伪假设上继续修复。
5. **修复 / Fix**：修复根因，跑回归测试，计算 RCC（见 §3）。RCC < 0.5 不得提交。

> 关键约束：步骤可回退但不可跳过。跳过 ①直接 ③ 是最常见的误诊来源（见 §6）。

## §3 Root_Cause_Confidence 公式 / RCC Formula

```
RCC = 0.5 × Reproducibility + 0.3 × Locality + 0.2 × Fix_Verification
```

| 维度 / Dimension | 1.0 | 0.5 | 0.0 |
|---|---|---|---|
| Reproducibility 可复现性 | 可稳定复现 | 偶发（概率/时序触发） | 无法复现 |
| Locality 定位精度 | 精确到代码行/函数 | 定位到模块 | 仅泛泛定位 |
| Fix_Verification 修复验证 | bug 消失且无回归 | bug 消失但有回归 | 未修复/仍复现 |

> 权重设计：复现性占 50%（无复现则根因不可信）；定位精度占 30%（粗定位=猜）；修复验证占 20%（最终证据）。

计算示例：
- 稳定复现(1.0) + 定位到函数(1.0) + 修复无回归(1.0) = 0.5 + 0.3 + 0.2 = **1.0** → 高置信
- 偶发复现(0.5) + 定位到模块(0.5) + 修复有回归(0.5) = 0.25 + 0.15 + 0.1 = **0.5** → 中置信
- 无法复现(0.0) + 泛泛定位(0.0) + 未修复(0.0) = **0.0** → 禁止修复

## §4 阈值与处置 / Thresholds & Disposition

| RCC | 置信度 | 处置 |
|---|---|---|
| ≥ 0.8 | 高 | 直接修复，提交后回归测试 |
| 0.5 – 0.8 | 中 | 修复但标记"待观察"，加监控/日志跟踪 1-2 个迭代 |
| < 0.5 | 低 | **禁止修复**，必须回到 §2 深入排查，先提升复现性与定位精度 |

## §5 最小复现路径模板 / Minimal Reproduction Template

```markdown
- bug_id: <唯一标识>
- symptoms: <现象描述，含报错/日志/截图引用>
- steps_to_reproduce:
  1. <步骤 1>
  2. <步骤 2>
  3. <步骤 n>
- minimal_repro: <最小触发输入/命令/数据；越短越好>
- environment: <OS / 语言版本 / 依赖版本 / 配置>
- expected_vs_actual:
  - expected: <预期行为>
  - actual: <实际行为>
```

## §6 误诊检测清单 / Misdiagnosis Checklist

| 误诊模式 | 信号 | 处置 |
|---|---|---|
| 改了症状没改根因 | 症状短暂消失后又复现 | 回到 §2 ②隔离，重找根因 |
| 改 A 修了 B（巧合修复） | 改动与根因无因果链路 | 验证因果：撤改动看是否复现 |
| 修复引入新 bug（回归） | 回归测试失败 | Fix_Verification 降为 0.5 或 0.0 |
| 偶发 bug 当稳定 bug 修 | Reproducibility 虚标为 1.0 | 强制按 0.5 计 RCC |
| 跳过复现直接猜测 | 无 steps_to_reproduce | 禁止修复，先建复现路径 |

## §7 失败信号 / Failure Signals

| 信号 | 描述 | 修复 |
|---|---|---|
| 未建复现路径就改代码 | 跳过 §2 ① | 强制先填 §5 模板 |
| 根因停在"可能是 X" | Locality ≤ 0.5 | 继续二分隔离到行/函数 |
| RCC < 0.5 仍提交修复 | 违反 §4 阈值 | 阻断提交，回 §2 |
| 修复后未跑回归测试 | Fix_Verification 缺失 | 强制跑全量回归 |
| 连续 3 次修复仍复现 | 根因误判 | 触发 governance.md §6 Reflexion |

## §8 与其他文档的关系 / Relationship with Other Documents

- **`truth-protocol.md` §8**：RCC 作为 bug 修复场景的置信度输入，校准"我说修好了"的自评。
- **`self-refinement.md`**：修复后用 Reflexion 自检——是否真的改了根因、是否引入回归。
- **`governance.md` §6**：连续 3 次修复失败触发 Reflexion 反思闭环，记录教训避免重撞。
- **`code-review-quality.md`**：修复提交后需经过代码审查，确认 RCC 评分与改动匹配。
