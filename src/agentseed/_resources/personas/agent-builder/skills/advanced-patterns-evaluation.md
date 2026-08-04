---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 用户要设计智能体的评估体系（自动化评估、工具调用量化、多轮测试、跨平台一致性）
terminates_when: T    # 评估体系四项模式（Pattern 1-4）的设计已落地为可 CI 运行的方案
provides: π           # 评估体系设计模式（自动化评估框架 / BFCL / τ-bench / 跨平台一致性）、golden case 模板、检查清单
interface: R          # 输入=智能体评估需求与平台部署情况；输出=评估方案 + golden case 模板 + 检查清单
---

# 评估体系设计模式 (Evaluation System Design Patterns)

---

## Category 1: Evaluation System Design / 第一类：评估体系设计

### Pattern 1: Automated Evaluation Framework Design / 自动化评估框架设计

#### 核心概念 / Core Concept

把"人工 spot-check"升级为可 CI 自动运行的评估管线。核心是**三道判定机制**——任何被测 case 必须依次通过三道关卡，全部通过才算合格：

- **第一道：正则黑名单**。把"禁止响应"用正则表达死。例如客服智能体的禁止响应包含"我帮你下订单"（不能替用户下单），则用正则匹配该短语，命中即判失败。这一道成本最低、速度最快，只做精确字符串/模式判定。
- **第二道：语义必中**。把"期望要点"用语义匹配判死。每个 golden case 标注若干"必中要点"（如"必须告知退货时限 7 天"），用 embedding 相似度或轻量 LLM 判定实际输出是否覆盖每条要点。这一道处理"说法不同但意思一致"的情况。
- **第三道：LLM-as-Judge（G-Eval 式 CoT 评审）**。前两道通过后，用 LLM 评审员做 CoT（思维链）式打分。G-Eval 思路：先让 judge 模型生成评审 CoT（"这条输出好在哪、差在哪、应该给几分"），再据此输出最终分数。CoT 让评审更稳定、可解释。

关键约束：**judge 模型与被测模型不能同型号**。同型号会产生同源偏差（同一家族的模型对同类错误彼此宽容）。例如被测用 GPT-4o，judge 用 Claude 或 Gemini；被测用 Claude，judge 用 GPT-4o。

评估维度从"通过/失败"二值升级为**多维雷达图**：正确性 / 效率 / 完整性 / 工具使用 / 推理质量 / 规则遵守率。六维分别打分（0–1 或 0–5），可视化成雷达图后能一眼看出智能体的短板在哪个维度，而非只看到"83% 通过率"这一个数字。

#### 设计指南 / Design Guidelines

1. **golden cases 版本化**：评估数据集纳入 git，每次规则变更记录新增/废弃了哪些 case。禁止直接修改已有 case——修改即破坏回归基准，要新增 case 修问题，废弃 case 标注废弃日期和原因。
2. **测试集防污染**（SWE-bench Live 思想）：定期轮换测试集，防止被测模型在训练数据中见过测试题导致虚高。高价值 case 可拆分为"公开训练用"和"私有评测用"两份。
3. **CI 集成为 pytest 风格断言**：每个 case 写成 `assert agent_response_passes(response, case)` 形式，规则变更后 CI 自动回归。失败的 case 在 CI 报告里显示是哪一道关卡挂了（正则/语义/judge）。
4. **judge 评审要可复现**：judge 的 CoT 和最终分数都要记录到 trace，便于事后复核。同一 case 多次评审的方差 > 0.2 时触发人工复核。
5. **多维雷达图必须有阈值线**：每维设定最低线（如规则遵守率不得低于 0.9），低于线即判失败，即使其他维度很高。

#### 集成模式 / Integration Patterns

```python
# 三道判定管线 / Three-gate pipeline
def evaluate_case(agent_response, golden_case):
    # Gate 1: regex blacklist
    for pattern in golden_case.forbidden_patterns:
        if re.search(pattern, agent_response):
            return {"passed": False, "gate": "regex_blacklist", "hit": pattern}
    # Gate 2: semantic must-hit
    for point in golden_case.required_points:
        if not semantic_match(agent_response, point, threshold=0.75):
            return {"passed": False, "gate": "semantic_must_hit", "missed": point}
    # Gate 3: LLM-as-judge with CoT (judge model != tested model)
    score = g_eval_judge(agent_response, golden_case.rubric,
                         judge_model="claude" if agent_under_test_family != "claude" else "gpt-4o")
    return {"passed": score.passed, "gate": "llm_judge",
            "radar": score.radar, "cot": score.cot}

# pytest 风格断言 / pytest-style assertion
def test_customer_service_refund_policy():
    resp = agent.run("我想退货，多久能退？")
    result = evaluate_case(resp, GOLDEN["refund_policy"])
    assert result["passed"], f"failed at {result['gate']}: {result}"
```

集成到 AGENTS.md §12 评估框架：三道判定替换原"四维评估"中的"准确率"维度判定方式，多维雷达图替换"通过率"单一指标。规则变更触发回归评估。

#### 来源引用 / Source Citation

