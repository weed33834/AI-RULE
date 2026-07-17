# Workflow Automator Agent / 工作流自动化智能体

> 一个即用型工作流自动化智能体模板，使用计划-执行（Plan-and-Execute）模式管理任务、通知、事件调度、API调用和文件操作，具备长期记忆和任务上下文。
> A ready-to-use workflow automator agent template using Plan-and-Execute for task management, notifications, scheduling, API calls, and file operations, with long-term memory and task context.

---

## 目录结构 / Directory Structure

```
workflow-automator/
├── system-prompt.md     # 系统提示词（中英双语，可直接粘贴使用）
├── config.yaml          # 智能体配置（模型/温度/工具/记忆/安全策略）
├── tools.json           # 工具定义（OpenAI Function Calling 格式）
├── test-cases.md        # 测试用例（22个，含正常/边界/对抗/真实性）
└── README.md            # 本文件
```

## 功能概览 / Features

| 功能 / Feature | 说明 / Description |
|---|---|
| 创建任务 / Create Task | 创建带标题、描述、截止日期和优先级的任务 |
| 更新任务 / Update Task | 更新任务状态、描述和属性 |
| 发送通知 / Send Notification | 通过邮件、Slack、SMS 等发送通知 |
| 调度事件 / Schedule Event | 创建日历事件和提醒 |
| 调用 API / Call API | 调用外部 API（GET/POST/PUT/DELETE/PATCH） |
| 读写文件 / Read/Write File | 读取和写入文件 |

## 配置说明 / Configuration

| 配置项 / Config | 值 / Value |
|---|---|
| 推理模式 / Reasoning | Plan-and-Execute |
| 模型 / Model | gpt-4o |
| 温度 / Temperature | 0.3 |
| 短期记忆 / Short-term Memory | 是 / Yes |
| 长期记忆 / Long-term Memory | 是 / Yes |
| 任务上下文 / Task Context | 是 / Yes |
| HTTPS 强制 / HTTPS Only | 是 / Yes |
| 注入防御 / Injection Defense | 是 / Yes |

## 确认点 / Confirmation Points

以下操作执行前需用户明确确认：

| 操作 / Action | 原因 / Reason |
|---|---|
| `send_notification` | 通知发送后不可撤回 |
| `call_api` (POST/PUT/DELETE) | 可能修改外部系统数据 |
| `write_file` | 可能覆盖重要文件 |
| `schedule_event` | 创建日历事件影响他人 |

## 计划-执行工作流 / Plan-and-Execute Workflow

```
用户工作流需求 (User Workflow Request)
    ↓
理解目标 (Understand Goal)
    ↓
分解步骤 (Break Down Steps) —— 含工具、依赖、风险
    ↓
呈现计划 (Present Plan) —— 等待用户确认
    ↓
逐步执行 (Execute Step by Step)
  ├─ create_task / update_task
  ├─ send_notification（需确认）
  ├─ schedule_event（需确认）
  ├─ call_api（需确认）
  └─ read_file / write_file（需确认）
    ↓
每步验证 (Verify Each Step)
    ↓
汇总报告 (Summary Report)
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
    name="Workflow Automator Agent",
    instructions=instructions,
    model="gpt-4o",
    temperature=0.3,
    tools=tools,
)
```

### 2. 工具后端实现 / Tool Backend Implementation

```python
import requests
import os

def call_api(url, method="GET", headers=None, body=None, params=None, timeout=30):
    # 1. 验证 HTTPS / Validate HTTPS
    if not url.startswith("https://"):
        return {"error": "Only HTTPS URLs are allowed."}
    # 2. 执行请求 / Execute request
    response = requests.request(
        method=method, url=url, headers=headers,
        data=body, params=params, timeout=timeout
    )
    # 3. 记录审计日志 / Log for audit
    log_api_call(url, method, response.status_code)
    return {"status_code": response.status_code, "body": response.text}

def write_file(file_path, content, append=False):
    # 1. 验证白名单 / Validate whitelist
    WHITELIST = ["/workspace/", "/tmp/", "/data/user/work/"]
    if not any(file_path.startswith(w) for w in WHITELIST):
        return {"error": f"Path not in whitelist: {file_path}"}
    # 2. 检查是否覆盖 / Check overwrite
    if os.path.exists(file_path) and not append:
        # 需用户确认 / Requires user confirmation
        pass
    # 3. 写入 / Write
    mode = "a" if append else "w"
    with open(file_path, mode) as f:
        f.write(content)
    return {"success": True, "path": file_path}
```

### 3. 集成 Slack / 邮件 / 日历

```python
# Slack 通知 / Slack notification
def send_notification(channel, recipient, message, subject=None):
    if channel == "slack":
        requests.post(recipient, json={"text": f"{subject}\n{message}"})
    elif channel == "email":
        # 使用 SMTP 或 SendGrid / Use SMTP or SendGrid
        pass

# Google Calendar / Outlook 日历事件
def schedule_event(title, start_time, end_time, timezone, attendees):
    # 使用 Google Calendar API 或 Microsoft Graph API
    pass
```

## 安全注意事项 / Security Notes

- **HTTPS 强制 / HTTPS Only**: 所有 API 调用必须使用 HTTPS。
- **文件白名单 / File Whitelist**: 文件写入仅限白名单目录。
- **确认机制 / Confirmation**: 通知、API调用、文件写入需用户确认。
- **速率限制 / Rate Limit**: 每会话最多 50 次 API 调用。
- **审计日志 / Audit Log**: 记录所有 API 调用和文件操作。
- **注入防御 / Injection Defense**: 拒绝"跳过确认"的注入指令。

## 测试 / Testing

运行 `test-cases.md` 中的 22 个测试用例验证智能体行为。重点关注：
- 真实性测试：确保不编造 API 响应、任务结果和文件内容
- 对抗测试：确保 HTTP 调用、系统目录写入和确认绕过被阻止
- 边界测试：正确处理不存在的任务ID、API错误和文件覆盖
