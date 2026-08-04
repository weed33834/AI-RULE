# deployment-guide.md — 跨平台部署指南 / Cross-Platform Deployment Guide

---

## 1. 一句话描述 / One-sentence Description

**中文：** 以一份与平台无关的通用 `config.yaml` 作为单一事实源，通过确定性的适配规则将其映射到 Dify、Coze、OpenAI、LangChain 及自定义框架等各平台的原生配置，实现"一次定义、多处部署"。

**English:** Use a single platform-agnostic `config.yaml` as the single source of truth, and map it to the native configurations of Dify, Coze, OpenAI, LangChain, and custom frameworks through deterministic adaptation rules, achieving "define once, deploy anywhere."

---

## 2. 适用场景 / Applicable Scenarios

| 场景 / Scenario | 说明 / Description |
|---|---|
| 多平台分发 / Multi-platform distribution | 同一个智能体需要同时上线 Dify、Coze、OpenAI 等多个渠道 |
| 团队协作 / Team collaboration | 用一份可版本化、可 review 的 YAML 描述智能体，避免平台 UI 上的"隐式配置"丢失 |
| 环境迁移 / Environment migration | 从一个平台迁移到另一个平台时，有标准中间格式可参照 |
| CI/CD 部署 / CI/CD deployment | 将智能体配置纳入代码仓库，通过脚本自动部署到目标平台 |
| 灾备与回滚 / Backup & rollback | 配置以文件形式存档，可快速重建或回滚到历史版本 |

**不适用 / Not applicable：** 仅依赖某平台专属能力（如 Dify 工作流可视化编排、Coze 插件生态）且无法抽象为通用配置的场景——此时应直接使用平台原生 DSL。

---

## 3. 核心方法论 / Core Methodology

### 3.1 单一事实源（Single Source of Truth）

所有智能体定义集中在一个 `config.yaml` 中，包含六个域：

1. **meta** — 元信息（名称、版本、描述）
2. **model** — 模型选择与采样参数
3. **persona** — 系统提示词、语气风格
4. **tools** — 工具/函数定义
5. **memory** — 记忆与上下文策略
6. **guardrails** — 安全护栏与输出约束

### 3.2 适配优先级（Adaptation Priority）

当通用配置与目标平台原生能力冲突时，按以下优先级取舍：

```
安全护栏 (guardrails) > 行为正确性 > 人格一致性 > 效率优化 > 平台原生体验
```

**原则：** 护栏与真实性规则在任何平台都不可丢失；为追求平台特性而牺牲正确性的适配是错误适配。

### 3.3 能力映射矩阵（Capability Mapping Matrix）

每个平台对六个域的支持程度不同。适配前先确认目标平台的能力边界：

| 域 / Domain | Dify | Coze | OpenAI (Responses/Assistants) | LangChain | 自定义框架 |
|---|---|---|---|---|---|
| meta | DSL 内置 | Bot 信息 | Assistant/Prompt 元数据 | 代码变量 | 自定义 |
| model | 节点内配置 | BotModelInfoConfig | 请求参数 | llm 绑定 | 自定义 |
| persona | LLM 节点 prompt | BotPromptInfo | instructions / input instructions | system message | 自定义 |
| tools | 工具节点 / 函数 | 插件 / workflow | function / 内置工具 | BaseTool 列表 | 自定义 |
| memory | 会话变量 / 记忆节点 | auto_save_history | previous_response_id / Thread | RunnableWithMessageHistory | 自定义 |
| guardrails | 内容审核前置节点 | 平台审核 + prompt | moderation / prompt 约束 | 输出解析器 + 校验 | 自定义 |

> 注：OpenAI Assistants API 已于 2025-08-26 宣布弃用，硬停止日期为 2026-08-26，官方推荐迁移至 Responses API + Conversations API。详见第 5 节。

---

## 4. 决策树 / 流程图 — Decision Tree

