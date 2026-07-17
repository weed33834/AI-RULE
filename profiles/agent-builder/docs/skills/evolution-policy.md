# evolution-policy.md — 智能体迭代演进策略 / Agent Evolution Policy

---

## 1. 一句话描述 / One-sentence Description

**中文：** 以对话日志为证据、以"发现→修改→回归→A/B→上线"为闭环、以语义化版本为锚点，在"红线永不放松、行为规则可控放松、效率规则可删"的演进原则下，让智能体持续变好而不变坏。

**English:** Drive continuous improvement-without-regression through an evidence-based log analysis loop (discover → modify → regress → A/B → ship), anchored by semantic versioning, under the principle that red-lines never relax, behavior rules relax controllably, and efficiency rules may be removed.

---

## 2. 适用场景 / Applicable Scenarios

| 场景 / Scenario | 说明 / Description |
|---|---|
| 已上线智能体持续优化 / Live agent optimization | 需要基于真实流量迭代而非凭直觉改 prompt |
| 多人协作维护 / Multi-maintainer | 需要 版本 + 变更记录 防止互相覆盖 |
| 高风险领域 / High-stakes domains | 医疗/金融/法律等，演进不能引入安全回退 |
| A/B 驱动产品 / A/B-driven products | 需要量化验证改动收益再全量 |
| 合规审计 / Compliance audit | 需要可追溯的版本与变更历史 |

**不适用 / Not applicable：** 还未上线、无真实日志的原型阶段——此时应先做用例驱动的设计验证，再进入演进闭环。

---

## 3. 核心方法论 / Core Methodology

### 3.1 对话日志分析方法（Log Analysis Methods）

演进以日志为证据。三类分析方法按频率分层执行：

**a) 量化指标监控（高频，每日/实时）**
- **任务完成率 / Task completion rate**：以结束信号判定成功结束的比例。
- **平均轮数 / Avg turns per task**：过长提示流程低效或澄清不足。
- **转人工率 / Handoff rate**：升高说明能力边界被频繁触及。
- **护栏触发率 / Guardrail trigger rate**：升高说明越界输入增多或防护失效。
- **用户负面信号 / Negative signals**：如"不对""算了""不是这个"等更正/放弃信号占比。

**b) 失败模式聚类（中频，每周）**
- 抽取"未成功结束"与"含负面信号"的会话。
- 按失败原因聚类：意图识别错误 / 信息收集不全 / 工具调用失败 / 越界 / 人格漂移 / 上下文丢失。
- 每类取代表性样本 3–5 条，作为优化输入。

**c) 深度个案复盘（低频，按需）**
- 对严重案例（如安全事件、客诉）逐轮还原。
- 定位根因：是 prompt / 状态机 / 工具 / 模型 / 上下文 哪一层的问题。

**d) 轨迹洞察（Trajectory Insights，跨数百会话，每周/每月）**

> 来源：Amazon Bedrock AgentCore 轨迹洞察。补足单会话复盘看不到的全局规律。

跨数百个会话自动发现失败模式，能力包括：

- **沉默失败检测 / Silent-failure detection**：发现"无错误信号但行为错误"的会话。这类会话没有抛异常、没有触发护栏、用户也没有明确点"踩"，但智能体自信地给出了错误答案。检测手段：
  - 交叉验证：用 LLM-as-Judge 或事后人工抽检，对"看似成功"的会话做正确性复核。
  - 行为偏移信号：对比同类任务的成功会话轨迹，找出步骤数、工具调用模式异常但未报错的会话。
  - 用户隐式信号：会话结束后短期内用户重新发起相似请求（说明上次没解决）。
- **失败轨迹聚类 / Failure-trajectory clustering**：按**执行路径相似度**聚类，而非仅按错误类型。同一错误类型可能根因不同（如"工具调用失败"可能是 prompt 给错参数、也可能是工具本身 bug、也可能是上下文丢失导致选错工具）。聚类维度：
  - 工具调用序列（哪些工具、什么顺序）
  - 状态机路径（经过了哪些阶段、在哪里回退）
  - 上下文长度与压缩时点
  - 用户更正/重复提问的位置
