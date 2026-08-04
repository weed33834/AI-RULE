# AgentSeed — 一条命令，给你的 Agent 一个大脑

> **`pip install agentseed && agentseed forge`** → 空白 Agent 立刻拥有完整人格、规则体系、技能和工具配置。

**🌐 语言:** [English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md)

**📦 平台分布:** [GitHub](https://github.com/weed33834/agentseed) — **主平台**（Releases、pip 安装、CI/CD） · [Gitee](https://gitee.com/badhope/agentseed) — 备份镜像 · [Gitcode](https://gitcode.com/badhope/agentseed) — 备份镜像

![License](https://img.shields.io/badge/license-MIT-blue)
![Personas](https://img.shields.io/badge/personas-6-green)
![Platforms](https://img.shields.io/badge/platforms-13-orange)
![Tests](https://img.shields.io/badge/tests-144%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-informational)

AgentSeed 是一个 **面向 AI Agent 的人格治理平台**。把它注入空白 AI 编程助手（Claude Code、Cursor、Copilot、Trae、Gemini、Windsurf 等），立刻获得：

- 🧬 **永久大脑（治理引擎）** — 安全边界、决策公式、自进化触发
- 🎭 **可插拔人格（Persona Packs）** — coding、novel、paper、conversation、interactive-novel、agent-builder
- 🚀 **零配置平台同步** — 13 个平台，一条命令

---

## 工作原理

```
┌──────────────────────────────────────────────┐
│                 AgentSeed                      │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  ⚡ 治理引擎（不可插拔）                  │ │
│  │  P0 安全红线 · 决策公式 · 自进化触发     │ │
│  └─────────────────────────────────────────┘ │
│                    ↓                          │
│  ┌─────────────────────────────────────────┐ │
│  │  🎭 人格包（可插拔画像）                  │ │
│  │  coding · novel · paper · agent-builder   │ │
│  │  conversation · interactive-novel · 自定义│ │
│  └─────────────────────────────────────────┘ │
│                    ↓                          │
│  ┌─────────────────────────────────────────┐ │
│  │  🚀 13 平台同步                           │ │
│  │  Claude Code · Cursor · Copilot · Trae   │ │
│  │  Gemini · Windsurf · Cline · Continue    │ │
│  │  Amazon Q · Qodo · Lingma · Comate       │ │
│  │  AGENTS.md（通用）                        │ │
│  └─────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

---

## 快速开始

```bash
# 安装
pip install https://github.com/weed33834/agentseed/releases/download/v2.4.0/agentseed-2.4.0-py3-none-any.whl

# 自动检测 → 装配 → 生成
agentseed forge

# 交互模式：选择你的画像
agentseed forge --interactive

# 指定画像
agentseed forge --profile coding

# 预览（不写文件）
agentseed forge --dry-run

# 切换画像
agentseed switch --profile novel

# 列出所有可用画像
agentseed list

# 同步到指定平台
agentseed sync --platform cursor

# 启动 MCP Server（stdio 模式）
agentseed serve

# 启动 MCP Server（HTTP/SSE 模式）
agentseed serve --port 8080
```

AgentSeed 会自动检测你的项目类型（pyproject.toml → coding、chapters/ → novel 等），选择最合适的 Persona Pack，并生成所有必要的规则文件。

### MCP Server

AgentSeed 将治理引擎和画像管理能力暴露为 MCP 工具，任何兼容 MCP 的客户端都可以程序化地查询和强制执行 AI 安全规则：

| 工具 | 描述 |
|------|------|
| `governance_check` | 检查工具调用是否违反 P0 安全红线 |
| `persona_list` | 列出所有可用的画像包 |
| `persona_activate` | 切换到指定画像 |
| `gap_detect` | 分析上下文是否存在能力缺口 |

在 MCP 客户端中配置：

```json
{
  "mcpServers": {
    "agentseed": {
      "command": "agentseed",
      "args": ["serve"]
    }
  }
}
```

---

## 为什么用 AgentSeed？

| 问题 | AgentSeed 方案 |
|---------|-------------------|
| AI Agent 缺乏一致的行为规则 | **P0 治理** — 处处相同的安全基线 |
| 不同任务需要不同人格 | **Persona Packs** — 切换身份而不丢失安全 |
| 为多个工具配置规则很繁琐 | **13 平台同步** — 一条命令全覆盖 |
| Agent 在预设工具失败时卡住 | **自进化引擎** — 自动检测缺口，搜索/获取/安装 |
| 自定义人格难以创建和分享 | **Persona 市场** — 创建一次，社区共享 |

### 对比竞品

| 项目 | 做什么 | AgentSeed 差异 |
|---------|-------------|---------------------|
| agent-rules (steipete) | Cursor/Claude 的统一 .mdc 规则 | 已归档；仅编码 |
| agent-rules-books | 从软件书籍提炼的规则 | 仅编码；无人格 |
| ACP | Agent 配置 + MCP 管理 | 无治理；无自进化 |
| agents.md | AGENTS.md 格式标准 | 仅格式；无内容 |
| chatgpt_system_prompt | 系统提示词合集 | 仅收藏；无工具链 |
| **AgentSeed** | **完整人格 + 治理 + 同步平台** | **完整的 Agent 大脑** |

---

## 内含什么

### 🧬 治理引擎（宪法层）
永久大脑。任何 Persona Pack 都不能覆盖它。

- `core/governance.md` — P0 红线（安全、真实、边界）
- `core/constraints.yaml` — 机器可执行的钩子
- `core/agent-modes.md` — Task / Project / Autonomous 模式
- `core/self-evolution.md` — ★ 缺口检测 + 自愈
- `core/dar-spec.md` — 领域权威评分（搜索质量）
- `core/persona-router.md` — 人格路由与选择

### 🎭 人格包（可插拔）
每个包 = SOUL + 规则 + 技能 + MCP + 提示词

| 画像 | 适用 | 关键特质 |
|---------|-----|-----------|
| `coding` | 软件工程师 | 重构、测试、CI/CD |
| `novel` | 小说家 | 章节、人物、世界观 |
| `paper` | 学术研究者 | 文献综述、LaTeX、投稿 |
| `conversation` | 通用助手 | 问答、调研、分析 |
| `interactive-novel` | 游戏编剧 | 分支叙事、状态机 |
| `agent-builder` | Agent 设计师 | 构建、评估、部署 Agent |

### 🚀 平台同步
为 **13 个平台**生成平台原生规则文件：

Claude Code, Cursor, Copilot, Trae, Gemini, Windsurf, Cline, Continue, Amazon Q, Qodo, Lingma, Comate，以及 AGENTS.md（通用）。

---

## 架构

完整架构设计见 [docs/AGENTSEED_ARCHITECTURE.md](docs/AGENTSEED_ARCHITECTURE.md)。

关键创新：
- **骨架模式**：核心规则内联，技能按需加载 — 保持提示词精简
- **自进化引擎**：Agent 检测自身能力缺口并自愈
- **质量门禁**：所有自动获取的内容都通过 安全 → 质量 → 兼容 检查

---

## 安装

```bash
# pip — 从 GitHub Releases 安装（主平台）
pip install https://github.com/weed33834/agentseed/releases/download/v2.4.0/agentseed-2.4.0-py3-none-any.whl

# 从源码安装
git clone https://github.com/weed33834/agentseed.git     # GitHub（主平台）
git clone https://gitee.com/badhope/agentseed.git        # Gitee（镜像）
git clone https://gitcode.com/badhope/agentseed.git      # Gitcode（镜像）
cd agentseed
pip install -e .
```

---

## 开发

```bash
# 创建新画像
agentseed persona new my-role

# 验证规则
agentseed verify

# 运行测试
python -m pytest tests/

# 检查规则质量
python scripts/validate_rules.py
```

---

## 许可证

MIT

---

*AgentSeed: 宪法教 Agent 何时自己找资源，身份决定擅长领域。*
