# tool-design.md — 工具 / Function Calling 设计规范
# Tool / Function Calling Design Specification

---

## 一句话描述 / One-line Description

> 本文档定义 Agent 工具（Function Calling）的设计规范：基于 OpenAI Function Calling 标准结构，约束命名（动词+名词）、参数设计原则与副作用五级标注，确保工具可被 LLM 正确选择、安全调用、可审计追溯。
>
> This document defines the design specification for Agent tools (Function Calling): based on the OpenAI Function Calling standard structure, it constrains naming (verb+noun), parameter design principles, and a five-level side-effect annotation, ensuring tools can be correctly selected by LLMs, safely invoked, and auditably traced.

---

## 适用场景 / Applicable Scenarios

- **工具开发阶段**：为 Agent 设计新的可调用工具（Function / Tool）。
- **工具审查阶段**：评审已有工具是否符合命名规范、参数设计原则与副作用标注要求。
- **安全治理阶段**：根据副作用等级决定是否需要人工确认（human-in-the-loop）。
- **工具文档阶段**：生成统一的工具规格说明，供 LLM 与人类开发者共同理解。

---

## 核心方法论 / Core Methodology

工具设计遵循 **三层规范**：

```
┌───────────────────────────────────────────────┐
│  Layer 3: 副作用标注 Side-Effect Annotation   │  五级风险标注 → 决定是否需人工确认
├───────────────────────────────────────────────┤
│  Layer 2: 参数设计 Parameter Design           │  JSON Schema + 类型 + 必填 + 枚举
├───────────────────────────────────────────────┤
│  Layer 1: 结构与命名 Structure & Naming       │  OpenAI 标准格式 + 动词+名词命名
└───────────────────────────────────────────────┘
```

### Layer 1: 标准结构与命名 / Standard Structure & Naming

#### OpenAI Function Calling 标准结构

OpenAI Chat Completions API 的工具定义采用以下标准结构（基于 `tools` 参数）：

```json
{
  "type": "function",
  "function": {
    "name": "<工具名称>",
    "description": "<工具描述：做什么、何时用、返回什么>",
    "parameters": {
      "type": "object",
      "properties": {
        "<参数名>": {
          "type": "<JSON Schema 类型>",
          "description": "<参数描述>",
          "enum": ["<可选枚举值>"]
        }
      },
      "required": ["<必填参数名>"]
    }
  }
}
```

**字段说明**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `type` | 是 | 固定值 `"function"` |
| `function.name` | 是 | 工具名称，遵循命名规范（见下） |
| `function.description` | 是 | **最关键字段**。LLM 依据此决定是否调用该工具。须说明：工具做什么、何时该用、何时不该用、返回值含义。 |
| `function.parameters` | 是 | JSON Schema 对象，定义参数结构 |
| `function.parameters.properties` | 是 | 每个参数的类型、描述、约束 |
| `function.parameters.required` | 是 | 必填参数名数组（可为空数组 `[]`） |

> 参考来源：OpenAI Function Calling 官方文档 https://platform.openai.com/docs/guides/function-calling

#### 命名规范：动词+名词 / Naming Convention: Verb + Noun

工具名应采用 **小写蛇形命名（snake_case）**，结构为 **动词_名词**，明确表达"做什么动作 + 操作什么对象"。

| 规则 | 正确示例 | 错误示例 | 原因 |
|------|----------|----------|------|
| 动词开头 | `search_documents` | `documents` | 缺少动作，LLM 不知是搜索还是删除 |
| 动词+名词 | `create_issue` | `issue_creation` | 名词开头，动作不明确 |
| snake_case | `get_weather` | `getWeather` / `GetWeather` | 大小写不一致，部分系统不兼容 |
| 动词精确 | `delete_file` | `remove_file_permanently` | 过长；`delete` 已足够明确 |
| 避免缩写 | `calculate_total` | `calc_ttl` | 缩写降低 LLM 理解准确度 |

**常用动词词表**：

| 动词 | 语义 | 副作用倾向 |
|------|------|------------|
| `get` / `fetch` / `search` / `query` / `list` | 读取/查询 | 无/低 |
| `create` / `add` / `post` | 创建 | 中 |
| `update` / `edit` / `modify` / `set` | 修改 | 中高 |
| `delete` / `remove` | 删除 | 高 |
| `send` / `publish` / `notify` | 发送/通知 | 中高（外部可见） |
| `execute` / `run` | 执行命令/脚本 | 高（需评估） |

### Layer 2: 参数设计原则 / Parameter Design Principles