- **根因推断 / Root-cause inference**：从轨迹模式推断问题出在哪一层：
  | 轨迹特征 / Pattern | 推断根因 / Inferred Layer |
  |---|---|
  | 意图识别错误但后续工具调用正确 | prompt（意图归一化部分） |
  | 阶段跳转错误或卡在某阶段 | 状态机 |
  | 工具参数错误或工具未触发 | 工具（描述/参数/schema） |
  | 同一输入在不同模型版本上结果差异大 | 模型 |
  | 长会话尾部漂移、目标丢失 | 上下文（压缩过度/未重注入） |
  | 沉默失败但轨迹与成功会话高度相似 | 模型/知识（可能知识本身有误） |

**轨迹洞察与 a/b/c 的关系**：a/b/c 是"已知问题查详情"，轨迹洞察是"未知问题先发现"。建议先跑轨迹洞察发现候选失败模式，再用 b 的失败模式聚类和 c 的个案复盘深入。

**日志字段最低要求：** `session_id`、`turn_index`、`user_input`、`agent_output`、`intent`、`state_snapshot`、`tool_calls`、`guardrail_flags`、`end_signal`、`timestamp`。

### 3.2 提示词优化循环（Prompt Optimization Loop）

```
发现(Discover) → 修改(Modify) → 回归(Regress) → A/B → 上线(Ship)
```

1. **发现 / Discover**：从日志分析中得到一个具体、可验证的问题假设（如"退款原因收集阶段，用户说'坏了'时 30% 未被识别为退款意图"）。假设必须可量化。
2. **修改 / Modify**：针对假设改 prompt / 状态机 / 工具。**每次只改一个变量**，否则无法归因。
3. **回归 / Regress**：在固定测试集（含护栏用例、人格用例、历史失败样本）上跑回归。
   - 护栏用例**任一失败 → 禁止进入下一步**。
   - 目标指标改善 + 无回归 → 进入 A/B。
4. **A/B**：小流量灰度对比新旧版本，按预设指标与显著性判断。
   - 显著性判断需足够样本量（**需验证：具体样本量阈值按业务流量与统计方法定**）。
5. **上线 / Ship**：全量发布，记录版本与变更说明，加入回归集防腐化。

### 3.3 版本管理（Semantic Versioning）

采用语义化版本 `MAJOR.MINOR.PATCH`，但赋予智能体语义：

| 段 / Segment | 触发条件 / Trigger | 示例 |
|---|---|---|
| **MAJOR** | 人格边界/角色定位变更、能力范围重大重构、迁移平台 | 1.x.x → 2.0.0 |
| **MINOR** | 新增工具/新流程阶段、prompt 行为优化、能力增强 | 1.3.x → 1.4.0 |
| **PATCH** | 修 bug、措辞微调、参数小调、不改变行为语义 | 1.2.3 → 1.2.4 |

**配套要求：**
- 每个 config.yaml 必须有 `version` 字段（语义化）。
- 每次发布附 `CHANGELOG`：版本号、日期、变更类型、变更说明、回归结果。
- 可回滚：保留历史版本 config，出问题可即时切回。

### 3.4 演进原则（Evolution Principles）

三类规则放松力度严格不同，这是演进的不可逾越红线：

```
┌─────────────────────────────────────────────────────────┐
│  安全护栏 & 真实性红线 ──► 永不放松 (Never relax)        │
│  - 只能加强, 不能削弱                                    │
│  - 任何版本都不允许降低护栏强度或放宽真实性要求          │
│  - 若改动导致护栏回归失败 → 立即回滚, 不可上线           │
├─────────────────────────────────────────────────────────┤
│  行为规则 ──► 可控放松 (Relax controllably)              │
│  - 语气/详略/流程步骤可根据数据调整                      │
│  - 必须有 A/B 数据支撑, 且不触发护栏回归                  │
│  - 放松幅度小步迭代, 不一次性大改                        │
├─────────────────────────────────────────────────────────┤
│  效率规则 ──► 可删除 (May remove)                        │
│  - 压缩策略/轮数限制/token 预算等可按需删改              │
│  - 删除前确认不影响正确性与护栏                          │
│  - 删除后监控相关指标无恶化                              │
└─────────────────────────────────────────────────────────┘
```

**判断一条规则属于哪类：** 问"如果放松它，最坏后果是什么？"
- 涉及安全/虚假信息/越界 → 红线类，永不放松。
- 涉及用户体验/流程细节 → 行为类，可控放松。
- 涉及性能/成本/长度 → 效率类，可删改。