```
开始部署 / Start
   │
   ▼
读取 config.yaml / Read config.yaml
   │
   ▼
选择目标平台 / Select target platform ──┬── Dify ────────► 转换为 DSL(YAML) → 导入校验 → 发布
   │                                     │
   ├── Coze ──────► 调用 Bot 创建/更新 API → 发布为 API 连接器
   │
   ├── OpenAI ────► 优先 Responses API（新建）；遗留系统 Assistants API（迁移中）
   │
   ├── LangChain ─► 生成 Python 配置代码 → AgentExecutor 运行
   │
   └── 自定义 ────► 生成框架适配层代码
   │
   ▼
能力缺口检查 / Capability gap check
   │
   ├─ 缺口在 guardrails? ──► YES ──► 必须在 prompt 或前置/后置环节补齐，否则拒绝部署
   │                       └─ NO
   ├─ 缺口在 tools? ───────► YES ──► 降级为"提示模型手动处理"或换平台
   │                       └─ NO
   └─ 缺口在 memory? ─────► YES ──► 降级为无状态，记录已知限制
   │
   ▼
部署后回归 / Post-deploy regression
   │
   ├─ 护栏用例通过? ──► NO ──► 回滚，不可上线
   └─ 人格用例通过? ──► NO ──► 调整 prompt 后重试
   │
   ▼
完成 / Done
```

---

## 5. 各平台真实部署步骤 / Platform-specific Real Deployment Steps

> 以下步骤基于各平台官方文档（截至 2025–2026）。涉及具体字段名若官方文档有更新，以官方为准；不确定处标注 **需验证**。

### 5.1 Dify — DSL 导入

**背景事实：** Dify DSL 是 Dify.AI 在 v0.6 及之后定义的 AI 应用工程文件标准，文件格式为 YML（也支持 JSON 序列化，遵循统一 schema）。它涵盖应用基本描述、模型参数、编排配置等信息。导入时会进行版本检查，若 DSL 文件版本低于当前实例会发出警告。DSL 文件**不包含**工具节点中已填入的授权信息（如第三方 API key）；若环境变量含 `Secret` 类型，导出时会询问是否允许导出敏感信息。

**部署步骤：**

1. 将 `config.yaml` 通过适配脚本转换为 Dify DSL（YAML）结构，包含：
   - 应用元信息（名称、描述、图标）
   - 模型参数（provider、model、temperature 等）
   - 编排配置（节点 + 连线 edges）
2. 在 Dify「Studio」页面选择「创建空白应用」或进入已有应用编排页。
3. 点击应用菜单中的「导入 DSL」（或在编排页左上角「导入 DSL」）。
4. 上传生成的 YML 文件。
5. 系统进行版本检查；若版本较低，按提示升级 Dify 实例或修正 DSL 版本字段。
6. 导入后在编排页校验：LLM 节点的 prompt、模型参数、工具节点是否正确映射。
7. 手动补齐工具节点的授权信息（API key 等，DSL 不携带）。
8. 在「发布」处发布为 Web App / API。

**config → DSL 关键字段映射（基于验证的结构）：**

| config.yaml | Dify DSL |
|---|---|
| `meta.name` / `meta.description` | 应用名称 / 描述 |
| `model.*` | LLM 节点的 model provider 配置 |
| `persona.system_prompt` | LLM 节点的 prompt / 系统提示词 |
| `tools[].name` | 工具节点（需手动补授权） |
| `guardrails.*` | 内容审核前置节点 + prompt 约束 |

> **需验证：** Dify DSL 顶层字段的确切名称（如 `app`、`kind`、`version`、`workflow`/`orchestration` 等）随版本演进，建议从目标 Dify 实例导出一份示例 DSL 作为字段参照模板，再据此填充。

### 5.2 Coze — Bot 配置与发布为 API

**背景事实：** Coze（扣子）是字节跳动的智能体平台，分国内版（coze.cn）与国际版（coze.com）。Bot 创建后可发布为 API 服务；发布时 Bot 获得版本号。Bot 配置数据结构包含 `BotPromptInfo`、`BotOnboardingInfo`、`BotModelInfoConfig`、`BotKnowledge`、`WorkflowIDList` 等。发布到 API 使用连接器 ID（如 `"1024"` 代表 API 渠道）。

**部署步骤（以国际版为例）：**

