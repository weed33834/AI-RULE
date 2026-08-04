---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 用户要为智能体设计评估/可观测/安全/进阶架构能力，需要先总览 12 项模式做选型
terminates_when: T    # 模式选型决策完成，已识别需要采用的子模块
provides: π           # 12 项高级架构模式总览、选型决策树、常见陷阱、检查清单、子文件索引
interface: R          # 输入=智能体设计需求与阶段；输出=模式选型建议 + 子文件导航
---

# 高级架构模式总览 (Advanced Patterns Overview)

---

## One-line Description / 一句话描述

> 12 项工业界验证过的高级架构模式，覆盖评估体系、可观测性、安全对齐与高级推理架构，为智能体提供超越"提示词 + 工具调用"基础形态的进阶能力蓝图。
>
> 12 industry-verified advanced architecture patterns spanning evaluation systems, observability, safety alignment, and advanced reasoning architectures — a blueprint for capabilities beyond the basic "prompt + tool call" form.

---

## When to Use / 适用场景

- 基础智能体已上线，需要从"能跑"升级到"可量化、可监控、可对抗"的工程化形态 / Moving an agent from "it runs" to a measurable, monitored, adversarially-tested engineering form
- 需要在多个平台间保证行为一致性，并量化平台适配差异 / Guaranteeing cross-platform behavioral consistency and quantifying adaptation gaps
- 安全敏感场景（金融、医疗、法务）需要对抗性测试、幻觉检测、自我批评闭环 / Safety-critical domains requiring adversarial testing, hallucination detection, and self-critique loops
- 任务复杂度超出 Naive RAG，需要 GraphRAG / Corrective RAG / Self-RAG 等进阶检索策略 / Tasks exceeding Naive RAG that need advanced retrieval strategies
- 希望把核心能力封装为标准 MCP Server，一次实现多平台复用 / Encapsulating core capabilities as a standard MCP Server for cross-platform reuse

---

## Pattern Overview / 模式总览

12 项模式按四类组织。每项模式均含核心概念、设计指南、集成模式、来源引用四节。

The 12 patterns are organized into four categories. Each pattern contains four sections: Core Concept, Design Guidelines, Integration Patterns, and Source Citation.

| # | 模式 / Pattern | 类别 / Category | 来源 / Source |
|---|---|---|---|
| 1 | 自动化评估框架设计 / Automated Eval Framework | 评估体系 / Evaluation | DeepEval / RAGAS / AgentEval / G-Eval |
| 2 | 工具调用可靠性量化 / Tool-Call Reliability Metrics | 评估体系 / Evaluation | BFCL (Berkeley) |
| 3 | τ-bench 式测试架构 / τ-bench Test Harness | 评估体系 / Evaluation | τ-bench (Sierra 2024) |
| 4 | 跨平台一致性评估 / Cross-Platform Consistency | 评估体系 / Evaluation | Chatbot Arena pairwise + Elo |
| 5 | 六类 span 模型 / Six-Type Span Model | 可观测性 / Observability | OpenTelemetry GenAI semantic conventions |
| 6 | 可观测性架构设计 / Observability Architecture | 可观测性 / Observability | Langfuse / Phoenix (Arize) / OTel GenAI |
| 7 | 对抗性测试设计 / Adversarial Testing | 安全与对齐 / Safety | Promptfoo / Garak (NVIDIA) / PyRIT (Microsoft) |
| 8 | 幻觉自动检测设计 / Hallucination Detection | 安全与对齐 / Safety | SelfCheckGPT / Vectara HEM / RAGAS |
| 9 | Constitutional Self-Critique 闭环 / Constitutional Self-Critique | 安全与对齐 / Safety | Anthropic Constitutional AI |
| 10 | Reflexion 自我反思机制 / Reflexion | 高级架构 / Advanced | Shinn et al. "Reflexion" 2023 |
| 11 | GraphRAG / Agentic RAG / 进阶检索 / Advanced RAG | 高级架构 / Advanced | Microsoft GraphRAG / CRAG / Self-RAG |
| 12 | MCP Server 封装模式 / MCP Server Encapsulation | 高级架构 / Advanced | Anthropic MCP (2024.11) |

---

