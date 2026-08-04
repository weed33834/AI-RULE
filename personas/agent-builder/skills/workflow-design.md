# workflow-design.md — 复杂工作流编排模式 / Complex Workflow Orchestration Patterns

---

## 1. 一句话描述 / One-sentence Description

**中文：** 以"节点 + 边 + 共享状态"为核心抽象，提供顺序、并行、条件分支、循环、人工审批、超时处理等可组合的工作流模式库，并配以状态管理、错误重试与幂等性设计，使智能体流程可控制、可恢复、可演进。

**English:** Centered on the abstraction of "nodes + edges + shared state," this guide provides a composable workflow pattern library (sequential, parallel, conditional branch, loop, human approval, timeout) with state management, error retry, and idempotency design, making agent flows controllable, recoverable, and evolvable.

---

## 2. 适用场景 / Applicable Scenarios

| 场景 / Scenario | 说明 / Description |
|---|---|
| 多步决策流程 / Multi-step decision flow | 需要精确控制"先做什么、再做什么、何时分支"的复杂智能体 |
| 人机协作 / Human-in-the-loop | 关键步骤需人工审批后才继续（如退款、发送邮件） |
| 可恢复长流程 / Resumable long flows | 流程可能中断（超时/异常），需要断点续跑 |
| 多智能体协作 / Multi-agent collaboration | 多个角色智能体按流程分工协作 |
| 批量并行处理 / Batch parallel processing | 对多个独立子任务并行执行后汇总 |

**不适用 / Not applicable：** 单轮问答、无分支的简单线性调用——直接用一次模型调用即可，引入工作流引擎属过度设计。

---

## 3. 核心方法论 / Core Methodology

### 3.1 核心抽象：节点 + 边 + 共享状态

```
共享状态 (Shared State)
    │  （贯穿所有节点的可读写数据结构）
    │
    ▼
节点 A ──边──► 节点 B ──条件边──► 节点 C / 节点 D
 (读/写状态)    (读/写状态)        (读/写状态)
```

- **节点 / Node：** 一个执行单元（LLM 调用、工具调用、纯逻辑、子图）。接收状态、返回状态更新。
- **边 / Edge：** 节点间的转移规则。普通边（固定下一步）、条件边（按状态动态路由）。
- **共享状态 / State：** 贯穿全流程的 TypedDict/dataclass，各节点读写其中字段。

### 3.2 工作流模式库 / Workflow Pattern Library

#### 模式 1：顺序 / Sequential

```
[A] ──► [B] ──► [C] ──► [END]
```
节点依次执行，前者输出作为后者输入。最基础的模式。

#### 模式 2：并行 / Parallel (Fan-out / Fan-in)

```
        ┌──► [B1] ──┐
[A] ────┤            ├──► [汇总] ──► [END]
        └──► [B2] ──┘
```
A 后并行执行 B1、B2，全部完成后汇总。适合独立子任务加速。

#### 模式 3：条件分支 / Conditional Branch

```
              ┌── 条件1 ──► [B]
[A] ──判断──┤
              └── 条件2 ──► [C]
```
根据状态中的字段值，动态路由到不同节点。

#### 模式 4：循环 / Loop

```
[A] ──► [B: 检查] ──不满足──► [C: 修正] ──► 回到 [B]
              │
            满足 ──► [END]
```
反复执行直到条件满足（如自校正、迭代优化）。需设最大循环次数防死循环。

#### 模式 5：人工审批节点 / Human Approval (Human-in-the-loop)

```
[A] ──► [暂停·等待人工] ──批准──► [B]
                  │
                拒绝 ──► [END: 已拒绝]
```
流程在审批节点中断，等待人工输入后继续。需配合持久化检查点。

#### 模式 6：超时处理 / Timeout Handling

```
[A] ──► [B (带超时)]
         ├─ 在超时内完成 ──► [C]
         └─ 超时 ──► [降级/重试/跳过]
```
为节点设超时上限，超时后走降级路径而非无限等待。

### 3.3 状态管理 / State Management

- **状态结构：** 用 TypedDict 明确定义字段，便于类型检查与文档化。
- **状态更新方式：** 节点返回部分更新（仅变更字段），由框架合并；或用 reducer 处理列表/累加字段。
- **持久化检查点 / Checkpointing：** 每个节点执行后保存状态快照，支持中断恢复与回放。LangGraph 原生支持 checkpointer。
- **状态隔离：** 并行分支应避免写同一字段造成竞态；用不同字段或事后合并。

### 3.4 错误处理与重试策略 / Error Handling & Retry