1. 在 Coze 工作台创建 Bot：填写名称、描述。
2. 配置模型（`BotModelInfoConfig`）：选择模型、设置温度等。
3. 编写 Persona/Prompt（`BotPromptInfo`）：将 `config.yaml` 的 `persona.system_prompt` 填入。
4. 配置插件/工作流：将 `config.yaml` 的 `tools` 映射为 Coze 插件或 workflow 节点。
5. （可选）配置知识库（`BotKnowledge`）。
6. 点击右上角「Publish」进入发布页。
7. 填写 changelog。
8. 在「Publish to > API」设置中选择「API」。
9. 点击「Publish」。
10. 发布后获取 Bot ID，用于调用 Chat API。

**调用 Chat API（v3）：**

- 端点：`POST https://api.coze.com/v3/chat`（国际版）/ `POST https://api.coze.cn/v3/chat`（国内版）
- 请求参数（已验证）：
  - `bot_id`（必填）：Bot 唯一标识
  - `user_id`（必填）：用户标识
  - `stream`（必填）：是否流式
  - `auto_save_history`（必填）：是否自动保存历史；**当 `stream=true` 时必须为 `false`**
  - `additional_messages`（必填）：消息数组
  - `conversation_id`（可选）：会话 ID，复用已有会话
- 鉴权：`Authorization: Bearer {access_token}`

> **需验证：** `additional_messages` 数组内每条消息的字段结构（`role`、`content`、`content_type` 等）以官方 Chat v3 文档为准。

### 5.3 OpenAI — Responses API（推荐）与 Assistants API（迁移中）

**重要事实：** OpenAI 于 2025-08-26 宣布 **Assistants API 弃用**，硬停止日期为 **2026-08-26**。官方推荐新建项目使用 **Responses API**（运行请求并返回输出）配合 **Conversations API**（存储多轮对话）进行替代。Assistant 配置将迁移至 dashboard 托管的「Prompts」。Chat Completions API 仍被持续支持（无状态，每次重发完整历史）。

#### 5.3a Responses API（新建项目推荐）

**部署步骤：**

1. 将 `config.yaml` 的 `persona.system_prompt` 作为 `instructions` 传入。
2. 将 `tools` 映射为：
   - 自定义函数 → `tools` 中的 function 定义（`type: "function"`）
   - 内置能力 → 内置工具（如 `web_search`、`file_search`）**（需验证：computer_use 等工具的确切 type 名称）**
3. 将 `model.name` 映射为请求的 `model` 字段。
4. 多轮对话通过 `previous_response_id` 串联（Responses API 的状态化机制），或使用 Conversations API 管理会话。
5. 护栏：在 `instructions` 中写明约束；必要时配合 moderation 接口。
6. 调用：`POST https://api.openai.com/v1/responses`，请求体含 `model`、`input`、`instructions`、`tools`。

> **需验证：** Responses API 请求体字段名（`input` vs `messages`）、`previous_response_id` 的确切行为、内置工具 `type` 字符串的完整列表——以 OpenAI 官方 API 参考为准。

#### 5.3b Assistants API（仅遗留系统，迁移倒计时中）

**对象模型：** Assistant、Thread、Message、Run、RunStep。

**部署步骤：**

1. 创建 Assistant：`POST /v1/assistants`，body 含 `model`、`name`、`instructions`（来自 `persona.system_prompt`）、`tools`。
2. 创建 Thread：`POST /v1/threads`。
3. 添加 Message：`POST /v1/threads/{thread_id}/messages`，body 含 `role`、`content`。
4. 创建 Run：`POST /v1/threads/{thread_id}/runs`，body 含 `assistant_id`。
5. 轮询 Run 状态直至 `completed`，再读取 messages。
6. 工具类型：`function`、`code_interpreter`、`file_search`。

> **迁移提醒：** 任何仍在 Assistants API 上的系统必须制定 2026-08-26 前的迁移计划。新功能不再添加到 Assistants API。

### 5.4 LangChain — Python 配置

**背景事实：** LangChain 提供 `create_tool_calling_agent(llm, tools, prompt)`（基于工具调用的 agent）与 `create_react_agent(llm, tools, prompt)`（ReAct 范式）。运行时由 `AgentExecutor(agent=agent, tools=tools, verbose=True)` 执行；会话记忆可通过 `RunnableWithMessageHistory` 包装。LangChain 已发布 1.0 版本。

