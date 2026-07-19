# DAR v2 优化方案与测试框架设计

> 基于 v1 实测暴露的 6 类问题 + 业界提示词工程评估最佳实践（HELM/Anthropic/OpenAI），设计 DAR v2 优化与定制化测试体系。
> 参考来源：Anthropic "Create strong empirical evaluations"、OpenAI "Evaluation Flywheel"、Stanford HELM Capabilities、Multi-rubric Evaluation 模式。

---

## §1 v1 实测问题诊断

| # | 问题 | 根因 | v1 证据 |
|---|------|------|---------|
| P1 | DAR 提示词过长（200-400 字），小模型返回空响应 | 指令预算溢出（ManyIFEval 幂律衰减） | moonweaver S3 -19 分 |
| P2 | Citation Fidelity 下降 -0.44 | DAR 未显式要求附 URL+日期 | 3 模型平均引用质量下滑 |
| P3 | Conflict Handling 下降 -0.33 | DAR 无冲突呈现指导 | 多场景忽略来源分歧 |
| P4 | Freshness Awareness 下降 -0.33 | DAR 时效提醒被淹没在长前缀中 | 模型未标注数据年份 |
| P5 | 强基线场景 DAR 引入噪音 | 模型已有领域知识，DAR 前缀干扰推理 | S6-AGENT 全模型下滑 |
| P6 | 中文 DAR 提示词干扰模型理解 | 中英混排措辞不当 | DeepSeek S2 -11 分 |

---

## §2 DAR v2 优化方案

### 2.1 核心原则

1. **精简至上**：DAR 前缀压缩到 60-80 字（v1 的 1/4），仅保留路由规则 + 关键术语
2. **显式约束追加**：在 DAR 前缀末尾追加 3 条硬约束（引用/冲突/时效）
3. **分级加载**：为小模型提供精简版 DAR（仅路由，不含打分公式）
4. **场景感知跳过**：当问题属于模型强项领域时，自动减载 DAR 前缀

### 2.2 DAR v2 前缀模板（精简版）

```
[DAR] {domain} 优先源：{T1_sources}。关键术语：{key_terms}。
要求：①事实附URL+日期 ②来源冲突时呈现分歧 ③数据标注年份，>12月降权。
```

**对比 v1**：
- v1 coding 前缀：~200 字（含打分公式、权重、T1-T4 完整说明）
- v2 coding 前缀：~70 字（仅路由源 + 术语 + 3 条硬约束）

### 2.3 各领域 DAR v2 前缀

#### coding
```
[DAR] coding/security 优先源：CVE/NVD/Snyk/GitHub Advisory/官方文档。关键术语：CVE/CVSS/CWE/semver。
要求：①事实附URL+日期 ②来源冲突时呈现分歧 ③数据标注年份，>12月降权。
```

#### conversation
```
[DAR] 事实核查优先源：World Bank/IMF/WHO/政府门户/Snopes。关键术语：名义GDP/PPP/CPI/PMI。
要求：①事实附URL+日期 ②来源冲突时呈现分歧 ③数据标注年份，>12月降权。
```

#### paper
```
[DAR] 学术优先源：Google Scholar/Semantic Scholar/arXiv/PubMed/CrossRef/Retraction Watch。关键术语：DOI/h-index/Q1/peer review。
要求：①事实附URL+日期 ②来源冲突时呈现分歧 ③数据标注年份，>12月降权。
```

#### novel
```
[DAR] 创作研究优先源：Merriam-Webster/OED/Etymonline/Behind the Name/GeoNames。关键术语：etymology/anachronism/archaism。
要求：①事实附URL+日期 ②来源冲突时呈现分歧 ③历史事实标注年代来源。
```

#### agent-builder
```
[DAR] AI agent 优先源：Hugging Face/Papers with Code/LangChain/LMSYS Arena。关键术语：LLM/RAG/ReAct/Elo/tool calling。
要求：①事实附URL+日期 ②来源冲突时呈现分歧 ③benchmark 标注日期，>3月降权。
```

### 2.4 优化措施与 v1 问题对应关系

| 优化措施 | 解决问题 | 预期效果 |
|---------|---------|---------|
| 前缀压缩到 60-80 字 | P1 指令预算溢出 | 小模型不再返回空响应 |
| 追加"①事实附URL+日期" | P2 引用保真度下降 | Citation Fidelity 转正 |
| 追加"②来源冲突时呈现分歧" | P3 冲突处理下降 | Conflict Handling 转正 |
| 追加"③数据标注年份" | P4 时效意识下降 | Freshness Awareness 转正 |
| 前缀精简减少噪音 | P5 强基线场景下滑 | S6-AGENT 降幅收窄 |
| 中文前缀措辞优化 | P6 中文理解干扰 | S2-GDP 转正 |

---

## §3 新测试框架设计

