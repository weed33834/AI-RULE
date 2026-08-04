---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 用户要实现多智能体协作，需参考具体框架的配置/代码模板
terminates_when: T    # 模板已参考并适配到具体用例，配置/代码已落地
provides: π           # 多智能体配置 YAML 模板、CrewAI 顺序/层级实现示例、LangGraph 层级实现示例
interface: R          # 输入=选定的协作模式 + 框架；输出=可直接参考/改写的配置与代码模板
---

# 多智能体协作模板示例 (Multi-Agent Collaboration Templates)

---

### 多智能体配置模板 / Multi-Agent Configuration Template

```yaml
# multi_agent_config.yaml — 多智能体协作配置模板

collaboration:
  mode: "hierarchical"            # sequential | parallel | hierarchical
  framework: "crewai"             # crewai | langgraph | autogen

  # 智能体定义 / Agent definitions
  agents:
    - id: "orchestrator"
      role: "编排者"
      goal: "分解任务、分配子任务、审查结果、合并输出"
      backstory: "你是一个经验丰富的项目经理，擅长任务分解和团队协调。"
      model: "gpt-4o"
      tools: ["task_decomposer", "result_merger"]
      max_iterations: 10
      is_manager: true            # CrewAI hierarchical 模式中的 manager

    - id: "researcher"
      role: "研究员"
      goal: "收集和分析相关信息"
      backstory: "你是一个严谨的研究员，擅长信息检索和分析。"
      model: "gpt-4o-mini"
      tools: ["web_search", "knowledge_retriever"]
      allow_delegation: false

    - id: "writer"
      role: "撰稿人"
      goal: "根据研究结果撰写清晰、结构化的内容"
      backstory: "你是一个专业撰稿人，擅长将复杂信息转化为易读文本。"
      model: "gpt-4o"
      tools: []
      allow_delegation: false

    - id: "reviewer"
      role: "审校员"
      goal: "检查内容的准确性、完整性和一致性"
      backstory: "你是一个严格的审校员，不放过任何事实错误和逻辑漏洞。"
      model: "gpt-4o"
      tools: ["fact_checker"]
      allow_delegation: false

  # 通信协议 / Communication protocol
  communication:
    message_format: "json"
    message_types:
      - "task_assignment"
      - "task_result"
      - "question"
      - "answer"
      - "handoff"
      - "conflict_report"
      - "status_update"
    max_message_tokens: 2000      # 单条消息最大 token 数

  # 冲突解决 / Conflict resolution
  conflict_resolution:
    enabled: true
    detection: "auto"             # auto | manual
    strategies:
      fact_conflict: "third_party_verify"
      plan_conflict: "orchestrator_decide"
      quality_conflict: "highest_score"
    log_conflicts: true

  # 上下文隔离 / Context isolation
  context_isolation:
    principle: "minimal_visibility"
    shared_state_fields:          # LangGraph State 中共享的字段
      - "task_id"
      - "current_results"
      - "status"
    private_state_fields:         # 各智能体私有字段
      - "internal_reasoning"
      - "working_notes"
    information_downgrade: "summary"  # none | summary | extract

  # 错误处理 / Error handling
  error_handling:
    timeout_seconds: 120          # 单个智能体执行超时
    max_retries: 3                # 最大重试次数
    on_failure: "reassign"        # reassign | skip | abort
```

### CrewAI 实现示例 / CrewAI Implementation Example

```python
# CrewAI 顺序执行示例（基于 CrewAI 官方文档的概念）

from crewai import Agent, Task, Crew, Process

# 定义智能体 / Define agents
researcher = Agent(
    role="研究员",
    goal="收集和分析相关信息",
    backstory="你是一个严谨的研究员，擅长信息检索和分析。",
    verbose=True
)

writer = Agent(
    role="撰稿人",
    goal="根据研究结果撰写清晰、结构化的内容",
    backstory="你是一个专业撰稿人，擅长将复杂信息转化为易读文本。",
    verbose=True
)

# 定义任务 / Define tasks（顺序执行：研究 → 写作）
research_task = Task(
    description="研究 {topic} 的最新趋势和关键发现",
    expected_output="一份包含关键发现的研究报告",
    agent=researcher
)

writing_task = Task(
    description="基于研究结果撰写一篇结构清晰的分析文章",
    expected_output="一篇 1000 字左右的分析文章",
    agent=writer
)

# 组建 Crew（顺序模式）/ Assemble crew (sequential mode)
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,   # 顺序执行
    verbose=True
)

# 执行 / Execute
result = crew.kickoff(inputs={"topic": "AI Agent 发展趋势"})
```