**部署步骤：**

1. 安装：`pip install langchain langchain-openai`（或对应 provider 包）。
2. 初始化 LLM：将 `config.yaml` 的 `model` 映射为 `ChatOpenAI(model=..., temperature=...)` 等。
3. 构建 prompt 模板：包含 `system_prompt`（来自 persona）、`chat_history`、`agent_scratchpad`、`input` 占位符。
4. 定义工具：将 `config.yaml` 的 `tools` 实现为 `BaseTool` 子类或用 `@tool` 装饰器。
5. 创建 agent：`agent = create_tool_calling_agent(llm, tools, prompt)`。
6. 创建执行器：`agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)`。
7. 包装记忆：`RunnableWithMessageHistory(agent_executor, ...)` 实现多轮。
8. 护栏：在输出后用输出解析器/校验函数校验，不符则重试或拦截。
9. 部署：可用 LangServe（**需验证：LangServe 当前维护状态**）或 FastAPI 自建端点。

### 5.5 自定义框架

**部署步骤：**

1. 编写适配层（adapter）：将 `config.yaml` 解析为内部运行时对象。
2. 实现六个域的最小接口：`load_meta`、`load_model`、`load_persona`、`load_tools`、`load_memory`、`load_guardrails`。
3. 对无法原生支持的域，提供默认降级策略（见决策树）。
4. 部署为 HTTP 服务（FastAPI / Flask）或任务消费者。
5. 护栏必须在请求前（输入过滤）与响应后（输出校验）各设一道。

---

## 6. 模板示例 — Template Example

### 6.1 通用 config.yaml 模板（单一事实源）

```yaml
# config.yaml — 智能体通用配置 / Universal Agent Configuration
# 本文件是与平台无关的单一事实源，由适配脚本映射到各平台原生格式。

version: "1.0.0"          # 语义化版本 / semantic version

meta:
  name: "customer-support-agent"
  description: "电商售后客服智能体 / E-commerce after-sales support agent"
  author: "agent-ops"

model:
  provider: "openai"       # openai | anthropic | azure | ...
  name: "gpt-4o-mini"      # 需验证：模型名以 provider 官方为准
  temperature: 0.3
  max_tokens: 1024
  top_p: 1.0

persona:
  system_prompt: |
    你是一名电商售后客服。只回答售后相关问题。
    You are an e-commerce after-sales support agent. Only answer after-sales questions.
  tone:
    formality: "polite"    # casual | polite | formal
    verbosity: "concise"   # concise | balanced | verbose

tools:
  - name: "query_order"
    description: "查询订单状态 / Query order status"
    parameters:
      type: "object"
      properties:
        order_id:
          type: "string"
          description: "订单号 / Order ID"
      required: ["order_id"]
  - name: "submit_refund"
    description: "提交退款申请 / Submit refund request"
    parameters:
      type: "object"
      properties:
        order_id: { type: "string" }
        reason: { type: "string" }
      required: ["order_id", "reason"]

memory:
  type: "conversation"     # none | conversation | summary
  window: 10               # 保留最近 N 轮
  summary_strategy: "rolling"  # 需验证：具体压缩策略实现

guardrails:
  input_filter:
    - "拒绝处理与售后无关的请求 / Reject non-after-sales requests"
  output_constraints:
    - "不编造订单信息 / Do not fabricate order info"
    - "不承诺平台未提供的赔偿 / Do not promise unsupported compensation"
  forbidden_topics:
    - "政治 / politics"
    - "竞品对比 / competitor comparison"
  max_turns: 20
```

### 6.2 适配脚本结构示例（伪代码）