- DeepEval（Confident AI）：`https://github.com/confident-ai/deepeval`，pytest 风格 LLM 评估框架
- RAGAS：`https://github.com/explodinggradients/ragas`，RAG 四维评估
- AgentEval（NVIDIA）：智能体任务级评估
- G-Eval：Liu et al. "G-Eval: NLG Evaluation using GPT-4 with CoT and Forms" (2023)
- SWE-bench Live：`https://www.swebench.com/`，动态防污染思想

---

### Pattern 2: Tool-Call Reliability Quantification / 工具调用可靠性量化

#### 核心概念 / Core Concept

工具调用是智能体"动手"的部分，但绝大多数评估只看"最终回答对不对"，忽略了工具调用本身的质量。BFCL（Berkeley Function Calling Leaderboard）把工具调用拆成 5 个可独立量化的指标，让"工具调用好不好"从模糊感觉变成精确数字：

1. **Tool Selection F1**：该调哪些工具选对了吗？把"应调工具集"和"实调工具集"做 F1。漏调（false negative）和误调（false positive）都扣分。
2. **Argument Exact Match**：参数填对了吗？逐参数比对，类型、值都一致才算匹配。
3. **Call Order Accuracy**：调用顺序对吗？有依赖的工具（先查再改）顺序错了会失败。
4. **Hallucinated Tool Call Rate**：调用了不存在的工具吗？模型"幻觉"出系统里没有的工具名。
5. **Missing Tool Call Rate**：该调没调的工具占应调工具的比例。

评估方法分两层：**AST-based（结构等价）** 和 **semantic match（语义等价）**。AST-based 比对调用结构（工具名 + 参数 schema），快速但严格——"北京" ≠ "北京市"。semantic match 在 AST 不等时再判语义等价（"北京" = "北京市" = "Beijing"），避免假阴性。

#### 设计指南 / Design Guidelines

1. **每个 golden case 标注"期望工具调用序列"**作为结构化字段，而非自然语言描述。字段格式：`[{tool, args, order}]`，CI 自动比对实际 vs 期望。
2. **AST 比对优先，语义比对兜底**：先用 AST 快筛（毫秒级），AST 不等的再用 LLM 判语义等价（秒级），控制成本。
3. **5 个指标独立报告**：不要合成单一"工具调用分"。合成后定位不了问题——是选错工具还是参数填错？分开看才能定位。
4. **幻觉工具调用率是 P0 监控项**：调用不存在的工具往往意味着模型在"编造能力"，必须告警。

#### 集成模式 / Integration Patterns

```yaml
# golden case 结构化字段 / structured golden case
- id: refund_lookup_001
  user_input: "查一下订单 A123 能不能退"
  expected_tool_calls:
    - order: 1
      tool: query_order
      args: {order_id: "A123"}
      arg_match: exact
    - order: 2
      tool: check_refund_policy
      args: {order_status: "<from step 1>"}
      arg_match: semantic   # 状态值可能表述不同
  forbidden_tool_calls: [cancel_order, issue_refund]  # 查询场景禁止写操作
```

```python
def evaluate_tool_calls(actual_calls, expected_calls):
    return {
        "selection_f1": tool_set_f1(actual_calls, expected_calls),
        "argument_exact_match": arg_match_rate(actual_calls, expected_calls, mode="exact"),
        "argument_semantic_match": arg_match_rate(actual_calls, expected_calls, mode="semantic"),
        "call_order_accuracy": order_accuracy(actual_calls, expected_calls),
        "hallucinated_tool_call_rate": hallucinated_rate(actual_calls, available_tools),
        "missing_tool_call_rate": missing_rate(actual_calls, expected_calls),
    }
```

集成到 AGENTS.md §5 工具编排与 §12 评估框架：BFCL 五指标作为工具调用质量的标准度量，与五级副作用标注互补——副作用标注管"该不该调"，BFCL 管"调得对不对"。

#### 来源引用 / Source Citation

- BFCL（Berkeley Function Calling Leaderboard）：`https://gorilla.cs.berkeley.edu/leaderboard.html`，UC Berkeley
- BFCL 论文：Patil et al. "API-Bank" / Gorilla 项目相关 (2024)
- AST 比对方法：借鉴编译器 AST diff 思想

---

### Pattern 3: τ-bench Test Harness Architecture / τ-bench 式测试架构

#### 核心概念 / Core Concept

τ-bench（Sierra 2024）提出了一种比"单轮问答评估"更接近真实部署的测试架构。核心是**三角色架构**：

- **用户模拟器**：用一个 LLM 扮演真实用户提问。不是固定脚本，而是按用户画像（急躁/啰嗦/模糊）生成多轮对话。这让测试覆盖"用户说不清话"的真实场景。
- **被测 Agent**：你的智能体，正常处理用户模拟器的输入。
- **判定器**：另一个 LLM，在对话结束后判定智能体是否合规。判定不只看"任务完成了吗"，更看"过程中有没有违反 policy"。

τ-bench 的两个关键贡献：