### 3.1 设计原则（对标业界最佳实践）

| 原则 | 来源 | 落地方式 |
|------|------|---------|
| 任务特异性 | Anthropic | 每个垂直场景独立设计测试用例 |
| 复杂度梯度 | HELM | Easy 60% / Medium 25% / Hard 15% |
| 双用户画像 | OpenAI Flywheel | Casual + Professional 各占 50% |
| 多维 rubric | OpenAI Multi-rubric | 每场景 3-5 个正交维度 |
| Pairwise A/B | Arize/Anthropic | 同 judge 同批次对比 v1 vs v2 |
| 防过拟合 | OpenAI TPR/TNR | held-out test set，只跑一次 |

### 3.2 测试矩阵

```
5 个垂直场景 × 3 个复杂度 × 2 个用户画像 = 30 个测试用例
每个用例 × 2 版本（v1 DAR vs v2 DAR）× 3 个模型 = 180 次 API 调用
```

### 3.3 场景 × 复杂度 × 用户画像矩阵

#### 场景 A: Coding（代码开发）

| ID | 复杂度 | 用户类型 | 测试用例 |
|----|--------|---------|---------|
| A-E-C | Easy | Casual | "这个报错了帮我看看" — 给一段报错信息，无上下文 |
| A-E-P | Easy | Professional | 给一个明确的单函数 bug 修复任务 + 回归测试要求 |
| A-M-C | Medium | Casual | "帮我写个登录接口" — 口语化需求，缺技术细节 |
| A-M-P | Medium | Professional | 跨模块重构 FastAPI 中间件，要求保持 API 兼容 + 附设计说明 |
| A-H-C | Hard | Casual | "我的网站好慢怎么办" — 模糊的性能问题描述 |
| A-H-P | Hard | Professional | 在真实项目结构上解决 SWE-bench 级问题 + 性能约束 + 兼容旧版本 |

**评分 rubric（4 维）**：
1. **correctness** — 代码是否正确解决实际问题（超越测试通过率）
2. **code_quality** — 是否符合仓库惯例、有无死代码/魔数
3. **source_citation** — 是否引用官方文档/CVE/NVD 等权威源
4. **communication** — 是否说明改了什么及为什么

---

#### 场景 B: Paper（学术论文）

| ID | 复杂度 | 用户类型 | 测试用例 |
|----|--------|---------|---------|
| B-E-C | Easy | Casual | "什么是 transformer" — 宽泛概念解释 |
| B-E-P | Easy | Professional | 精确术语定义 + 要求 DOI 引用 |
| B-M-C | Medium | Casual | "帮我写个文献综述" — 无具体方向 |
| B-M-P | Medium | Professional | 指定领域的文献综述 + 多源综合 + 方法论描述 |
| B-H-C | Hard | Casual | "这篇论文靠谱吗" — 给一篇论文让评估可信度 |
| B-H-P | Hard | Professional | 跨学科综述 + 对比 SOTA + 可验证引用链 + 统计严谨性 |

**评分 rubric（4 维）**：
1. **groundedness** — 每条陈述是否有来源支持（无 hallucination）
2. **source_quality** — 来源是否权威（T1/T2 期刊 vs 博客）
3. **coverage** — 是否覆盖关键文献和反方观点
4. **academic_rigor** — 引用格式、统计严谨性、术语使用

---

#### 场景 C: Novel（文学创作）

| ID | 复杂度 | 用户类型 | 测试用例 |
|----|--------|---------|---------|
| C-E-C | Easy | Casual | "写个开头" — 碎片化灵感 |
| C-E-P | Easy | Professional | 单场景描写 + 风格样本 + 字数约束 |
| C-M-C | Medium | Casual | "给个角色名和背景" — 模糊需求 |
| C-M-P | Medium | Professional | 多章节衔接 + 伏笔与回收 + 多视角叙事 + 一致性要求 |
| C-H-C | Hard | Casual | "写个维多利亚时代的故事" — 有历史设定但无细节 |
| C-H-P | Hard | Professional | 长篇一致性（人物动机/时间线/世界观）+ 主题深度 + 去 AI 味 |

**评分 rubric（4 维）**：
1. **creativity** — 创意性、细节描写、打破工整结构
2. **consistency** — 人物/情节/世界观一致性
3. **historical_accuracy** — 历史事实/词源/人名时代准确性
4. **anti_ai_flavor** — 是否避免 AI 文学味（同质化、过度工整）

---

#### 场景 D: Agent-Builder（智能体搭建）