## 子文件索引 / Subfile Index

12 项模式按主题拆分为 3 个子文件。Agent 先读本总览文件做选型，再按需读取对应子文件查看模式详情。

The 12 patterns are split into 3 subfiles by topic. Agents read this overview first for selection, then load the relevant subfile on demand for pattern details.

| 子文件 / Subfile | 主题 / Topic | 包含模式 / Patterns |
|---|---|---|
| `advanced-patterns-evaluation.md` | 评估体系设计 / Evaluation System Design | Pattern 1–4：自动化评估框架 / BFCL 工具调用量化 / τ-bench 测试架构 / 跨平台一致性 |
| `advanced-patterns-observability.md` | 可观测性设计 / Observability Design | Pattern 5–6：六类 span 模型 / 可观测性架构 |
| `advanced-patterns-safety.md` | 安全与对齐 + 高级架构 / Safety & Alignment + Advanced Architecture | Pattern 7–12：对抗性测试 / 幻觉检测 / Constitutional self-critique / Reflexion / GraphRAG·CRAG·Self-RAG / MCP 封装 |

---

## Pattern Selection Decision Tree / 模式选型决策树

```
你的智能体处于什么阶段？
│
├─ 还没上线，需要评估体系
│  ├─ 需要自动化 CI 评估 ──► Pattern 1 (自动化评估框架)
│  ├─ 工具调用频繁 ──► Pattern 2 (BFCL 工具调用量化)
│  ├─ 多轮对话 + 有 policy ──► Pattern 3 (τ-bench harness)
│  └─ 多平台部署 ──► Pattern 4 (跨平台一致性)
│
├─ 已上线，需要可观测性
│  ├─ 还没有 trace ──► Pattern 5 (六类 span 模型)
│  └─ 有 trace 但没闭环 ──► Pattern 6 (可观测性架构)
│
├─ 安全敏感场景
│  ├─ 担心被攻击 ──► Pattern 7 (对抗性测试)
│  ├─ 输出含数字/事实 ──► Pattern 8 (幻觉检测)
│  └─ 需要输出前对齐 ──► Pattern 9 (Constitutional self-critique)
│
└─ 任务复杂度超出基础形态
   ├─ 失败重试不智能 ──► Pattern 10 (Reflexion)
   ├─ RAG 检索不够好 ──► Pattern 11 (GraphRAG/CRAG/Self-RAG)
   └─ 想多平台复用核心能力 ──► Pattern 12 (MCP 封装)
```

选型原则：**按需选择，不要全上**。12 项模式都有成本（实现成本 + 运行成本 + 维护成本）。评估体系（1–4）和可观测性（5–6）是基础设施，建议优先；安全对齐（7–9）按场景风险等级选择；高级架构（10–12）按任务复杂度选择。

Selection principle: **choose on demand, do not adopt all 12**. Each pattern has implementation, runtime, and maintenance cost. Evaluation (1–4) and observability (5–6) are infrastructure — prioritize them. Safety alignment (7–9) depends on scenario risk. Advanced architecture (10–12) depends on task complexity.

---

## Common Pitfalls / 常见陷阱

| 陷阱 / Pitfall | 后果 / Consequence | 防护 / Prevention |
|---|---|---|
| judge 模型与被测同型号 / judge same as tested | 评估虚高，同源偏差 | 强制不同模型族 |
| golden case 直接修改 / editing golden cases in place | 破坏回归基准 | 只新增不修改，废弃标注原因 |
| 正则黑名单覆盖不全 / incomplete regex blacklist | 第一道关卡形同虚设 | 禁止响应逐条正则化，CI 检查覆盖率 |
| span 过度追踪 / over-tracing | trace 数据爆炸，存储成本高 | 只追踪关键操作，非关键操作合并 |
| 对抗测试只测单轮 / single-turn-only adversarial | 漏掉多轮渗透攻击 | 多轮对抗测试默认开启 |
| 幻觉检测全量跑 / hallucination check on all outputs | 成本爆炸 | 只检测数字类/事实类输出 |
| Reflexion 无限重试 / Reflexion infinite retry | 资源耗尽 | 最大重试 3 次，超限请求人工 |
| GraphRAG 用于简单场景 / GraphRAG for simple FAQ | 过度设计，成本高 | 简单场景用 Naive RAG |
| MCP server 默认开放写 / MCP server default write-enabled | 安全漏洞 | 默认只读，写操作显式授权 |
| self-critique 每次触发 / self-critique every output | 成本翻倍，延迟翻倍 | 按触发条件（高敏感/低置信度）选择性触发 |