1. **策略遵守率作为独立指标**：传统评估只看任务完成，τ-bench 把"是否违反 policy"独立出来。智能体可能完成了任务但违规（如绕过身份验证就退了款），这种"成功"在生产里是事故。
2. **数据库状态校验**：除了对话正确，还要校验智能体是否正确修改了系统状态。例如用户要求改地址，对话看起来对了，但数据库里地址到底改没改？τ-bench 直接查数据库验证。

#### 设计指南 / Design Guidelines

1. **policy 必须有可机器判定的条款**：每个 policy 条款配一个判定函数。模糊条款（"要礼貌"）不能机器判定，必须重写成可判定的（"回复必须以敬语开头"→正则可判）。
2. **用户模拟器要有多样画像**：单一画像测不出鲁棒性。至少 3–5 种画像（新手/专家/急躁/模糊/对抗）。
3. **判定器与被测不同模型族**：同 Pattern 1，避免同源偏差。
4. **状态校验要查 ground truth 数据库**：不能只信对话里的"已修改"措辞，必须查实际数据库状态。
5. **多轮对话测试要固定随机种子**：用户模拟器是 LLM 生成，不固定种子则每次跑结果不同，无法回归。

#### 集成模式 / Integration Patterns

```python
def tau_bench_run(agent, user_simulator, judge, policy, db, seed=42):
    conversation = []
    state = db.snapshot()
    # Phase 1: user simulator drives multi-turn dialog
    for turn in user_simulator.run(profile="impatient", seed=seed):
        reply = agent.run(turn, conversation)
        conversation.append((turn, reply))
        if user_simulator.says_done():
            break
    # Phase 2: judge evaluates policy compliance + task completion
    policy_score = judge.check_policy(conversation, policy)  # per-clause judgement functions
    task_score = judge.check_task_completion(conversation, expected_outcome)
    # Phase 3: database state verification
    state_ok = db.verify_expected_changes(state, expected_db_changes)
    return {"policy_compliance": policy_score,
            "task_completion": task_score,
            "db_state_correct": state_ok}
```

集成到 AGENTS.md §12 评估框架与 §8 安全护栏：τ-bench harness 作为"集成测试"层，与 Pattern 1 的"单元评估"互补——Pattern 1 测单 case，τ-bench 测多轮端到端。policy 条款纳入 §8 安全护栏的行为边界声明。

#### 来源引用 / Source Citation

- τ-bench：Yao et al. "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains" (Sierra, 2024)
- 项目页：`https://github.com/sierra-research/tau-bench`
- 用户模拟器思想：借鉴 Rasa 对话模拟 + LLM 生成

---

### Pattern 4: Cross-Platform Consistency Evaluation / 跨平台一致性评估

#### 核心概念 / Core Concept

同一份规则集（AGENTS.md + config.yaml）部署到 N 个平台（Dify / Coze / OpenAI / LangChain / Coze 国内版……），行为会一致吗？现实是：几乎不会完全一致。各平台的提示词拼接顺序、工具调用解析、记忆管理实现都有差异。

Chatbot Arena 的 pairwise comparison + Elo 排名提供了一种量化方法：同一份考题在 N 个平台跑，两两比较（pairwise）哪个回答更好，再用 Elo 积分排名。Elo 分数差能量化"平台适配一致性"——差值越小越一致。

关键认知：**一致性不等于相同**。各平台可以有可接受的差异范围（如措辞不同但事实一致），超出范围才算不一致。

#### 设计指南 / Design Guidelines

1. **构造的智能体应标注"平台一致性期望"**：明确定义各平台可接受的差异范围。例如"事实陈述必须 100% 一致；措辞和顺序允许差异；格式允许平台原生差异"。
2. **pairwise 比较用盲评**：judge 不知道回答来自哪个平台，避免平台偏见。
3. **Elo 排名定期更新**：每次平台升级后重跑，跟踪一致性趋势。某平台 Elo 突然下降说明该平台升级引入了不一致。
4. **差异要归因**：不只是打分，要标注差异类型（事实差异/措辞差异/格式差异/能力缺失）。事实差异是 P0 问题，措辞差异可接受。

#### 集成模式 / Integration Patterns

```yaml
# 平台一致性期望 / platform consistency expectation
platform_consistency:
  required_identical:   # 必须 100% 一致
    - factual_statements   # 事实陈述（数字、时限、政策）
    - tool_call_sequence   # 工具调用序列
  acceptable_variance:  # 允许差异
    - wording_and_phrasing  # 措辞
    - response_order        # 回答点顺序
    - formatting            # 格式（用平台原生 markdown）
  forbidden:            # 任何平台都不允许
    - fabrication           # 造假
    - policy_violation      # 违规
```

集成到 AGENTS.md §13 部署与适配：跨平台一致性评估作为部署后验证环节，与"适配优先级：护栏 > 行为正确性 > 人格一致性 > 效率 > 原生 UX"呼应——一致性评估量化了各平台的适配质量。

#### 来源引用 / Source Citation

- Chatbot Arena：`https://chat.lmsys.org/`，LMSYS，pairwise + Elo 排名方法
- Chatbot Arena 论文：Chiang et al. "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference" (2024)
- Elo 评分系统：Elo "The Rating of Chess Players" (1978)

---