### 3.5 技能生命周期管理（Skill Lifecycle Management）

> 来源：Hermes Agent 自主技能创建 + MUSE-Autoskill 框架。把技能（Skill 文档）当作有生命周期的资产，而非一次性写完就丢的文档。

#### 3.5.1 五阶段流程图 / Five-Stage Flow

```
┌─────────────────────────────────────────────────────────────┐
│              技能生命周期 / Skill Lifecycle                   │
└─────────────────────────────────────────────────────────────┘

  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
  │ 1.创建  │───▶│ 2.使用  │───▶│ 3.评估  │───▶│ 4.改进  │───▶│ 5.淘汰  │
  │ Create  │    │  Use    │    │Evaluate │    │ Improve │    │ Retire  │
  └─────────┘    └─────────┘    └────┬────┘    └────┬────┘    └────┬────┘
       ▲              │              │              │              │
       │              │              │ 评分回升     │ 评分仍低     │
       │              │              └──回到 使用───┘              │
       │              │                            └──────────────┘
       │              │                            连续 N 次低于阈值
       │              │                            → 归档不再自动加载
       │              │
       │   下次相似任务自动检索加载
       │
   完成复杂任务后
   自动提取可复用技能文档
```

#### 3.5.2 各阶段定义 / Stage Definitions

1. **创建 / Create**：智能体完成一次复杂任务后，自动提取可复用的技能文档。提取内容包含：任务模式 + 关键决策点 + 工具用法 + 失败教训。新技能初始置信度为 0.5（既不轻信也不忽视）。
2. **使用 / Use**：下次遇到相似任务时，通过任务-技能匹配（语义相似度 + 任务类型匹配）自动检索并加载该技能文档。加载后在本次会话的使用结果计入评估。
3. **评估 / Evaluate**：跟踪每个技能的三个核心指标（见 3.5.3）。评估在每次使用后即时更新，并按周汇总。
4. **改进 / Improve**：根据使用反馈自动优化技能内容——补充缺失步骤、修正错误示例、增加边界情况。改进后版本号 +0.0.1，回归测试通过才生效。
5. **淘汰 / Retire**：连续 N 次（默认 N=5）评分低于阈值（默认 0.4）的技能归档，不再自动加载。归档不删除，保留供人工复查与可能的复活。

#### 3.5.3 评估指标 / Evaluation Metrics

| 指标 / Metric | 计算方式 / Calculation | 权重 / Weight |
|---|---|---|
| 成功率 / Success rate | 使用该技能后任务成功完成的比例 | 0.5 |
| 平均耗时 / Avg duration | 使用该技能的会话平均轮数/耗时（与基线对比） | 0.2 |
| 用户反馈评分 / User feedback | 用户显式赞/踩 + 隐式信号（是否重新发起相似请求） | 0.3 |

综合评分 `score = 0.5*success + 0.2*duration_norm + 0.3*feedback`，范围 0.0-1.0。

#### 3.5.4 改进策略 / Improvement Strategy

- **缺失步骤补充**：若使用该技能的会话中频繁出现技能未覆盖的步骤，自动将该步骤补入技能文档。
- **错误示例修正**：若技能中的示例被频繁误用，替换为更清晰的示例。
- **边界情况增加**：若技能在某类输入上成功率骤降，补充该类输入的处理说明。
- **改进门槛**：改进需有 ≥ 3 次使用样本支撑，避免单次偶发误判；改进后须通过回归测试。

### 3.6 自主技能策展器（Autonomous Skill Curator）

> 来源：Hermes Agent v0.12.0 Curator 机制。定期自动运行，对技能库做体检。

#### 3.6.1 运行周期 / Run Cycle

- 默认每月运行一次（可在配置中改为每周）。
- 运行时机：低峰期（如每周日凌晨），避免影响在线服务。
- 运行输入：全部技能文档 + 各技能近一周期内的使用指标 + 用户反馈。

#### 3.6.2 策展规则 / Curation Rules

策展器对每个技能执行以下检查：

1. **打分 / Score**：按 3.5.3 的指标计算每个技能的综合评分。
2. **相似度合并检测 / Merge detection**：计算技能两两之间的语义相似度；相似度 > 0.85 的对标记为"建议合并"候选。
3. **淘汰检测 / Retirement detection**：标记连续 N 次评分低于阈值的技能为"建议归档"。
4. **新增建议 / New-skill suggestion**：从近期高频出现但无对应技能的任务模式中，提取"建议新增技能"候选。

