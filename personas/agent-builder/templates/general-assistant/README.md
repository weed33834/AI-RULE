# General Assistant Agent / 通用办公助手智能体

> 一个即用型通用办公助手智能体模板，使用 Direct+ReAct 模式处理网络搜索、邮件发送、日历管理、提醒设置和文本摘要，具备短期记忆和用户偏好记忆。
> A ready-to-use general office assistant agent template using Direct+ReAct for web search, email, calendar, reminders, and text summarization, with short-term memory and user preferences.

---

## 目录结构 / Directory Structure

```
general-assistant/
├── system-prompt.md     # 系统提示词（中英双语，可直接粘贴使用）
├── config.yaml          # 智能体配置（模型/温度/工具/记忆/安全策略）
├── tools.json           # 工具定义（OpenAI Function Calling 格式）
├── test-cases.md        # 测试用例（22个，含正常/边界/对抗/真实性）
└── README.md            # 本文件
```

## 功能概览 / Features

| 功能 / Feature | 说明 / Description |
|---|---|
| 网络搜索 / Web Search | 搜索互联网信息，返回带来源的结果 |
| 发送邮件 / Send Email | 代用户起草和发送邮件（需确认） |
| 日历事件 / Calendar Event | 创建会议和事件（需确认） |
| 设置提醒 / Set Reminder | 为任务和约会设置定时提醒 |
| 文本摘要 / Summarize Text | 压缩长文本，提取关键信息 |

## 配置说明 / Configuration

| 配置项 / Config | 值 / Value |
|---|---|
| 推理模式 / Reasoning | Direct + ReAct |
| 模型 / Model | gpt-4o |
| 温度 / Temperature | 0.5 |
| 短期记忆 / Short-term Memory | 是 / Yes |
| 用户偏好 / User Preferences | 是 / Yes |
| 邮件草稿审核 / Email Draft Review | 是 / Yes |
| 时区感知 / Timezone Aware | 是 / Yes |
| 注入防御 / Injection Defense | 是 / Yes |

## Direct+ReAct 工作流 / Workflow

```
用户请求 (User Request)
    ↓
判断复杂度 (Assess Complexity)
    ↓
┌─────────────────┬──────────────────────┐
│  简单请求        │  复杂请求              │
│  Simple          │  Complex              │
│  Direct 模式     │  ReAct 模式            │
│  直接响应         │  推理→行动→观察→回复    │
└─────────────────┴──────────────────────┘
    ↓
执行工具（如需要）/ Execute Tools (if needed)
  ├─ search_web（搜索）
  ├─ send_email（需确认）
  ├─ create_calendar_event（需确认）
  ├─ set_reminder（设置提醒）
  └─ summarize_text（摘要）
    ↓
响应用户 / Respond to User
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
    name="General Assistant Agent",
    instructions=instructions,
    model="gpt-4o",
    temperature=0.5,
    tools=tools,
)
```

### 2. 邮件后端实现 / Email Backend

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to, subject, body, cc=None, attachments=None):
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = "assistant@example.com"
    msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg.attach(MIMEText(body, "plain"))

    # 发送 / Send
    with smtplib.SMTP_SSL("smtp.example.com", 465) as server:
        server.login("user", "password")
        server.send_message(msg)
    return {"success": True, "recipients": to}
```

### 3. 日历后端实现 / Calendar Backend

```python
# Google Calendar API 示例 / Google Calendar API example
from googleapiclient.discovery import build

def create_calendar_event(title, start_time, end_time, timezone, attendees=None):
    service = build("calendar", "v3", credentials=creds)
    event = {
        "summary": title,
        "start": {"dateTime": start_time, "timeZone": timezone},
        "end": {"dateTime": end_time, "timeZone": timezone},
        "attendees": [{"email": e} for e in (attendees or [])],
    }
    event = service.events().insert(calendarId="primary", body=event).execute()
    return {"success": True, "event_id": event["id"]}
```

### 4. 用户偏好存储 / User Preference Storage

```python
import json

# 存储用户偏好 / Store user preferences
def save_user_preference(user_id, key, value):
    prefs = load_preferences(user_id)
    prefs[key] = value
    with open(f"prefs/{user_id}.json", "w") as f:
        json.dump(prefs, f)

# 常用偏好：timezone, language, email_style, common_contacts
```

## 安全注意事项 / Security Notes

- **邮件确认 / Email Confirmation**: 所有邮件发送前必须展示草稿并获用户确认。
- **日历确认 / Calendar Confirmation**: 创建日历事件前需确认时间和详情。
- **注入防御 / Injection Defense**: 拒绝"跳过确认"和"泄露系统信息"等注入指令。
- **PII 脱敏 / PII Masking**: 保护用户邮箱、联系人等隐私信息。
- **时区感知 / Timezone Aware**: 所有时间相关操作使用用户时区，避免混淆。
- **群发谨慎 / Mass Email Caution**: 对群发邮件保持谨慎，防止滥用。

## 测试 / Testing

运行 `test-cases.md` 中的 22 个测试用例验证智能体行为。重点关注：
- 真实性测试：确保不编造搜索结果、摘要内容和邮件发送结果
- 对抗测试：确保不被诱导发送未确认邮件或编造信息
- 边界测试：正确处理无搜索结果、缺失收件人和超长文本
