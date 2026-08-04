# Multi-Agent Collaboration Patterns / 多智能体协作模式

---

## 一句话描述 / One-Sentence Description

**中文：** 多智能体协作模式是多个 LLM 智能体通过结构化通信协议协同完成复杂任务的架构范式，涵盖顺序执行、并行执行和层级执行三种核心模式，辅以冲突解决和上下文隔离机制保障协作质量。

**English:** Multi-agent collaboration patterns are architectural paradigms in which multiple LLM agents work together to accomplish complex tasks through structured communication protocols, encompassing three core modes — sequential, parallel, and hierarchical execution — supplemented by conflict resolution and context isolation mechanisms to ensure collaboration quality.

---

## 适用场景 / Applicable Scenarios

| 场景 / Scenario | 推荐模式 / Recommended Pattern | 说明 / Description |
|---|---|---|
| 研究 → 写作 → 审校流水线 / Research-Write-Review pipeline | 顺序执行 / Sequential | 每步依赖前一步输出 |
| 多维度独立分析 / Multi-dimensional independent analysis | 并行执行 / Parallel | 多个智能体同时分析不同维度，最后汇总 |
| 复杂任务分解与委派 / Complex task decomposition | 层级执行 / Hierarchical | 编排者分解任务，执行者各自完成 |
| 代码开发与代码审查 / Code development and review | 顺序 + 并行混合 | 开发者写代码，多个审查者并行检查不同方面 |
| 辩论式决策 / Debate-based decision making | 并行执行 / Parallel | 多个智能体提出不同方案，投票或综合得出结论 |

---

## 核心方法论 / Core Methodology

### 1. 三种协作模式 / Three Collaboration Patterns

#### 1.1 顺序执行（Sequential / Pipeline）

```
Agent A → Agent B → Agent C → 最终输出
 (研究)    (写作)    (审校)
```

- **定义：** 智能体按固定顺序依次执行，前一个的输出作为后一个的输入。
- **适用条件：** 任务有明确的阶段划分，每阶段依赖前一阶段的结果。
- **优点：** 流程清晰、易于调试、结果可预测。
- **缺点：** 总耗时为各阶段耗时之和，无法并行加速；单点故障会导致整条流水线中断。
- **框架支持：**
  - **CrewAI：** `Process` 设置为 `sequential`（默认模式），任务按 `tasks` 列表顺序执行，前一个任务的输出自动作为下一个任务的上下文。
  - **LangGraph：** 通过 `add_edge` 连接节点，形成线性执行图。

#### 1.2 并行执行（Parallel / Fan-out and Fan-in）

```
         ┌→ Agent A (分析维度 1) ─┐
输入 ────┤→ Agent B (分析维度 2) ─┤──→ 汇总 Agent → 最终输出
         └→ Agent C (分析维度 3) ─┘
```

- **定义：** 多个智能体同时执行各自独立的子任务，最后由汇总智能体合并结果。
- **适用条件：** 子任务之间相互独立，无需等待彼此结果。
- **优点：** 总耗时约等于最慢子任务的耗时；可扩展性强。
- **缺点：** 结果合并可能有冲突；需要设计合并/裁决策略；资源消耗高（同时调用多个 LLM）。
- **框架支持：**
  - **LangGraph：** 使用 `Send` API 实现并行节点分发，通过条件边汇聚到汇总节点。多个节点可以并行执行，状态在共享的 `State` 中传递。
  - **AutoGen：** 使用 `GroupChat` + `GroupChatManager`，管理器可以调度多个智能体并行响应（需验证并行调度细节）。

#### 1.3 层级执行（Hierarchical / Orchestrator-Worker）

```
              编排者 Agent (Orchestrator)
              ┌─────────┼─────────┐
              ↓         ↓         ↓
          执行者 A   执行者 B   执行者 C
          (子任务1)  (子任务2)  (子任务3)
              └─────────┼─────────┘
                        ↓
              编排者 Agent (审查 + 合并)
                        ↓
                   最终输出
```

- **定义：** 一个编排者智能体负责任务分解、委派和结果审查；多个执行者智能体各自完成被分配的子任务。
- **适用条件：** 任务复杂度高，需要动态分解和灵活委派。
- **优点：** 灵活性高，编排者可根据任务动态调整分配策略；有审查环节保障质量。
- **缺点：** 编排者是单点和性能瓶颈；编排者自身的 LLM 调用消耗额外 token；调试复杂。
- **框架支持：**
  - **CrewAI：** `Process` 设置为 `hierarchical`，需指定 `manager_llm` 或 `manager_agent`。编排者（manager）负责任务分配和审查。`allow_delegation=True` 时，智能体自动获得"Delegate Work"和"Ask Question"工具。
  - **LangGraph：** 通过条件边实现编排者节点根据状态动态路由到不同执行者节点，支持循环（编排 → 执行 → 审查 → 再分配）。
  - **AutoGen：** `GroupChatManager` 充当编排者角色，根据会话上下文选择下一个发言的智能体。