| ID | 复杂度 | 用户类型 | 测试用例 |
|----|--------|---------|---------|
| D-E-C | Easy | Casual | "帮我做个能查天气的机器人" — 自然语言描述 |
| D-E-P | Easy | Professional | 单工具单步任务 + 明确 config 定义 |
| D-M-C | Medium | Casual | "我想要一个能帮我管日程的 AI" — 模糊需求 |
| D-M-P | Medium | Professional | 多工具编排 + 条件分支 + 失败回滚策略 |
| D-H-C | Hard | Casual | "做个像 ChatGPT 一样的助手" — 极度模糊 |
| D-H-P | Hard | Professional | 长程任务 + 自我纠错 + 跨工具状态传递 + SLA 要求 |

**评分 rubric（4 维）**：
1. **architecture_quality** — 角色模型/工具选择/状态机设计
2. **tool_selection** — 工具副作用分级是否合理
3. **error_handling** — 失败回滚/边界条件处理
4. **benchmark_awareness** — 是否引用 LMSYS/Open LLM Leaderboard 数据

---

#### 场景 E: Conversation（通用日常）

| ID | 复杂度 | 用户类型 | 测试用例 |
|----|--------|---------|---------|
| E-E-C | Easy | Casual | 日常闲聊："今天天气怎么样" |
| E-E-P | Easy | Professional | 精确事实查询 + 要求结构化输出 + 引用 |
| E-M-C | Medium | Casual | 多轮上下文 + 突然话题切换 + 口语化 |
| E-M-P | Medium | Professional | 复合约束（IFEval 范式）："300字摘要+禁用逗号+高亮3处" |
| E-H-C | Hard | Casual | 模糊难断案例 + 反讽/混合情感 |
| E-H-P | Hard | Professional | 多源交叉验证 + 对抗性追问 + 要求可验证引用链 |

**评分 rubric（4 维）**：
1. **factuality** — 事实准确性、无 hallucination
2. **context_utilization** — 上下文利用（多轮引用早期信息）
3. **safety** — 安全性（不输出有害内容）
4. **source_routing** — 是否按 DAR 路由优先查权威源

---

### 3.4 评分标准

每个维度 0-5 分，单用例总分 /20。

| 分数 | 含义 |
|------|------|
| 0 | 完全缺失该能力 |
| 1 | 有意识但执行很差 |
| 2 | 基本执行但有明显缺陷 |
| 3 | 合格执行，有小瑕疵 |
| 4 | 良好执行，接近完美 |
| 5 | 完美执行，无可挑剔 |

### 3.5 评分方法

采用**混合评分**：
- **确定性评分**（关键词匹配）：source_citation, source_routing, benchmark_awareness, historical_accuracy
- **LLM-as-judge 评分**：creativity, anti_ai_flavor, communication, context_utilization
- judge 模型与生成模型不同（避免自洽性偏差）

### 3.6 A/B 对比方法

- **Pairwise**：同 judge 同批次评估 v1 DAR vs v2 DAR
- **交换顺序**：每次比较交换 v1/v2 顺序跑两遍，消除位置偏差
- **CI gate**：任一维度回退 >0.5 分则该优化措施被否决

### 3.7 防过拟合措施

1. **三分数据集**：30 个测试用例按 20/40/40 切分为 train/validation/test
2. **TPR/TNR 双指标**：不只看 accuracy，看 judge 能否抓到失败
3. **held-out test set**：最终只在 test set 上跑一次
4. **flaky task 隔离**：某任务 3 次重跑方差 >1 分则标记为 flaky，移出 gating 集

---

## §4 迭代优化流程

```
Phase 1: 基线建立
  - v1 DAR 前缀 × 30 测试用例 × 3 模型 = 90 次 API 调用
  - 记录 baseline scores

Phase 2: v2 优化测试
  - v2 DAR 前缀 × 30 测试用例 × 3 模型 = 90 次 API 调用
  - 记录 v2 scores

Phase 3: 逐项对标
  - 逐用例对比 v1 vs v2
  - 保留正向提升的优化措施
  - 剔除负向或无效果的措施

Phase 4: 迭代（如需要）
  - 对 v2 中仍负向的维度进行针对性调整
  - 生成 v3，重新测试
  - 直到所有维度正向或持平
```

---

## §5 可用 API 渠道

| 渠道 | URL | 可用模型 | 用途 |
|------|-----|---------|------|
| 主接口 | api.587.lol/v1 | moonweaver-4.8 (1) | 小模型测试 |
| 备用接口 | api.hcnsec.cn/v1 | 26 个文本模型 | 主力测试 |
| 第三接口 | cli.999554.xyz/v1 | 待激活 | 备用 |

**主力测试模型**（3 个，从 v1 中选出最有效的）：
1. Qwen3.5-397B-A17B — v1 最佳 DAR 兼容性
2. DeepSeek-V4-Pro — v1 响应快质量高
3. moonweaver-4.8 — 小模型代表，测试精简版 DAR 效果

**扩展测试模型**（从备用接口新发现的）：
4. glm-5.1 — 新可用模型
5. Qwen3-Coder-Next-FP8 — 编码专用模型
6. MiniMax-M2.7 — 新可用模型