#### 3.6.3 策展报告格式 / Curation Report Format

```yaml
# skill_curation_report.yaml — 策展报告 / Curation Report
review_period:
  from: "2026-06-13"
  to: "2026-07-13"
  generated_at: "2026-07-13T03:00:00Z"
summary:
  skills_reviewed: 24
  merge_suggestions: 2
  retire_suggestions: 1
  new_skill_suggestions: 3
merge_suggestions:
  - skill_a: "docs/skills/prompt-patterns.md"
    skill_b: "docs/skills/conversation-design.md"
    similarity: 0.88
    reason: "两文档在'意图澄清'部分高度重叠"
retire_suggestions:
  - skill: "docs/skills/legacy-x.md"
    consecutive_low_scores: 6
    avg_score: 0.32
    reason: "连续 6 次评分低于 0.4 阈值"
new_skill_suggestions:
  - candidate_task_pattern: "多步骤报表生成 + 邮件分发"
    occurrence_count: 47
    reason: "近一月出现 47 次但无对应技能文档"
next_action: "需用户确认后执行合并/归档/新增"
```

#### 3.6.4 安全约束（P0 级，不可例外）/ Safety Constraints

- **只建议不执行**：策展器输出的所有合并/淘汰/新增建议，必须经用户确认后才生效。策展器本身不修改任何技能文件。
- **可追溯**：每次策展运行生成一份完整报告存档，包含所有评分依据。
- **可回滚**：用户确认执行后，被合并/归档的技能原文保留在 `archive/` 目录，可一键恢复。
- **不自动删除**：归档 ≠ 删除；归档的技能不再自动加载，但文件保留供复查。

---

## 4. 决策树 / 流程图 — Decision Tree

```
从日志发现一个问题假设 / Discover a hypothesis from logs
   │
   ▼
该假设是否可量化? / Is it quantifiable?
   ├─ NO ──► 重新定义假设, 直到可量化
   └─ YES
   │
   ▼
定位规则类别 / Classify the rule
   │
   ├─ 安全护栏/真实性? ──► 红线类: 只能加强, 改动须更严
   ├─ 行为规则? ─────────► 行为类: 可放松, 需 A/B
   └─ 效率规则? ─────────► 效率类: 可删改, 监控指标
   │
   ▼
修改(每次只改一个变量) / Modify (one variable at a time)
   │
   ▼
回归测试 / Regression
   │
   ├─ 护栏用例任一失败? ──► YES ──► 禁止上线 → 回滚 → 重新修改
   │                       └─ NO
   ├─ 目标指标改善 & 无回归? ──► NO ──► 记录负结果 → 重新修改或放弃
   │                            └─ YES
   │
   ▼
A/B 灰度 / A/B canary
   │
   ├─ 显著正向 & 护栏无恶化? ──► NO ──► 保留旧版 → 归因分析
   │                            └─ YES
   │
   ▼
上线 / Ship
   │
   ├─ 升版本号(MAJOR/MINOR/PATCH 按 3.3) / Bump version
   ├─ 写 CHANGELOG / Write changelog
   ├─ 新用例并入回归集 / Add cases to regression set
   └─ 监控上线后指标 / Monitor post-ship metrics
```

---

## 5. 模板示例 — Template Example

### 5.1 演进检查清单（可直接用于每次发布评审）