| 原则 | 说明 | 示例 |
|------|------|------|
| **类型明确** | 每个参数必须声明 JSON Schema 类型（string/number/integer/boolean/array/object） | `"type": "string"` |
| **描述充分** | 每个参数必须有 description，说明含义、格式、取值范围 | `"description": "城市名称，如 '北京' 或 'San Francisco, CA'"` |
| **必填最小化** | 仅将核心参数设为 required，可选参数提供默认值或允许省略 | 搜索工具的 `limit` 参数应可选，默认 10 |
| **枚举约束** | 取值有限的参数用 `enum` 约束，减少幻觉 | `"enum": ["celsius", "fahrenheit"]` |
| **原子参数** | 每个参数表达一个独立含义，避免复合参数 | 用 `city` + `country` 而非 `"location": "Beijing,China"` |
| **避免歧义** | 参数名应自解释，不依赖上下文 | 用 `repository_owner` 而非 `owner`（owner 含义模糊） |
| **数组需约束** | 数组参数应声明 `items` 类型与 `maxItems` | `"items": {"type": "string"}, "maxItems": 10` |

**JSON Schema 类型速查**：

| 类型 | JSON Schema | 示例值 |
|------|-------------|--------|
| 字符串 | `"type": "string"` | `"hello"` |
| 整数 | `"type": "integer"` | `42` |
| 浮点数 | `"type": "number"` | `3.14` |
| 布尔值 | `"type": "boolean"` | `true` |
| 数组 | `"type": "array"` | `[1, 2, 3]` |
| 对象 | `"type": "object"` | `{"key": "value"}` |
| 枚举字符串 | `"type": "string", "enum": [...]` | `"celsius"` |

### Layer 3: 副作用五级标注 / Five-Level Side-Effect Annotation

> 以下五级标注为本文档提出的 **设计约定（convention）**，非任何平台原生 API 字段。建议在工具的 `description` 中以标签形式标注，供编排层（如 LangGraph）据此决定是否需要人工确认。

| 等级 | 标签 | 语义 | 示例 | 人工确认要求 |
|------|------|------|------|--------------|
| **L0** | `[side-effect:none]` | 纯函数，无副作用，幂等。多次调用结果相同，不改变任何状态。 | `calculate_sum`、`format_date` | 不需要 |
| **L1** | `[side-effect:read]` | 只读查询。读取外部数据源但不修改。可能有缓存/日志等隐式副作用，但业务数据不变。 | `search_documents`、`get_weather`、`list_files` | 不需要 |
| **L2** | `[side-effect:create]` | 创建/写入。产生新数据或新记录，但不修改已有数据。可逆（通常可删除）。 | `create_issue`、`send_email`、`post_comment` | 视场景而定（建议确认） |
| **L3** | `[side-effect:update]` | 修改/更新。改变已有数据的状态或内容。可能可逆也可能不可逆。 | `update_profile`、`transfer_funds`、`rename_file` | 需要确认 |
| **L4** | `[side-effect:delete]` | 删除/不可逆。永久删除数据或执行不可逆操作。 | `delete_file`、`drop_table`、`execute_command` | 必须确认 |

**标注方式**：在 `description` 字段开头以方括号标签标注：

```json
{
  "description": "[side-effect:L3] 更新指定用户的个人资料字段。需要 user_id 和至少一个可更新字段。"
}
```

**编排层处理逻辑**（伪代码）：

```python
def execute_tool(tool, args):
    level = parse_side_effect_tag(tool.description)
    if level in ("L3", "L4"):
        # 需要人工确认
        approval = request_human_approval(tool.name, args, level)
        if not approval:
            return {"error": "用户拒绝执行"}
    return tool.run(args)
```

---

## Tool Context Policy (工具内嵌策略)

对应 AGENTS.md §5 新增规则。

工具接收两类输入：
1. **arguments**（模型设置）— 模型根据用户意图生成的参数
2. **tool context**（开发者设置）— 开发者确定的策略约束

通过 tool context 携带安全策略：
| 策略字段 | 作用 | 示例 |
|----------|------|------|
| select_only | 限制只读操作 | `select_only=True` |
| allowed_tables | 限制可访问表 | `tables=['users', 'orders']` |
| max_rows | 限制返回行数 | `max_rows=1000` |
| allowed_operations | 限制允许的操作 | `operations=['read', 'list']` |

即使模型尝试越权操作，工具层也会拒绝。安全边界不依赖模型自觉。

---

## 决策树 / Decision Tree

```
Q1: 工具是否只读取数据、不修改任何状态？
├─ 是 ──► 副作用 L0 或 L1，无需人工确认
└─ 否 ──► Q2

Q2: 工具是否创建新数据/新记录（不触碰已有数据）？
├─ 是 ──► 副作用 L2，视场景决定是否确认
└─ 否 ──► Q3

Q3: 工具是否修改已有数据？
├─ 是 ──► 副作用 L3，需人工确认
└─ 否 ──► Q4

Q4: 工具是否删除数据或执行不可逆操作？
├─ 是 ──► 副作用 L4，必须人工确认
└─ 否 ──► 重新评估，可能需要拆分工具

Q5: 参数是否有固定取值集合？
├─ 是 ──► 使用 enum 约束
└─ 否 ──► 确保 description 充分描述格式与范围

Q6: 工具名是否为"动词+名词"结构？
├─ 否 ──► 重命名为动词+名词
└─ 是 ──► 工具定义完成
```

