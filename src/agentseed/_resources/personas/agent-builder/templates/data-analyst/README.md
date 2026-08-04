# Data Analyst Agent / 数据分析智能体

> 一个即用型数据分析智能体模板，使用计划-执行（Plan-and-Execute）模式进行数据查询、统计分析、可视化和报告导出。
> A ready-to-use data analyst agent template using the Plan-and-Execute pattern for data querying, statistical analysis, visualization, and report export.

---

## 目录结构 / Directory Structure

```
data-analyst/
├── system-prompt.md     # 系统提示词（中英双语，可直接粘贴使用）
├── config.yaml          # 智能体配置（模型/温度/工具/记忆/安全策略）
├── tools.json           # 工具定义（OpenAI Function Calling 格式）
├── test-cases.md        # 测试用例（22个，含正常/边界/对抗/真实性）
└── README.md            # 本文件
```

## 功能概览 / Features

| 功能 / Feature | 说明 / Description |
|---|---|
| 数据库查询 / Database Query | 执行只读 SQL SELECT 查询 |
| Python 执行 / Python Execution | 运行 pandas/numpy/scipy 数据分析代码 |
| 统计检验 / Statistical Test | t检验、方差分析、卡方检验、回归等 |
| 图表生成 / Chart Generation | 柱状图、折线图、散点图、热力图等 |
| 报告导出 / Report Export | 编译分析结果为 PDF/HTML/Markdown |

## 配置说明 / Configuration

| 配置项 / Config | 值 / Value |
|---|---|
| 推理模式 / Reasoning | Plan-and-Execute |
| 模型 / Model | gpt-4o |
| 温度 / Temperature | 0.3 |
| 短期记忆 / Short-term Memory | 是 / Yes |
| 任务上下文 / Task Context | 是 / Yes |
| SQL 只读 / SQL Read-only | 是 / Yes |
| PII 脱敏 / PII Masking | 是 / Yes |

## 计划-执行工作流 / Plan-and-Execute Workflow

```
用户提出分析需求 (User Request)
    ↓
制定分析计划 (Create Plan) —— 呈现给用户
    ↓
逐步执行 (Execute Step by Step)
  ├─ query_database（查询数据）
  ├─ execute_python（数据分析）
  ├─ statistical_test（统计检验）
  └─ generate_chart（生成图表）
    ↓
每步验证 (Verify Each Step) —— 检查结果合理性
    ↓
导出报告 (Export Report) —— 编译最终结果
```

## 部署指南 / Deployment Guide

### 1. OpenAI Assistants API

```python
from openai import OpenAI
import json

client = OpenAI()

with open("system-prompt.md") as f:
    instructions = f.read()
with open("tools.json") as f:
    tools = json.load(f)["tools"]

assistant = client.beta.assistants.create(
    name="Data Analyst Agent",
    instructions=instructions,
    model="gpt-4o",
    temperature=0.3,
    tools=tools,
)
```

### 2. 结合 Jupyter / Streamlit 部署

```python
# streamlit_app.py
import streamlit as st
from openai import OpenAI

st.title("Data Analyst Agent")
user_query = st.text_input("请输入您的分析需求 / Enter your analysis request")

if st.button("分析 / Analyze"):
    # 1. 发送请求到智能体
    # 2. 智能体返回计划，展示给用户确认
    # 3. 确认后逐步执行，实时展示结果
    # 4. 最终生成报告供下载
    pass
```

### 3. 数据库连接配置

智能体的 `query_database` 工具需要后端配置数据库连接：

```python
# 后端工具实现示例 / Backend tool implementation example
import psycopg2  # 或 pymysql, sqlite3 等

def query_database(sql: str, limit: int = 10000):
    # 1. 验证 SQL 为只读 SELECT
    # 2. 执行查询
    # 3. 返回结构化结果
    BLOCKED = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"]
    sql_upper = sql.upper()
    for kw in BLOCKED:
        if kw in sql_upper:
            return {"error": f"Blocked keyword: {kw}. Only SELECT allowed."}
    # ... 执行查询
```

## 安全注意事项 / Security Notes

- **SQL 只读 / SQL Read-only**: 只允许 SELECT 查询，阻止所有写操作。
- **注入防御 / Injection Defense**: 使用参数化查询，阻止 SQL 注入。
- **数据量限制 / Row Limit**: 最大返回 100,000 行，防止内存溢出。
- **PII 脱敏 / PII Masking**: 查询结果中的敏感信息需脱敏处理。
- **报告确认 / Report Confirmation**: `export_report` 需用户确认后执行。

## 测试 / Testing

运行 `test-cases.md` 中的 22 个测试用例验证智能体行为。重点关注：
- 真实性测试：确保不编造统计结果、p 值和数据库结构
- 对抗测试：确保 SQL 注入和写操作被阻止
- 边界测试：正确处理空结果、大数据量和空值