| 策略 / Strategy | 说明 / Description |
|---|---|
| **重试 / Retry** | 对瞬时错误（网络抖动、限流）自动重试；指数退避（backoff）避免雪崩 |
| **最大重试次数** | 设上限（如 3 次），超过则进入降级路径 |
| **降级 / Fallback** | 重试耗尽后走备选方案（如换模型、返回缓存的默认回复、转人工） |
| **超时 / Timeout** | 单节点设超时，超时视为失败触发重试或降级 |
| **错误隔离** | 并行分支中某分支失败不应拖垮整体；记录失败分支，其余继续 |
| **死信 / Dead Letter** | 多次失败的任务写入死信队列，人工后续处理 |

### 3.5 幂等性设计 / Idempotency Design

> **幂等性：** 同一请求重复执行多次，结果与执行一次相同。对可恢复的工作流至关重要——重试或恢复时不会产生副作用重复。

| 设计要点 / Principle | 做法 / Approach |
|---|---|
| **幂等键 / Idempotency Key** | 每个请求/任务带唯一 ID，下游据 ID 去重 |
| **工具幂等** | 工具实现支持"已执行则直接返回上次结果"；写操作用 upsert 而非 insert |
| **状态机防重复** | 流程状态机记录"已完成节点"，恢复时跳过已完成节点 |
| **副作用外置** | 将有副作用的操作（发邮件、扣款）集中到流程末端，执行前先查是否已执行 |

---

## 4. 决策树 / 流程图 — Decision Tree

```
工作流设计需求 / Workflow design needed
   │
   ▼
Q1: 流程是线性的还是有分支/循环？
   ├─ 纯线性（A→B→C）──► 顺序模式，无需状态机框架
   └─ 有分支/循环/并行 ──► Q2
   │
   ▼
Q2: 是否需要精确控制每一步（状态机式）？
   ├─ 是 ──► LangGraph StateGraph（节点+边+共享状态，支持循环/条件/人机协作/检查点）
   └─ 否（偏好"角色分工团队"隐喻）──► CrewAI（Agent+Task+Crew，sequential/hierarchical）
   │
   ▼
Q3: 是否有人工审批节点？
   ├─ 是 ──► 用 interrupt/暂停机制 + 持久化检查点（中断恢复）
   └─ 否 ──► 全自动执行
   │
   ▼
Q4: 是否有可失败/可超时的外部依赖？
   ├─ 是 ──► 配置 重试(指数退避) + 最大次数 + 超时 + 降级路径
   └─ 否 ──► 标准执行
   │
   ▼
Q5: 流程可能中断需恢复？
   ├─ 是 ──► 启用检查点持久化 + 幂等设计（防重复副作用）
   └─ 否 ──► 无状态执行
   │
   ▼
Q6: 是否有并行子任务？
   ├─ 是 ──► Fan-out/Fan-in；注意状态字段隔离防竞态
   └─ 否 ──► 顺序执行
```

---

## 5. 模板示例 — Template Example

### 5.1 LangGraph StateGraph 示例（条件分支 + 循环 + 人工审批）

```python
# langgraph_workflow.py — 概念示意，API 以 LangGraph 官方文档为准
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# 1. 定义共享状态
class AgentState(TypedDict):
    query: str
    retrieved_docs: list
    answer: str
    quality_ok: bool
    retry_count: int

# 2. 定义节点函数（每个接收 state，返回部分更新）
def retrieve_node(state: AgentState) -> dict:
    docs = search_knowledge_base(state["query"])   # 你的检索逻辑
    return {"retrieved_docs": docs}

def generate_node(state: AgentState) -> dict:
    answer = call_llm(state["query"], state["retrieved_docs"])
    return {"answer": answer}

def review_node(state: AgentState) -> dict:
    """人工审批节点：检查答案质量。"""
    # 实际中用 interrupt() 暂停等待人工输入，此处简化为自动判断
    approved = human_review(state["answer"])        # 你的审批逻辑
    return {"quality_ok": approved}

def fix_node(state: AgentState) -> dict:
    """质量不达标时修正答案（循环体）。"""
    answer = call_llm(f"改进以下回答：{state['answer']}")
    return {"answer": answer, "retry_count": state.get("retry_count", 0) + 1}

# 3. 条件路由函数
def should_fix_or_end(state: AgentState) -> Literal["fix", "__end__"]:
    if state.get("quality_ok"):
        return END
    if state.get("retry_count", 0) >= 3:            # 防死循环：最多重试 3 次
        return END
    return "fix"

# 4. 构建图
graph = StateGraph(AgentState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)
graph.add_node("review", review_node)
graph.add_node("fix", fix_node)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", "review")
graph.add_conditional_edges("review", should_fix_or_end)  # review → fix 或 END
graph.add_edge("fix", "review")                            # fix → review（循环）

# 5. 编译（可加 checkpointer 实现持久化与中断恢复）
app = graph.compile()
# app = graph.compile(checkpointer=MemorySaver())  # 需验证 checkpointer 用法

# 6. 执行
result = app.invoke({"query": "退款政策是什么？"})
```