---

## 模板示例 / Template Examples

### 完整工具定义示例 / Complete Tool Definition Example

以下为一组配套的工具定义，覆盖五级副作用：

#### L0 示例：纯计算（无副作用）

```json
{
  "type": "function",
  "function": {
    "name": "calculate_sum",
    "description": "[side-effect:L0] 计算一组数字的总和。纯计算，无副作用。当需要对数值列表求和时使用。",
    "parameters": {
      "type": "object",
      "properties": {
        "numbers": {
          "type": "array",
          "items": { "type": "number" },
          "description": "需要求和的数字列表",
          "maxItems": 100
        }
      },
      "required": ["numbers"]
    }
  }
}
```

#### L1 示例：只读查询

```json
{
  "type": "function",
  "function": {
    "name": "search_documents",
    "description": "[side-effect:L1] 在知识库中全文搜索文档。只读操作，不修改任何数据。当用户需要查找资料、检索信息时使用。返回匹配文档的标题和摘要列表。",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "搜索关键词或自然语言查询"
        },
        "limit": {
          "type": "integer",
          "description": "返回结果的最大数量，默认 10",
          "default": 10,
          "minimum": 1,
          "maximum": 50
        },
        "sort_by": {
          "type": "string",
          "enum": ["relevance", "date_desc", "date_asc"],
          "description": "排序方式：相关性、日期降序、日期升序",
          "default": "relevance"
        }
      },
      "required": ["query"]
    }
  }
}
```

#### L2 示例：创建/写入

```json
{
  "type": "function",
  "function": {
    "name": "create_issue",
    "description": "[side-effect:L2] 在项目管理系统中创建一个新的 Issue（工单）。会产生新记录，但不修改已有数据。当用户需要提交 bug 报告、任务或需求时使用。",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "description": "Issue 标题，简明描述问题"
        },
        "description": {
          "type": "string",
          "description": "Issue 详细描述"
        },
        "priority": {
          "type": "string",
          "enum": ["low", "medium", "high", "urgent"],
          "description": "优先级",
          "default": "medium"
        },
        "assignee": {
          "type": "string",
          "description": "指派人用户名，可选"
        }
      },
      "required": ["title", "description"]
    }
  }
}
```

#### L3 示例：修改/更新

```json
{
  "type": "function",
  "function": {
    "name": "update_profile",
    "description": "[side-effect:L3] 更新指定用户的个人资料字段。会修改已有数据，需人工确认。当用户需要修改自己的资料信息时使用。至少需要提供一个可更新字段。",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {
          "type": "string",
          "description": "目标用户 ID"
        },
        "display_name": {
          "type": "string",
          "description": "新的显示名称，可选"
        },
        "email": {
          "type": "string",
          "description": "新的邮箱地址，可选，需符合邮箱格式",
          "format": "email"
        },
        "bio": {
          "type": "string",
          "description": "新的个人简介，可选，最多 500 字符",
          "maxLength": 500
        }
      },
      "required": ["user_id"]
    }
  }
}
```

#### L4 示例：删除/不可逆

```json
{
  "type": "function",
  "function": {
    "name": "delete_file",
    "description": "[side-effect:L4] 永久删除指定文件。此操作不可逆，必须经过人工确认。仅当用户明确要求删除文件时使用。删除前应确认文件路径正确。",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "要删除的文件完整路径，如 '/data/reports/old_report.csv'"
        },
        "confirm": {
          "type": "boolean",
          "description": "必须为 true 才会执行删除。用于二次确认。",
          "enum": [true]
        }
      },
      "required": ["file_path", "confirm"]
    }
  }
}
```

### 工具规格文档模板 / Tool Specification Document Template

```markdown
# 工具规格: {tool_name}

## 基本信息
- 名称 (name): ___________
- 副作用等级 (side-effect): L__
- 描述 (description): ___________

## 参数
| 参数名 | 类型 | 必填 | 描述 | 约束 |
|--------|------|------|------|------|
| ___________ | ___________ | 是/否 | ___________ | ___________ |

## 返回值
- 类型: ___________
- 结构: ___________

## 错误处理
| 错误场景 | 返回码 | 处理建议 |
|----------|--------|----------|
| ___________ | ___________ | ___________ |

## 人工确认策略
- 是否需要确认: 是/否
- 确认方式: ___________
```

---

## 常见陷阱 / Common Pitfalls

### 生产级反模式（5 大致命错误）

> 以下是生产环境大多数 Agent 错误的根源，比普通陷阱更深层、更隐蔽。

