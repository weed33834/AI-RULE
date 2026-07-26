---
# Skills 四元组（S = C, π, T, R；悉尼科大 + CSIRO Data61 2026 形式化）
applicable_when: C    # 用户已通过 tool-design.md 完成工具三层规范设计，需要具体模板/示例参考
terminates_when: T    # 完整工具定义已编写、工具规格文档已填写（基本信息/参数/返回值/错误处理/人工确认策略）
provides: π           # L0-L4 五级副作用完整工具定义示例、工具规格文档模板（含基本信息/参数/返回值/错误处理/人工确认策略）
interface: R          # 输入=工具名与设计意图；输出=可直接复用的工具定义 JSON + 规格文档模板
---

# 工具设计模板示例 (Tool Design Templates)

> 本文件为 [tool-design.md](./tool-design.md) 的子文件，提供可复用的工具定义示例与规格文档模板。

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