### 5.2 LangGraph 并行（Fan-out / Fan-in）示例

```python
# langgraph_parallel.py — 概念示意
from typing import TypedDict
from langgraph.graph import StateGraph, END

class ResearchState(TypedDict):
    topic: str
    subtopics: list
    results: list          # reducer 累加各分支结果

def split_node(state: ResearchState) -> dict:
    """将主题拆为子主题（Fan-out 前置）。"""
    subs = split_into_subtopics(state["topic"])
    return {"subtopics": subs}

def research_subtopic_factory(sub: str):
    """为每个子主题生成一个研究节点。"""
    def node(state: ResearchState) -> dict:
        res = research(sub)                       # 你的研究逻辑
        return {"results": [res]}                 # 返回列表，由 reducer 合并
    return node

def merge_node(state: ResearchState) -> dict:
    """汇总所有子主题结果（Fan-in）。"""
    summary = synthesize(state["results"])
    return {"results": [summary]}

graph = StateGraph(ResearchState)
graph.add_node("split", split_node)
graph.add_node("merge", merge_node)

# 为每个子主题动态加节点（实际并行度由框架调度）
for i, sub in enumerate(["背景", "现状", "趋势"]):
    graph.add_node(f"research_{i}", research_subtopic_factory(sub))
    graph.add_edge("split", f"research_{i}")
    graph.add_edge(f"research_{i}", "merge")

graph.set_entry_point("split")
graph.add_edge("merge", END)
app = graph.compile()
```

> **需验证：** LangGraph 中列表字段的状态合并需配置 reducer（如 `Annotated[list, operator.add]`），并行分支写同一字段时尤其重要。具体写法以 LangGraph 官方文档为准。

### 5.3 CrewAI 流程示例（角色分工 + 顺序流程）

```python
# crewai_workflow.py — 概念示意，API 以 CrewAI 官方文档为准
from crewai import Agent, Task, Crew

# 1. 定义角色智能体
researcher = Agent(
    role="市场研究员",
    goal="收集并整理指定主题的市场信息",
    backstory="资深市场分析师，擅长快速调研与信息整合。",
    tools=[web_search_tool],           # 你的工具
)

writer = Agent(
    role="内容撰稿人",
    goal="基于研究结果撰写高质量报告",
    backstory="专业技术撰稿人，擅长将复杂信息转化为清晰文字。",
)

editor = Agent(
    role="编辑审校",
    goal="审核并优化报告质量",
    backstory="严谨的内容编辑，确保准确性与可读性。",
)

# 2. 定义任务（绑定到智能体）
research_task = Task(
    description="调研 {topic} 的市场规模、主要玩家与趋势，输出要点列表。",
    agent=researcher,
    expected_output="结构化的市场调研要点列表",
)

writing_task = Task(
    description="基于调研结果撰写一份 800 字的市场分析报告。",
    agent=writer,
    expected_output="800 字市场分析报告草稿",
)

editing_task = Task(
    description="审校报告，修正事实错误与表达问题，输出终稿。",
    agent=editor,
    expected_output="审校后的报告终稿",
)

# 3. 组建 Crew（顺序流程）
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process="sequential",              # sequential | hierarchical
)

# 4. 执行
result = crew.kickoff(inputs={"topic": "AI 智能体市场"})
print(result)
```

### 5.4 错误处理与重试封装（通用模式）

```python
# retry_utils.py — 概念示意，通用重试与降级封装
import time
from functools import wraps

def with_retry(max_retries=3, backoff_base=1.0, fallback=None):
    """指数退避重试装饰器。"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait = backoff_base * (2 ** attempt)   # 1s, 2s, 4s...
                        time.sleep(wait)
            # 重试耗尽
            if fallback is not None:
                return fallback(*args, **kwargs)
            raise last_error
        return wrapper
    return decorator

# 使用示例：工具调用带重试 + 降级
@with_retry(max_retries=3, backoff_base=1.0, fallback=lambda **kw: {"status": "degraded"})
def call_order_api(order_id):
    return external_order_service.get(order_id)
```

### 5.5 幂等性设计示例