---

## Truthfulness Requirements / 真实性要求（对应 AGENTS.md §1）

- **来源真实**：每项模式标注的来源（论文/框架/项目）均为公开可查。安装前建议再次访问确认仓库活跃。
- **不夸大效果**：模式描述基于来源论文/框架的公开声明，不夸大。"降低错误率 X%"这类具体数字必须有论文出处。
- **局限性标注**：每项模式在"设计指南"中标注了成本和适用边界，不隐瞒"过度设计"的风险。
- **集成模式为示意**：代码示例是结构示意，非生产就绪代码。实际集成需按项目调整。

---

## Checklist / 检查清单

### 评估体系 / Evaluation
- [ ] 智能体配备可 CI 自动运行的评估套件（≥ 20 case，含期望响应要点 + 禁止响应 + 期望工具调用序列）
- [ ] 三道判定机制（正则黑名单 → 语义必中 → LLM-as-judge CoT）已实现
- [ ] judge 模型与被测模型不同族
- [ ] 多维雷达图（正确性/效率/完整性/工具使用/推理质量/规则遵守率）已配置
- [ ] golden cases 版本化，测试集防污染机制已建立
- [ ] BFCL 五指标（selection F1 / arg match / order accuracy / hallucinated rate / missing rate）已采集
- [ ] τ-bench harness（用户模拟器 + 被测 + 判定器 + 状态校验）已配置（如适用）
- [ ] 跨平台一致性期望已标注（如多平台部署）

### 可观测性 / Observability
- [ ] 六类 span 模型（root/agent/subagent/transfer/rule/tool）已定义
- [ ] rule span 覆盖所有 P0/P1 规则触发
- [ ] 可观测性接入方案已声明（trace 格式 / 存储位置 / 隐私策略）
- [ ] 高敏感场景 Langfuse 自部署，数据不出本地
- [ ] PII 在采集时脱敏
- [ ] trace → dataset 沉淀闭环已建立（含人工审核）

### 安全与对齐 / Safety & Alignment
- [ ] 每条 P0 规则配对抗性测试套件（7 类攻击 × 50–100 变体）
- [ ] 多轮对抗测试已开启（attacker 与 target 不同族）
- [ ] 幻觉检测覆盖数字类/事实类输出（三层：SelfCheckGPT / HEM / RAGAS）
- [ ] Constitutional self-critique 触发条件已定义
- [ ] self-critique 覆盖的规则范围已声明（P0 全覆盖）

### 高级架构 / Advanced Architecture
- [ ] Reflexion 失败处理策略已定义（最大重试 + 反思深度分层）
- [ ] 反思记忆已接入情景记忆
- [ ] RAG 策略层级已定义（Naive → Graph → Corrective → Self），按任务复杂度选择
- [ ] GraphRAG 启用前已评估成本（仅跨文档推理场景启用）
- [ ] 核心工具的 MCP 封装选项已标注（规则校验/知识查询/转介执行/状态管理）
- [ ] MCP server 默认只读，写操作显式授权

---

## Cross-References / 交叉引用

- 评估框架基础 → `skills/evaluation-framework.md`
- 智能体可观测性基础 → `skills/agent-observability.md`
- 智能体测试自动化 → `skills/agent-testing-automation.md`
- 安全护栏设计 → `skills/safety-guardrails-core.md`（核心） / `skills/safety-guardrails-llm-judge.md`（LLM-as-Judge） / `skills/safety-guardrails-templates.md`（模板）
- 工具设计规范（五级副作用标注） → `skills/tool-design.md`
- 记忆系统（知识图谱记忆） → `skills/memory-systems.md`
- 知识注入策略（RAG） → `skills/knowledge-injection.md`
- 推理模式选型 → `skills/reasoning-patterns.md`
- 智能体构造方法论 → `skills/construction-playbook.md`