```yaml
# evolution_review.yaml — 演进发布评审 / Evolution Release Review

release:
  version_from: "1.3.2"
  version_to: "1.4.0"            # MINOR: 新增退款进度查询流程
  date: "2026-07-12"
  changelog:
    - type: "feature"
      desc: "新增退款进度查询工具 query_refund_status"
    - type: "prompt"
      desc: "info_gathering 阶段增加退款进度主动告知"

hypothesis:
  statement: "用户在等待退款时重复询问进度, 占负面信号会话的 18%"
  metric_before: { negative_signal_rate: 0.18, avg_turns: 7.2 }
  metric_after:  { negative_signal_rate: 0.11, avg_turns: 5.8 }

regression:
  guardrail_cases: { total: 24, passed: 24, failed: 0 }
  persona_cases:   { total: 18, passed: 18, failed: 0 }
  historical_fail_samples: { total: 12, passed: 12, failed: 0 }
  verdict: "pass"               # 护栏 0 失败才可继续

ab_test:
  control_version: "1.3.2"
  treatment_version: "1.4.0"
  traffic_split: { control: 50, treatment: 50 }
  sample_size: 2400             # 需验证: 按业务流量与统计方法定
  significance: "p<0.05"
  result: "treatment 显著优于 control, 护栏无恶化"

rule_classification:
  - rule: "退款须在 3 工作日到账(真实性)"
    class: "red_line"           # 永不放松
    action: "保持, 未改动"
  - rule: "info_gathering 主动告知退款进度(行为)"
    class: "behavior"           # 可控放松
    action: "新增, A/B 验证通过"
  - rule: "上下文压缩阈值 85%(效率)"
    class: "efficiency"         # 可删改
    action: "未改动"

rollback:
  enabled: true
  previous_config_path: "configs/v1.3.2.yaml"
  trigger_on: ["guardrail_rate > baseline*1.2", "task_completion_rate < baseline*0.95"]
```

### 5.2 对话日志最小字段模板

```yaml
# 单轮日志记录 / Per-turn log record
log:
  session_id: "sess_20260712_001"
  turn_index: 4
  timestamp: "2026-07-12T10:23:11Z"
  version: "1.3.2"
  user_input: "那个不对，是收到的时候坏了"
  agent_output: "我之前理解退款原因是'不喜欢'，应为'商品破损'，对吗？"
  intent: { action: "correct", target: "refund_reason", constraints: [] }
  state_snapshot:
    stage: "info_gathering"
    collected: { order_id: "A123" }
    pending: ["refund_reason"]
  tool_calls: []
  guardrail_flags: []
  end_signal: null
  negative_signal: true         # 含"不对"更正信号
  tokens: { prompt: 1820, completion: 46 }
```

### 5.3 CHANGELOG 模板

```markdown
# CHANGELOG

## [1.4.0] — 2026-07-12
### Added
- 新增 query_refund_status 工具（退款进度查询）
- info_gathering 阶段主动告知退款进度
### Regression
- 护栏用例 24/24 通过；人格用例 18/18 通过；历史失败样本 12/12 通过
### A/B
- treatment(1.4.0) vs control(1.3.2)，n=2400，p<0.05，负面信号率 0.18→0.11
### Rule changes
- 行为类(可控放松): 新增主动告知；红线类/效率类未改动

## [1.3.2] — 2026-07-01
### Fixed
- 修复 order_id 含空格时工具调用失败的问题（PATCH）
```

---

## 6. 常见陷阱 / Common Pitfalls

1. **一次改多个变量 / Changing multiple variables at once**
   - 现象：同时改 prompt + 换模型 + 调温度，指标变化无法归因。
   - 纠正：每次只改一个变量，隔离效果。

2. **护栏回归未通过仍上线 / Shipping with guardrail regression**
   - 现象：为追新功能，对护栏用例失败视而不见。
   - 纠正：护栏用例 0 失败是硬门槛，任一失败立即回滚。

3. **放松红线类规则 / Relaxing red-line rules**
   - 现象：为提升完成率，放宽"不编造信息"约束。
   - 纠正：红线永不放松，只能加强。

4. **A/B 样本不足就下结论 / A/B with insufficient sample**
   - 现象：几十条流量就判断"显著提升"。
   - 纠正：按统计方法确定样本量与显著性阈值（标注需验证）。

5. **无版本号或版本不语义化 / No version or non-semantic versioning**
   - 现象：用"final""final2""final_真的最终"命名，无法回滚定位。
   - 纠正：强制语义化版本 + CHANGELOG。

6. **负结果不记录 / Not recording negative results**
   - 现象：改了没效果就默默丢弃，下次又踩同一坑。
   - 纠正：负结果也写入 CHANGELOG/实验记录，避免重复试错。

7. **用主观感受替代日志证据 / Gut feel over log evidence**
   - 现象："我觉得这样更好"就改 prompt。
   - 纠正：演进必须有可量化的日志假设与指标。

8. **删除效率规则后不监控 / Removing efficiency rules without monitoring**
   - 现象：删了压缩策略，上下文成本上升且正确性暗中恶化。
   - 纠正：删除后持续监控相关指标，恶化即恢复。