```python
# CrewAI 层级执行示例 / CrewAI hierarchical mode example

from crewai import Agent, Task, Crew, Process

manager = Agent(
    role="项目经理",
    goal="协调团队完成任务，确保质量和效率",
    backstory="你是一个经验丰富的项目经理。",
    allow_delegation=True
)

researcher = Agent(
    role="研究员",
    goal="收集和分析相关信息",
    backstory="你是一个严谨的研究员。",
    allow_delegation=True          # 启用后自动获得 Delegate Work 和 Ask Question 工具
)

writer = Agent(
    role="撰稿人",
    goal="撰写高质量内容",
    backstory="你是一个专业撰稿人。",
    allow_delegation=False
)

# 任务可以不指定 agent，由 manager 动态分配
research_task = Task(
    description="研究 {topic} 的最新趋势",
    expected_output="研究报告",
    agent=researcher               # 也可不指定，由 manager 分配
)

writing_task = Task(
    description="撰写分析文章",
    expected_output="分析文章",
    agent=writer
)

# 组建 Crew（层级模式）/ Assemble crew (hierarchical mode)
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.hierarchical,  # 层级执行
    manager_llm=None,              # 需指定 manager 使用的 LLM（None 时使用默认）
    verbose=True
)

result = crew.kickoff(inputs={"topic": "AI Agent 发展趋势"})
```

### LangGraph 实现示例 / LangGraph Implementation Example

```python
# LangGraph 层级执行示例（基于 LangGraph 官方文档的概念）

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

# 定义共享状态 / Define shared state
class AgentState(TypedDict):
    task: str
    research_result: str
    writing_result: str
    review_passed: bool
    messages: Annotated[list, operator.add]

# 定义节点函数 / Define node functions
def orchestrator(state: AgentState) -> AgentState:
    """编排者：分解任务，决定路由"""
    # 根据当前状态决定下一步
    return {"messages": ["orchestrator: 分配任务"]}

def researcher_node(state: AgentState) -> AgentState:
    """研究节点"""
    result = f"关于 {state['task']} 的研究发现..."
    return {"research_result": result, "messages": ["researcher: 完成研究"]}

def writer_node(state: AgentState) -> AgentState:
    """写作节点"""
    result = f"基于 {state['research_result']} 撰写的文章..."
    return {"writing_result": result, "messages": ["writer: 完成写作"]}

def reviewer_node(state: AgentState) -> AgentState:
    """审校节点"""
    passed = True  # 审校逻辑
    return {"review_passed": passed, "messages": ["reviewer: 审校完成"]}

def route_after_review(state: AgentState) -> str:
    """条件路由：审校通过则结束，否则回到写作"""
    if state.get("review_passed", False):
        return "end"
    return "rewrite"

# 构建图 / Build graph
workflow = StateGraph(AgentState)

# 添加节点 / Add nodes
workflow.add_node("orchestrator", orchestrator)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_node("reviewer", reviewer_node)

# 添加边 / Add edges
workflow.set_entry_point("orchestrator")
workflow.add_edge("orchestrator", "researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "reviewer")

# 添加条件边 / Add conditional edges
workflow.add_conditional_edges(
    "reviewer",                    # 源节点
    route_after_review,            # 路由函数
    {
        "end": END,                # 审校通过 → 结束
        "rewrite": "writer"        # 审校未通过 → 重新写作（循环）
    }
)

# 编译并执行 / Compile and run
app = workflow.compile()
result = app.invoke({"task": "AI Agent 发展趋势"})
```