### 2. 通信协议（Communication Protocol / JSON Structured）

智能体间通信应使用结构化 JSON 消息，确保可解析、可追溯：

```json
{
  "message_id": "msg_001",
  "from_agent": "researcher",
  "to_agent": "writer",
  "message_type": "task_result",
  "timestamp": "2025-06-15T14:30:00Z",
  "content": {
    "task_id": "task_research_01",
    "status": "completed",
    "result": "研究发现用户反馈主要集中在三个方面...",
    "confidence": 0.85,
    "sources": ["doc_001", "doc_005", "doc_012"]
  },
  "metadata": {
    "turn": 3,
    "session_id": "session_abc123"
  }
}
```

**消息类型定义：**

| 类型 / Type | 说明 / Description |
|---|---|
| `task_assignment` | 编排者向执行者分配子任务 |
| `task_result` | 执行者返回子任务结果 |
| `question` | 智能体向另一个智能体提问 |
| `answer` | 回复另一个智能体的提问 |
| `handoff` | 将任务移交给另一个智能体 |
| `conflict_report` | 报告结果冲突，请求裁决 |
| `status_update` | 汇报当前执行状态 |

### 3. 冲突解决机制（Conflict Resolution Mechanism）

当多个智能体的结果产生冲突时：

```
冲突解决流程:
1. 检测冲突：汇总智能体对比各执行者结果，识别矛盾点
2. 分类冲突:
   a. 事实冲突 — 对同一事实给出不同结论
   b. 方案冲突 — 提出不同的行动方案
   c. 质量冲突 — 对同一输出有不同质量评价
3. 裁决策略:
   a. 事实冲突 → 交由第三方验证智能体裁决，或回溯数据源
   b. 方案冲突 → 按预设优先级排序，或由编排者决策
   c. 质量冲突 → 取评分更高者，或合并双方意见
4. 记录日志：冲突内容、裁决过程、最终决策全部记录
5. 通知相关方：将裁决结果通知所有涉及的智能体
```

### 4. 上下文隔离原则（Context Isolation Principles）

```
原则 1：最小可见性 / Minimal Visibility
  - 每个智能体只能看到与其任务直接相关的上下文
  - 不应暴露其他智能体的完整内部推理过程
  - 仅传递任务结果和必要元数据

原则 2：状态边界 / State Boundary
  - 每个智能体维护独立的内部状态
  - 共享状态通过显式消息传递，不通过隐式全局变量
  - LangGraph 中通过 TypedDict State 定义共享状态的字段和类型

原则 3：信息降级 / Information Downgrading
  - 智能体 A 的详细输出传递给智能体 B 时，应进行摘要或结构化提取
  - 避免将完整的原始上下文（可能包含敏感信息）传递给不需要的智能体

原则 4：独立错误处理 / Independent Error Handling
  - 单个智能体失败不应导致整个系统崩溃
  - 设置超时机制和重试策略
  - 编排者应能感知执行者失败并重新分配任务
```

---

## Delegation Depth Limit (委托深度限制)

对应 AGENTS.md §11 新增规则。

- 多智能体委托链最大深度 3-5 跳。
- 超过限制时返回错误而非继续委托。
- 防止委托链失控消耗 API 配额和产生超时。
- 委托深度必须在智能体配置中声明。

## Idempotent Tool Calls (幂等工具调用)

对应 AGENTS.md §11 新增规则。

- 工具调用必须设计为幂等的——同一调用重复执行不产生副作用。
- 重试机制依赖幂等性保证。
- 非幂等操作必须设计去重机制（如唯一请求 ID）。

---

## 决策树 / Decision Tree