| # | 反模式 | 描述 | 为什么致命 | 检测方法 | 修复方向 |
|---|--------|------|-----------|----------|----------|
| 1 | **God Tool（上帝工具）** | 一个工具用 `action` 参数分发几十种行为 | LLM 无法推理几十种行为的关系和冲突；描述过长导致选择精度下降 | 参数中含 `action`/`mode`/`type` 枚举超过 5 个值 | 拆分为多个原子工具，一个工具做一件事 |
| 2 | **Silent Failure（静默失败）** | 返回 `{result: null}` 或空字符串 | LLM 误判为成功，继续基于空结果推理，错误级联 | 输出为 null/空/无 error 字段 | 结构化错误返回：含错误码、是否可重试、建议操作 |
| 3 | **Unstructured Blob（非结构化输出）** | 返回原始 HTML/日志/巨型 JSON | 消耗大量 context 且 LLM 无法提取关键信息 | 返回值非 JSON 或 JSON 超过 500 token | 一致的输出信封，始终返回相同 shape |
| 4 | **Leaking Internal State（泄露内部状态）** | 返回数据库 ID、内部 API key、堆栈跟踪 | 安全风险 + LLM 被无关信息干扰 | 输出含 `id`/`key`/`token`/`traceback` | 返回值清洗，只暴露业务字段 |
| 5 | **Overlapping Tool Descriptions（工具描述重叠）** | 两个工具描述过于相似 | LLM 无法区分，随机选择导致错误调用 | 两个工具的 description 语义相似度 > 0.7 | 在 description 中明确"不做什么"：`Does NOT search emails — use search_communications for those` |

### 常规陷阱

1. **description 过于简短**：仅写"搜索文档"，LLM 无法判断何时该用此工具而非另一个类似工具。description 应说明"做什么、何时用、何时不用、返回什么"。
2. **命名缺少动词**：工具名为 `documents` 或 `weather`，LLM 不知是查询还是删除。必须动词+名词。
3. **参数过多且无分组**：一个工具 10+ 参数，LLM 难以正确填充。应拆分为多个职责单一的工具，或用对象参数分组。
4. **必填参数过滥**：所有参数都设为 required，导致 LLM 被迫为可选参数编造值。仅核心参数设为必填。
5. **缺少 enum 约束**：取值有限的参数（如优先级、排序方式）未用 enum，LLM 可能生成无效值。
6. **副作用等级缺失**：未标注副作用等级，编排层无法判断是否需要人工确认。删除类操作可能被 LLM 自动执行而造成损失。
7. **L4 工具无二次确认参数**：删除类工具缺少 `confirm: true` 参数，仅靠编排层拦截。应在工具定义层面也加入确认机制，做双重保护。
8. **description 与实际行为不符**：description 声称只读但实际会写入缓存/日志。应以业务数据是否变化为准标注副作用。
9. **返回值格式未文档化**：工具返回非结构化数据，LLM 无法解析观察结果。应返回结构化 JSON。
10. **忽视 OpenAI 工具数量上限**：OpenAI API 对单次请求的 tools 数量有上限（需验证当前具体限制值，请查阅官方文档）。工具过多应考虑检索式工具选择。

---

## 检查清单 / Checklist

### 结构与命名 / Structure & Naming
- [ ] 使用 OpenAI 标准结构（type/function/name/description/parameters）。
- [ ] 工具名为 snake_case 的"动词+名词"结构。
- [ ] 动词精确（get/create/update/delete 等），无歧义。
- [ ] 避免缩写，名称自解释。

### 参数设计 / Parameter Design
- [ ] 每个参数有明确的 JSON Schema 类型。
- [ ] 每个参数有充分的 description（含格式、范围说明）。
- [ ] 必填参数最小化（仅核心参数 required）。
- [ ] 取值有限的参数使用 enum 约束。
- [ ] 数组参数声明 items 类型和 maxItems。
- [ ] 参数原子化（一个参数一个含义）。

### 副作用标注 / Side-Effect Annotation
- [ ] description 开头标注 `[side-effect:L_]` 等级。
- [ ] L0/L1：确认确实不修改业务数据。
- [ ] L2：确认是创建新数据而非修改已有数据。
- [ ] L3：编排层已配置人工确认拦截。
- [ ] L4：工具定义包含 `confirm` 参数 + 编排层人工确认（双重保护）。

### 文档与测试 / Documentation & Testing
- [ ] 已填写工具规格文档模板。
- [ ] 返回值为结构化 JSON，格式已文档化。
- [ ] 已定义错误场景与返回码。
- [ ] 已测试 LLM 能否在多工具场景下正确选择此工具。
- [ ] 已测试边界参数（空值、超长、非法枚举）。
- [ ] OpenAI API 工具数量上限已确认（查阅官方文档）。