```python
# idempotency.py — 概念示意
import hashlib

class IdempotentExecutor:
    """基于幂等键去重，避免重试导致副作用重复。"""

    def __init__(self, store):
        self.store = store              # 持久化存储（如 Redis/DB）

    def execute(self, idempotency_key: str, fn, *args, **kwargs):
        # 1. 查是否已执行
        cached = self.store.get(idempotency_key)
        if cached is not None:
            return cached               # 已执行，直接返回上次结果
        # 2. 首次执行
        result = fn(*args, **kwargs)
        # 3. 记录结果
        self.store.set(idempotency_key, result)
        return result

# 生成幂等键：业务标识 + 流程步骤
def make_key(trace_id: str, step: str) -> str:
    raw = f"{trace_id}:{step}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
```

---

## 6. 常见陷阱 / Common Pitfalls

1. **循环无终止条件导致死循环 / Infinite loop without exit condition**
   - 危害：智能体无限重试/自校正，烧尽 token 与时间。
   - 纠正：所有循环必须设最大次数或质量阈值作为退出条件。

2. **并行分支写同一状态字段造成竞态 / Race condition on shared state**
   - 危害：并行分支并发写同一字段，结果不确定。
   - 纠正：分支写不同字段；或用 reducer 显式定义合并规则。

3. **无检查点导致中断不可恢复 / No checkpointing = no recovery**
   - 危害：流程在长任务中途超时/崩溃，必须从头重跑。
   - 纠正：启用持久化检查点，记录每步状态，支持断点续跑。

4. **重试无退避导致雪崩 / Retry storms without backoff**
   - 危害：瞬时故障时所有请求同时重试，压垮下游。
   - 纠正：指数退避 + 抖动（jitter）+ 最大重试次数。

5. **重试导致副作用重复 / Retried side effects execute twice**
   - 危害：重试时邮件发两次、扣款扣两次。
   - 纠正：对有副作用的操作做幂等设计（幂等键去重）；副作用集中到流程末端。

6. **人工审批节点无超时 / Human approval without timeout**
   - 危害：审批人长时间不响应，流程永久挂起。
   - 纠正：审批节点设超时，超时后走默认路径（拒绝/转交/升级）。

7. **状态结构无类型约束 / Untyped state**
   - 危害：字段名拼错、类型混乱，运行时才发现。
   - 纠正：用 TypedDict/dataclass 明确定义状态结构，启用类型检查。

---

## 7. 检查清单 / Checklist

- [ ] 已识别所需工作流模式（顺序/并行/分支/循环/审批/超时）/ patterns identified
- [ ] 共享状态用 TypedDict/dataclass 明确定义，启用类型检查 / state typed & checked
- [ ] 所有循环设有最大次数/质量阈值退出条件 / loops have exit conditions
- [ ] 并行分支写不同字段或配置了 reducer 合并规则 / parallel branches avoid races
- [ ] 关键节点（人工审批）有超时与默认路径 / approval nodes have timeout & fallback
- [ ] 外部依赖配置了重试（指数退避）+ 最大次数 + 降级路径 / retry+fallback configured
- [ ] 长流程启用了持久化检查点，可断点续跑 / checkpointing enabled for recovery
- [ ] 有副作用的操作做了幂等设计（幂等键去重）/ side effects are idempotent
- [ ] 已选定编排工具（LangGraph 精确控制 / CrewAI 角色分工）/ orchestration tool selected
- [ ] 工作流已用测试用例验证各分支路径 / branches tested
- [ ] 错误/超时/降级路径已测试 / error & fallback paths tested

---

## 真实性要求 / Authenticity Requirements

- LangGraph 是 LangChain 团队开源的真实项目（github.com/langchain-ai/langgraph，MIT 许可），以"节点 + 边 + 共享状态"建模，原生支持循环、条件分支、人机协作（interrupt）、持久化检查点（checkpointer）。文中 `StateGraph`、`add_node`、`add_edge`、`add_conditional_edges`、`set_entry_point`、`compile` 均为 LangGraph 真实 API 概念。
- CrewAI 是真实开源项目（github.com/crewAIInc/crewAI），核心概念 Agent（role/goal/backstory）、Task（description/agent/expected_output）、Crew（agents/tasks/process）均为其真实抽象，支持 sequential 与 hierarchical 两种流程。
- 工作流模式（顺序/并行/分支/循环/人机协作/超时）均为工作流编排领域的通用经典模式，源自工作流与状态机理论。幂等性、指数退避重试、检查点恢复均为分布式系统的真实通用工程实践。
- 代码示例为**概念示意**，展示了真实框架的 API 调用形态与设计模式，但具体方法签名、参数名、reducer/checkpointer 配置方式需对照目标框架当前版本文档校准（已标注"需验证"处尤其如此）。运行前需安装对应包（`pip install langgraph crewai`）并配置好环境。
- 任何标注"需验证"的信息，使用前必须通过官方文档二次确认，不得直接用于生产决策。