```
任务到达
    │
    ├─ 任务是否可分解为多个子任务？
    │   ├─ 否 → 单智能体处理，不需要多智能体协作
    │   └─ 是 → 继续
    │
    ├─ 子任务之间是否有依赖关系？
    │   ├─ 有依赖（A 的输出是 B 的输入）
    │   │   └─ 依赖是否为线性链式？
    │   │       ├─ 是 → 选择【顺序执行】模式
    │   │       └─ 否（存在分支/循环）→ 选择【层级执行】模式
    │   └─ 无依赖（子任务相互独立）
    │       └─ 选择【并行执行】模式
    │
    ├─ 选择模式后，设计通信协议
    │   ├─ 定义智能体角色和职责
    │   ├─ 定义消息格式（JSON 结构化）
    │   ├─ 定义消息类型和流转规则
    │   └─ 定义状态共享方式（LangGraph: State / AutoGen: GroupChat / CrewAI: Task output）
    │
    ├─ 是否需要冲突解决？
    │   ├─ 是（并行模式尤其需要）
    │   │   ├─ 定义冲突检测规则
    │   │   ├─ 定义裁决策略
    │   │   └─ 定义冲突日志格式
    │   └─ 否 → 跳过
    │
    ├─ 设计上下文隔离方案
    │   ├─ 确定每个智能体的可见上下文范围
    │   ├─ 定义状态边界和传递方式
    │   ├─ 设计信息降级策略（摘要/提取）
    │   └─ 设计错误处理和重试策略
    │
    └─ 选择框架并实现
        ├─ 简单顺序流水线 → CrewAI (sequential process)
        ├─ 复杂图结构/需要循环 → LangGraph (StateGraph)
        ├─ 对话式协作/群聊 → AutoGen (GroupChat)
        └─ 需要委派和审查 → CrewAI (hierarchical process) 或 LangGraph (条件边 + 循环)
```

---

## 模板示例 / Template Examples

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

---

## 常见陷阱 / Common Pitfalls

### 1. 上下文污染 / Context Pollution
- **问题：** 将一个智能体的完整内部推理传递给另一个智能体，导致后者的判断被前者偏见影响。
- **解决方案：** 遵循上下文隔离原则，仅传递结构化结果和必要元数据，不传递内部推理过程。

### 2. 无限循环 / Infinite Loops
- **问题：** 层级模式中，编排者不断将任务在执行者间来回分配，或审校者永远不满意执行者的结果，形成无限循环。
- **解决方案：** 设置 `max_iterations` 硬上限，超限时强制终止并返回当前最佳结果。

### 3. 通信开销过大 / Excessive Communication Overhead
- **问题：** 智能体间频繁通信，每次通信都消耗 LLM 调用，导致 token 成本和延迟激增。
- **解决方案：** 减少不必要的通信轮次，批量传递信息，设计高效的通信协议。

### 4. 编排者单点瓶颈 / Orchestrator Single Point of Bottleneck
- **问题：** 层级模式中所有任务都经过编排者分配和审查，编排者成为性能瓶颈。
- **解决方案：** 编排者使用更强的模型但减少调用次数；对简单任务采用直接路由而非全量经过编排者。

### 5. 框架选型不当 / Improper Framework Selection
- **问题：** 用 AutoGen 的 GroupChat 做不需要对话的流水线任务，或用 CrewAI 的 sequential 做需要复杂条件分支的任务。
- **解决方案：** 根据任务特征选择框架 — 线性流水线选 CrewAI sequential，复杂图结构选 LangGraph，对话式协作选 AutoGen GroupChat。

### 6. 忽略错误传播 / Ignoring Error Propagation
- **问题：** 前一个智能体的错误输出被后续智能体当作正确输入使用，错误逐级放大。
- **解决方案：** 每个智能体对输入进行校验，发现异常时报告而非继续处理；编排者审查中间结果。

---

## 检查清单 / Checklist

### 设计阶段 / Design Phase
- [ ] 已确定协作模式（顺序/并行/层级）并论证理由
- [ ] 已定义每个智能体的角色、目标和工具
- [ ] 已设计结构化通信协议（JSON 消息格式）
- [ ] 已定义消息类型和流转规则
- [ ] 已设计冲突解决机制（如适用）
- [ ] 已制定上下文隔离方案
- [ ] 已选择合适的框架（CrewAI/LangGraph/AutoGen）

### 实现阶段 / Implementation Phase
- [ ] 每个智能体的 system prompt 已明确定义角色边界
- [ ] 消息格式已统一为 JSON 结构化
- [ ] 共享状态字段已定义（LangGraph: TypedDict State）
- [ ] 内部推理与传递结果已分离
- [ ] 超时机制和重试策略已配置
- [ ] 最大迭代次数已设置（防止无限循环）

### 测试阶段 / Testing Phase
- [ ] 已测试正常流程的端到端执行
- [ ] 已测试单个智能体失败时的错误处理
- [ ] 已测试并行模式的结果合并
- [ ] 已测试层级模式的任务分配和审查
- [ ] 已测试冲突场景的裁决逻辑
- [ ] 已测试最大迭代次数的强制终止

### 运维阶段 / Operations Phase
- [ ] 智能体间通信有完整日志
- [ ] Token 消耗和 API 调用次数有监控
- [ ] 执行延迟有监控和告警
- [ ] 冲突日志有定期分析
- [ ] 框架版本更新有兼容性评估
