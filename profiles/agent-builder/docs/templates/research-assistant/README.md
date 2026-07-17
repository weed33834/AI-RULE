# Research Assistant Agent / 研究助手智能体

> 一个即用型研究助手智能体模板，使用 ReAct+Reflection 模式进行文献调研、论文总结、笔记管理和引用生成，具备长期和情景记忆。
> A ready-to-use research assistant agent template using ReAct+Reflection for literature research, paper summarization, note management, and citation generation, with long-term and episodic memory.

---

## 目录结构 / Directory Structure

```
research-assistant/
├── system-prompt.md     # 系统提示词（中英双语，可直接粘贴使用）
├── config.yaml          # 智能体配置（模型/温度/工具/记忆/安全策略）
├── tools.json           # 工具定义（OpenAI Function Calling 格式）
├── test-cases.md        # 测试用例（22个，含正常/边界/对抗/真实性）
└── README.md            # 本文件
```

## 功能概览 / Features

| 功能 / Feature | 说明 / Description |
|---|---|
| 网络搜索 / Web Search | 搜索网络上的学术和非学术来源 |
| 读取链接 / Read URL | 获取网页、论文、文章的完整内容 |
| 总结论文 / Summarize Paper | 提取论文关键发现、方法和局限 |
| 保存笔记 / Save Note | 按主题存储研究发现到长期记忆 |
| 生成引用 / Cite Source | 生成 APA/MLA/Chicago/IEEE 格式引用 |

## 配置说明 / Configuration

| 配置项 / Config | 值 / Value |
|---|---|
| 推理模式 / Reasoning | ReAct + Reflection |
| 模型 / Model | claude-3.5-sonnet |
| 温度 / Temperature | 0.4 |
| 短期记忆 / Short-term Memory | 是 / Yes |
| 长期记忆 / Long-term Memory | 是 / Yes |
| 情景记忆 / Episodic Memory | 是 / Yes |
| 引用必需 / Citation Required | 是 / Yes |
| 注入防御 / Injection Defense | 是 / Yes |

## ReAct+Reflection 工作流 / Workflow

```
用户研究问题 (User Research Question)
    ↓
推理 (Reason) —— 分析需要什么信息
    ↓
行动 (Act) —— web_search / read_url / summarize_paper
    ↓
观察 (Observe) —— 审查搜索结果和内容
    ↓
反思 (Reflect) —— 评估来源可信度、证据强度、矛盾
    ↓
迭代 (Iterate) —— 信息不足时优化搜索
    ↓
综合 (Synthesize) —— 多来源综合，标注引用
    ↓
保存 (Save) —— save_note 存入长期记忆
```

## 部署指南 / Deployment Guide

### 1. Anthropic Claude API

```python
import anthropic
import json

client = anthropic.Anthropic()

with open("system-prompt.md") as f:
    system_prompt = f.read()
with open("tools.json") as f:
    tools = json.load(f)["tools"]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    temperature=0.4,
    system=system_prompt,
    tools=tools,
    messages=[{"role": "user", "content": "搜索关于...的研究"}]
)
```

### 2. 长期记忆实现 / Long-term Memory Implementation

```python
# 后端笔记存储 / Backend note storage
import sqlite3

def save_note(topic, title, content, source_urls, tags):
    conn = sqlite3.connect("research_notes.db")
    conn.execute("""
        INSERT INTO notes (topic, title, content, source_urls, tags, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (topic, title, content, json.dumps(source_urls), json.dumps(tags)))
    conn.commit()

def retrieve_notes(topic=None, tags=None):
    # 按主题或标签检索笔记
    pass
```

### 3. Web Search 工具后端 / Web Search Tool Backend

```python
# 可使用 SerpAPI, Tavily, Brave Search 等
# Can use SerpAPI, Tavily, Brave Search, etc.

def web_search(query, num_results=10, source_type="any"):
    # 调用搜索 API
    # 返回结构化结果
    pass

def read_url(url):
    # 使用 readability / trafilatura 提取正文
    # 返回标题、作者、日期、内容
    pass
```

## 安全注意事项 / Security Notes

- **引用必需 / Citation Required**: 所有论点必须有真实来源支撑，绝不编造引用。
- **来源评估 / Source Evaluation**: 自动评估来源可信度，识别掠夺性期刊。
- **注入防御 / Injection Defense**: 拒绝"编造引用"和"使用内置数据库"等注入指令。
- **预印本标注 / Preprint Flagging**: 自动标注预印本未经同行评审的状态。
- **PII 脱敏 / PII Masking**: 搜索和阅读过程中保护个人隐私信息。

## 测试 / Testing

运行 `test-cases.md` 中的 22 个测试用例验证智能体行为。重点关注：
- 真实性测试：确保不编造论文内容、搜索结果、作者和引用
- 对抗测试：确保不被诱导编造引用或忽略来源局限
- 边界测试：正确处理无结果、URL不可访问和矛盾来源
