# Code Reviewer Agent / 代码审查智能体

> 一个即用型代码审查智能体模板，使用反思（Reflection）模式审查代码变更，识别 Bug、安全漏洞、性能问题和风格违规。
> A ready-to-use code reviewer agent template using the Reflection pattern to review changes and identify bugs, vulnerabilities, performance and style issues.

---

## 目录结构 / Directory Structure

```
code-reviewer/
├── system-prompt.md     # 系统提示词（中英双语，可直接粘贴使用）
├── config.yaml          # 智能体配置（模型/温度/工具/记忆/安全策略）
├── tools.json           # 工具定义（OpenAI Function Calling 格式）
├── test-cases.md        # 测试用例（22个，含正常/边界/对抗/真实性）
└── README.md            # 本文件
```

## 功能概览 / Features

| 功能 / Feature | 说明 / Description |
|---|---|
| 读取文件 / Read File | 读取源文件内容进行审查 |
| 运行 Linter / Run Linter | 自动检测风格和语法问题 |
| 搜索模式 / Search Pattern | 查找相似代码、用法和重复 |
| Git Diff 分析 / Git Diff Analysis | 分析提交或 PR 的变更内容 |
| 结构化报告 / Structured Report | 按严重等级输出审查意见 |

## 配置说明 / Configuration

| 配置项 / Config | 值 / Value |
|---|---|
| 推理模式 / Reasoning | Reflection |
| 模型 / Model | gpt-4o |
| 温度 / Temperature | 0.2 |
| 短期记忆 / Short-term Memory | 是 / Yes |
| 长期记忆 / Long-term Memory | 否 / No |
| 只读模式 / Read-only | 是 / Yes |
| 注入防御 / Injection Defense | 是 / Yes |

## 反思模式工作流 / Reflection Workflow

```
初步审查 (Initial Review)
    ↓
反思质疑 (Reflect & Question) —— 这真的是问题吗？
    ↓
工具验证 (Verify with Tools) —— search_pattern / run_linter
    ↓
优化反馈 (Refine Feedback) —— 移除误报
    ↓
最终输出 (Final Output) —— 结构化报告
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
    name="Code Reviewer Agent",
    instructions=instructions,
    model="gpt-4o",
    temperature=0.2,
    tools=tools,
)
```

### 2. GitLab / Bitbucket 集成

将智能体配置为 Webhook 接收者，在 MR/PR 创建时触发审查，将结果作为评论发布。

## 安全注意事项 / Security Notes

- **只读模式 / Read-only**: 智能体只审查代码，不修改或提交代码。
- **敏感文件 / Sensitive Files**: 拒绝读取 `.env`、`secrets.yaml` 等敏感文件。
- **注入防御 / Injection Defense**: 拒绝"跳过审查"或"直接批准"的注入指令。
- **文件大小限制 / File Size Limit**: 单文件最大 5MB，防止读取超大文件。

## 测试 / Testing

运行 `test-cases.md` 中的 22 个测试用例验证智能体行为。重点关注：
- 真实性测试：确保不编造行号、Linter 输出和代码内容
- 对抗测试：确保不被注入绕过审查
- 边界测试：正确处理空文件、大文件和二进制文件