9. **历史失败样本不并入回归集 / Not adding failure cases to regression set**
   - 现象：修过的 bug 在后续版本复发。
   - 纠正：每个修复的失败样本永久并入回归集防腐化。

10. **沉默失败被忽略 / Ignoring silent failures**
    - 现象：会话无错误信号、无用户点踩，看似成功，实则给了错误答案。只看错误日志会漏掉这类失败。
    - 纠正：定期运行轨迹洞察的沉默失败检测，对"看似成功"的会话做 LLM-as-Judge 或人工抽检复核。

11. **按错误类型聚类而非轨迹聚类 / Clustering by error type instead of trajectory**
    - 现象：把所有"工具调用失败"归为一类，但根因可能是 prompt/工具/上下文三层之一，混在一起无法定位。
    - 纠正：失败轨迹聚类按执行路径相似度聚类，再对每类做根因推断。

12. **技能只创建不淘汰 / Skills created but never retired**
    - 现象：技能库持续膨胀，低效/过时技能拖慢检索、误导加载。
    - 纠正：落地技能生命周期淘汰阶段，连续 N 次低分技能归档；定期跑策展器体检。

13. **策展器自动执行合并/淘汰 / Curator auto-executing merges/retirements**
    - 现象：策展器绕过用户确认直接修改技能文件，误删有用技能。
    - 纠正：策展器只建议不执行；合并/淘汰/新增必须用户确认；归档不删除、可回滚。

---

## 7. 检查清单 — Checklist

- [ ] 日志含最低字段集，可支撑量化分析 / logs contain minimum fields for quantitative analysis
- [ ] 已建立量化指标监控（完成率/轮数/转人工/护栏触发/负面信号）/ quantitative metrics monitored
- [ ] 每周执行失败模式聚类，产出代表性样本 / weekly failure clustering with samples
- [ ] 优化假设可量化，每次只改一个变量 / hypothesis quantifiable, one variable per change
- [ ] 回归集含护栏用例、人格用例、历史失败样本 / regression set covers guardrails, persona, historical failures
- [ ] 护栏用例 0 失败才允许进入 A/B / zero guardrail failures before A/B
- [ ] A/B 有预设指标、样本量、显著性阈值 / A/B has preset metrics, sample size, significance
- [ ] 版本号语义化，CHANGELOG 完整 / semantic versioning, complete changelog
- [ ] 红线类规则仅加强不放松 / red-line rules only strengthened
- [ ] 行为类规则放松有 A/B 支撑 / behavior relaxation A/B-backed
- [ ] 效率类规则删改后有监控 / efficiency changes monitored post-removal
- [ ] 历史失败样本已并入回归集防腐化 / historical failures added to regression set
- [ ] 负结果有记录，可回滚到上一版本 / negative results recorded, rollback available
- [ ] 已运行轨迹洞察（沉默失败检测 + 轨迹聚类 + 根因推断）/ trajectory insights run (silent-failure, clustering, root-cause)
- [ ] 技能生命周期五阶段已落地（创建→使用→评估→改进→淘汰）/ skill lifecycle 5 stages implemented
- [ ] 技能评估指标（成功率/耗时/反馈）已采集与汇总 / skill evaluation metrics collected
- [ ] 自主策展器定期运行，输出策展报告 / curator runs periodically with report
- [ ] 策展器只建议不执行，合并/淘汰/新增经用户确认 / curator suggests only, user confirms actions
- [ ] 归档技能保留可回滚，不自动删除 / archived skills retained, rollbackable, not auto-deleted

## 进阶：12 项高级架构模式 / Advanced: 12 Architecture Patterns

> 本文档的演进策略在 `advanced-patterns.md` 中有进一步的方法论支撑：
> - **模式 1（自动化评估框架设计）**：为技能评估提供量化方法论——三道判定 + 六维雷达图 + CI 集成回归测试，将技能评估从主观判断升级为可量化、可回归的质量门禁。
> - **模式 10（Reflexion 自我反思机制）**：为技能改进提供闭环机制——失败时三步循环（分析原因 → 调整策略 → 重试），反思记忆存入 memory 避免重复犯错，与技能生命周期的"改进"阶段联动。来源 Shinn et al. 2023。
