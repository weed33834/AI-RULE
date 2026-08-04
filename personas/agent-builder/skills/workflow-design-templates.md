---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 用户要落地工作流编排代码（LangGraph StateGraph/并行、CrewAI、重试封装、幂等执行器）
terminates_when: T    # 所需模板示例已选定并改用、reducer/检查点等"需验证"项已对照官方文档确认
provides: π           # LangGraph StateGraph（条件分支+循环+人工审批）示例、LangGraph 并行 Fan-out/Fan-in 示例、CrewAI 顺序流程示例、指数退避重试装饰器、幂等执行器代码模板
interface: R          # 输入=工作流模式选择（来自 workflow-design.md 决策树）；输出=可直接改用的 Python 代码模板与"需验证"提示
---

# 工作流设计模板示例 (Workflow Design Templates)

> 本文件是 `workflow-design.md` 的子文件，专门覆盖原 §5 模板示例的可落地代码模板。方法论、决策树、常见陷阱与检查清单请见主文件 [workflow-design.md](./workflow-design.md)。

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

> **真实性说明：** 以上代码均为**概念示意**，展示真实框架（LangGraph、CrewAI）的 API 调用形态与设计模式，但具体方法签名、参数名、reducer/checkpointer 配置方式需对照目标框架当前版本文档校准（已标注"需验证"处尤其如此）。完整的真实性要求与框架出处见主文件 [workflow-design.md](./workflow-design.md) 的"真实性要求"章节。
