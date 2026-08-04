# Customer Service Agent / 客服智能体

> 一个即用型电商客服智能体模板，支持订单查询、退款处理、FAQ解答和人工升级。
> A ready-to-use e-commerce customer service agent template supporting order inquiries, refunds, FAQ, and human escalation.

---

## 目录结构 / Directory Structure

```
customer-service/
├── system-prompt.md     # 系统提示词（中英双语，可直接粘贴使用）
├── config.yaml          # 智能体配置（模型/温度/工具/记忆/安全策略）
├── tools.json           # 工具定义（OpenAI Function Calling 格式）
├── test-cases.md        # 测试用例（22个，含正常/边界/对抗/真实性）
└── README.md            # 本文件
```

## 功能概览 / Features

| 功能 / Feature | 说明 / Description |
|---|---|
| 订单查询 / Order Search | 通过订单号、邮箱或手机号搜索订单 |
| 订单状态 / Order Status | 查询发货、配送、支付等详细状态 |
| 退款处理 / Refund Processing | 按政策处理退款，执行前需用户确认 |
| FAQ 解答 / FAQ Answers | 从知识库检索常见问题答案 |
| 人工升级 / Human Escalation | 超出范围时升级至人工客服 |

## 配置说明 / Configuration

| 配置项 / Config | 值 / Value |
|---|---|
| 推理模式 / Reasoning | ReAct |
| 模型 / Model | gpt-4o |
| 温度 / Temperature | 0.3 |
| 短期记忆 / Short-term Memory | 是 / Yes |
| 用户偏好 / User Preferences | 是 / Yes |
| PII 脱敏 / PII Masking | 是 / Yes |
| 注入防御 / Injection Defense | 是 / Yes |

## 部署指南 / Deployment Guide

### 1. OpenAI Assistants API

```python
from openai import OpenAI

client = OpenAI()

# 读取系统提示词 / Read system prompt
with open("system-prompt.md", "r") as f:
    system_prompt = f.read()

# 读取工具定义 / Read tools
import json
with open("tools.json", "r") as f:
    tools = json.load(f)["tools"]

assistant = client.beta.assistants.create(
    name="Customer Service Agent",
    instructions=system_prompt,
    model="gpt-4o",
    temperature=0.3,
    tools=tools,
)
```

### 2. Dify / Coze 等平台

1. 创建新智能体 / Create a new agent
2. 将 `system-prompt.md` 的内容粘贴到"系统提示词"字段 / Paste system prompt content
3. 在"工具"配置中导入 `tools.json` / Import tools.json in tool configuration
4. 设置温度为 0.3 / Set temperature to 0.3
5. 启用短期记忆 / Enable short-term memory

### 3. 自定义后端 / Custom Backend

```python
# 伪代码 / Pseudocode
def handle_customer_message(user_input, session_id):
    # 1. 加载系统提示词 / Load system prompt
    # 2. 注入短期记忆和用户偏好 / Inject short-term memory & user preferences
    # 3. 调用 LLM (temperature=0.3) / Call LLM
    # 4. 如果 LLM 返回工具调用 / If tool call returned:
    #    - refund_order: 需用户确认 / Requires user confirmation
    #    - escalate_to_human: 需用户确认 / Requires user confirmation
    # 5. 执行工具，返回结果 / Execute tool, return result
    pass
```

## 安全注意事项 / Security Notes

- **退款确认 / Refund Confirmation**: `refund_order` 执行前必须与用户确认金额和原因。
- **金额限制 / Amount Limit**: 退款超过 $500 需升级人工审批。
- **PII 保护 / PII Protection**: 用户邮箱、手机号等信息需脱敏存储。
- **注入防御 / Injection Defense**: 拒绝"忽略指令"类提示注入攻击。
- **身份验证 / Identity Verification**: 查询订单需验证用户身份（邮箱/手机号匹配）。

## 测试 / Testing

运行 `test-cases.md` 中的 22 个测试用例验证智能体行为。重点关注：
- 真实性测试：确保不编造订单状态和FAQ答案
- 对抗测试：确保不被提示注入和社交工程绕过
- 边界测试：确保退款政策正确执行