```python
# adapter.py — 概念示意，非可运行生产代码 / conceptual, not production-ready
import yaml

def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def to_dify_dsl(cfg: dict) -> dict:
    """映射为 Dify DSL(YAML)。需参照目标 Dify 实例导出的示例 DSL 校准字段名。"""
    # 需验证：具体顶层字段名以 Dify 版本为准
    return {
        # "app": {...}, "kind": "app", "version": ..., "workflow": {...}
    }

def to_coze_bot(cfg: dict) -> dict:
    """映射为 Coze Bot 配置结构。"""
    return {
        "prompt_info": cfg["persona"]["system_prompt"],
        "model_info_config": {
            "model": cfg["model"]["name"],
            "temperature": cfg["model"]["temperature"],
        },
        # workflow_id_list / knowledge 按需填充
    }

def to_openai_responses(cfg: dict) -> dict:
    """映射为 OpenAI Responses API 请求体。"""
    # 需验证：字段名以官方 API 参考为准
    return {
        "model": cfg["model"]["name"],
        "instructions": cfg["persona"]["system_prompt"],
        "tools": [{"type": "function", "function": t} for t in cfg["tools"]],
    }

def to_langchain(cfg: dict) -> str:
    """生成 LangChain Python 配置代码片段。"""
    return f"""
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="{cfg['model']['name']}", temperature={cfg['model']['temperature']})
# tools / prompt / AgentExecutor 略
"""
```

---

## 7. 常见陷阱 / Common Pitfalls

1. **把 API key 写进 config.yaml / Hardcoding secrets in config**
   - 危害：泄露到版本库。
   - 纠正：密钥永远放环境变量/密钥管理服务；config.yaml 只放结构，不放凭证。Dify DSL 本身就不携带工具授权信息，遵循同一原则。

2. **忽视平台能力缺口，静默降级 / Silent degradation on capability gaps**
   - 危害：guardrails 在某平台无对应能力时被悄悄丢弃，导致越界输出。
   - 纠正：适配时必须显式检查 guardrails 是否可落地；不可落地则拒绝部署或强制前置/后置补齐。

3. **把 Assistants API 当长期方案 / Treating Assistants API as long-term**
   - 危害：2026-08-26 硬停止后服务中断。
   - 纠正：新建项目用 Responses API；存量系统制定迁移计划。

4. **温度/采样参数未跨平台对齐 / Sampling params not aligned across platforms**
   - 危害：同一 config 在不同平台行为不一致。
   - 纠正：明确每个平台对 temperature/top_p 的取值范围与默认值，适配时做归一化。

5. **工具 schema 在平台间字段名不一致 / Tool schema field drift**
   - 危害：function calling 在某平台失败。
   - 纠正：以 OpenAI function calling 的 JSON Schema 为基准，其他平台做字段名映射并测试。

6. **memory 策略假定全平台支持 / Assuming universal memory support**
   - 危害：无状态平台丢失上下文，多轮对话崩坏。
   - 纠正：显式记录每个平台的 memory 能力，降级时告知用户已知限制。

7. **DSL 版本不匹配导致导入静默失败 / DSL version mismatch**
   - 危害：低版本 DSL 导入高版本实例后字段缺失。
   - 纠正：从目标实例导出示例 DSL 作为字段参照；导入后逐节点校验。

---

## 8. 检查清单 / Checklist

部署前逐项确认 / Confirm each item before deployment：

- [ ] `config.yaml` 已通过 schema 校验，六域齐全 / config passes schema validation, all 6 domains present
- [ ] 无任何密钥硬编码在 config 中 / no secrets hardcoded in config
- [ ] 目标平台能力缺口已识别，guardrails 缺口已补齐 / capability gaps identified, guardrail gaps filled
- [ ] model 参数已按目标平台归一化 / model params normalized per platform
- [ ] 工具 schema 已在目标平台测试可调用 / tool schema tested callable on platform
- [ ] memory 策略与平台能力匹配，降级限制已记录 / memory strategy matches platform capability, degradations logged
- [ ] OpenAI 项目已确认使用 Responses API（新建）或有 Assistants 迁移计划 / OpenAI project uses Responses API (new) or has Assistants migration plan
- [ ] Dify DSL 版本与目标实例匹配，已参照示例 DSL 校准字段 / Dify DSL version matches instance, fields calibrated against sample
- [ ] Coze Bot 已发布且获得 Bot ID，Chat API 鉴权可用 / Coze Bot published with Bot ID, Chat API auth working
- [ ] 护栏用例（越界输入/输出）回归通过 / guardrail regression cases pass
- [ ] 人格用例（语气/边界）回归通过 / persona regression cases pass
- [ ] 已记录本次部署的平台版本与 config 版本，便于回滚 / platform & config versions recorded for rollback
