---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 98adaa6f98486df4666888a6691e7607_1ceef2998fe911f19340525400f8a581
    ReservedCode1: yHS36G9hdMm2QqpZMx1pav5DMx0ojpmMIw1vSdBok2o+z2kWm2oK6fD8fwfMJimJIk09fWe6NGuj+2jWjvy45V0Ox3YYbjNeYOmBNEEoLJ2ordzFMc4Y3yBQZHVLJyKHY8ZA0Plu6cNhfSOAjNPLG0yXhwRB7+Ov3zmK6azjafilqTHPDccey6Q4mdM=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 98adaa6f98486df4666888a6691e7607_1ceef2998fe911f19340525400f8a581
    ReservedCode2: yHS36G9hdMm2QqpZMx1pav5DMx0ojpmMIw1vSdBok2o+z2kWm2oK6fD8fwfMJimJIk09fWe6NGuj+2jWjvy45V0Ox3YYbjNeYOmBNEEoLJ2ordzFMc4Y3yBQZHVLJyKHY8ZA0Plu6cNhfSOAjNPLG0yXhwRB7+Ov3zmK6azjafilqTHPDccey6Q4mdM=
---

# AgentSeed MCP Server 接入教程

> 版本：AgentSeed v2.4.0 | 最后更新：2026-08-04

---

## 目录

1. [什么是 AgentSeed MCP Server](#1-什么是-agentseed-mcp-server)
2. [安装与验证](#2-安装与验证)
3. [MCP Server 概览](#3-mcp-server-概览)
4. [工具详解与 JSON-RPC 示例](#4-工具详解与-json-rpc-示例)
   - [4.1 governance_check](#41-governance_check)
   - [4.2 persona_list](#42-persona_list)
   - [4.3 persona_activate](#43-persona_activate)
   - [4.4 gap_detect](#44-gap_detect)
5. [各平台 MCP 配置指南](#5-各平台-mcp-配置指南)
   - [5.1 Claude Desktop](#51-claude-desktop)
   - [5.2 Cursor](#52-cursor)
   - [5.3 Cline (VS Code 扩展)](#53-cline-vs-code-扩展)
   - [5.4 Windsurf](#54-windsurf)
   - [5.5 Continue](#55-continue)
   - [5.6 Gemini CLI](#56-gemini-cli)
   - [5.7 Codex CLI](#57-codex-cli)
   - [5.8 Trae](#58-trae)
   - [5.9 Claude Code](#59-claude-code)
6. [常见问题](#6-常见问题)

---

## 1. 什么是 AgentSeed MCP Server

AgentSeed 是一个 **AI Agent 人格治理平台**，为 AI 编码助手注入完整的**治理引擎（Governance Engine）**和**可切换人格包（Persona Packs）**。其 MCP Server 将治理引擎和人格管理能力暴露为标准 MCP 工具，使任何兼容 MCP 协议的客户端都能以编程方式查询和执行 AI 安全规则。

AgentSeed MCP Server 在整个系统中处于以下架构位置：

```
┌──────────────────────────────────────────────┐
│                 AgentSeed                      │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  ⚡ GOVERNANCE ENGINE (不可切换)         │ │
│  │  P0 红线 · 决策公式 · 自进化触发器      │ │
│  └─────────────────────────────────────────┘ │
│                    ↓                          │
│  ┌─────────────────────────────────────────┐ │
│  │  🎭 PERSONA PACKS (可切换)               │ │
│  │  coding · novel · paper · agent-builder   │ │
│  │  conversation · interactive-novel · custom│ │
│  └─────────────────────────────────────────┘ │
│                    ↓                          │
│  ┌─────────────────────────────────────────┐ │
│  │  🔌 MCP Server (stdio)  ← 本文档主题    │ │
│  │  governance_check / persona_list /       │ │
│  │  persona_activate / gap_detect           │ │
│  └─────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

---

## 2. 安装与验证

### 2.1 安装

AgentSeed 通过 GitHub Releases 分发 whl 包，**不发布到 PyPI**。使用 `pip` 直接安装：

```bash
pip install https://github.com/weed33834/agentseed/releases/download/v2.4.0/agentseed-2.4.0-py3-none-any.whl
```

> **要求**：Python 3.10+

### 2.2 验证安装

安装完成后，使用以下命令验证 MCP Server 是否正常：

```bash
# 查看版本
agentseed --version

# 直接启动测试（stdio 模式，按 Ctrl+C 退出）
agentseed serve
```

成功输出示例：

```
AgentSeed MCP Server v2.4.0 starting in stdio mode...
```

---

## 3. MCP Server 概览

| 属性 | 值 |
|------|-----|
| **传输协议** | stdio（标准输入/输出） |
| **通信格式** | JSON-RPC 2.0 |
| **工具数量** | 4 个 |
| **启动命令** | `agentseed serve` |
| **认证** | 无需认证（本地进程通信） |

通用 MCP 客户端配置模板：

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

### 四个核心工具

| 工具名 | 功能 | 必填参数 |
|--------|------|----------|
| `governance_check` | 检查工具调用是否违反 P0 安全红线 | `tool_name`, `tool_args` |
| `persona_list` | 列出所有可用的 Persona Pack | 无 |
| `persona_activate` | 切换到指定 Persona | `persona_id` |
| `gap_detect` | 分析上下文中的能力缺口 | `context` |

---

## 4. 工具详解与 JSON-RPC 示例

> 所有请求和响应均遵循 JSON-RPC 2.0 规范，通过 stdio 通道传输。

### 4.1 governance_check

**功能**：检查给定的工具调用是否违反 `core/constraints.yaml` 中定义的 P0 安全红线。

**输入参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tool_name` | string | 是 | 待检查的工具名称 |
| `tool_args` | object | 是 | 传递给该工具的参数对象 |

**示例请求**：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "governance_check",
    "arguments": {
      "tool_name": "shell_executor",
      "tool_args": {
        "command": "rm -rf /etc/nginx"
      }
    }
  }
}
```

**示例响应（违规）**：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"allowed\": false, \"reason\": \"[P0 DESTRUCTIVE_OP_REQUIRES_CONFIRM] 破坏性操作已拦截，需用户确认\", \"risk_level\": \"P0\"}"
      }
    ]
  }
}
```

**示例响应（通过）**：

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"allowed\": true, \"reason\": \"All P0 checks passed\", \"risk_level\": \"none\"}"
      }
    ]
  }
}
```

### 4.2 persona_list

**功能**：列出 `personas/` 目录下所有可用的 Persona Pack 及其基本信息。

**输入参数**：无。

**示例请求**：

```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tools/call",
  "params": {
    "name": "persona_list",
    "arguments": {}
  }
}
```

**示例响应**：

```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[{\"id\": \"coding\", \"name\": \"软件开发规则\", \"description\": \"\"}, {\"id\": \"novel\", \"name\": \"小说创作规则\", \"description\": \"\"}, {\"id\": \"paper\", \"name\": \"Academic Paper Writing Rules\", \"description\": \"\"}, {\"id\": \"conversation\", \"name\": \"通用对话规则\", \"description\": \"\"}, {\"id\": \"interactive-novel\", \"name\": \"互动小说游戏规则\", \"description\": \"\"}, {\"id\": \"agent-builder\", \"name\": \"智能体构建规则\", \"description\": \"\"}]"
      }
    ]
  }
}
```

### 4.3 persona_activate

**功能**：切换到指定的 Persona Pack，返回该 Persona 的配置摘要（包括能力、限制、锚点文件和关键词）。

**输入参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `persona_id` | string | 是 | Persona Pack 标识符（如 `coding`、`novel`） |

**示例请求**：

```json
{
  "jsonrpc": "2.0",
  "id": 30,
  "method": "tools/call",
  "params": {
    "name": "persona_activate",
    "arguments": {
      "persona_id": "coding"
    }
  }
}
```

**示例响应**：

```json
{
  "jsonrpc": "2.0",
  "id": 30,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"persona\": {\"id\": \"coding\", \"name\": \"软件开发规则\", \"capabilities\": {\"enables\": [\"research\", \"testing\", \"review\", \"agent-governance\", \"dar\"], \"forbids\": [\"game-engine\", \"worldbuilding\", \"npc-simulation\"]}, \"anchors\": [\"pyproject.toml\", \"package.json\", \"requirements.txt\", \"src/\", \"tests/\"], \"keywords\": [\"修复\", \"重构\", \"测试\", \"部署\", \"接口\", \"Bug\", \"CI\", \"代码\"]}, \"platform_files\": [\"AGENTS.md\", \"CLAUDE.md\", \"GEMINI.md\", \".cursor/rules/project_rules.mdc\", \".github/copilot-instructions.md\", \".trae/rules/project_rules.md\", \".windsurfrules\"]}"
      }
    ]
  }
}
```

### 4.4 gap_detect

**功能**：基于 `core/self-evolution.md` 中的缺口评分公式，分析给定上下文的能力缺口，并返回缺口评分和改进建议。

**输入参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `context` | string | 是 | 待分析的上下文文本（如用户问题、任务描述） |

**示例请求**：

```json
{
  "jsonrpc": "2.0",
  "id": 40,
  "method": "tools/call",
  "params": {
    "name": "gap_detect",
    "arguments": {
      "context": "请帮我部署一个基于 BERT 的情感分析模型到 AWS SageMaker 并配置自动扩缩容"
    }
  }
}
```

**示例响应**：

```json
{
  "jsonrpc": "2.0",
  "id": 40,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"gaps\": [], \"suggestions\": [\"缺口很小，使用现有能力尽力回答\"], \"gap_score\": 0.2}"
      }
    ]
  }
}
```

---

## 5. 各平台 MCP 配置指南

### 5.1 Claude Desktop

Claude Desktop 通过 `claude_desktop_config.json` 管理 MCP Server。

**配置文件路径**：

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**配置内容**：在 `mcpServers` 对象中添加 `agentseed` 条目：

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

**操作步骤**：

1. 找到或创建上述路径的 `claude_desktop_config.json` 文件
2. 在 `mcpServers` 中添加 `agentseed` 配置块
3. 重启 Claude Desktop
4. 在对话中即可调用 AgentSeed 的四个 MCP 工具

### 5.2 Cursor

Cursor 支持通过项目根目录下的 `.cursor/mcp.json` 配置 MCP Server。

**配置文件路径**：`<项目根目录>/.cursor/mcp.json`

**配置内容**：

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

**操作步骤**：

1. 在项目根目录创建 `.cursor` 文件夹（如已存在则跳过）
2. 创建或编辑 `.cursor/mcp.json`，写入上述配置
3. 重新加载 Cursor 窗口（`Ctrl+Shift+P` → "Developer: Reload Window"）
4. MCP 工具将出现在 Cursor 的工具面板中

> **注意**：Cursor 要求 `.cursor/mcp.json` 中的 `command` 在系统 PATH 中可访问。如果 `agentseed` 命令不在 PATH 中，请使用绝对路径，例如 `"command": "C:\\Users\\<用户名>\\AppData\\Local\\Programs\\Python\\Python310\\Scripts\\agentseed.exe"`。

### 5.3 Cline (VS Code 扩展)

Cline 是 VS Code 的 AI 编码扩展，通过扩展设置面板配置 MCP Server。

**操作步骤**：

1. 打开 VS Code，安装 Cline 扩展
2. 点击 Cline 侧边栏图标，进入设置
3. 找到 **MCP Servers** 配置区域
4. 点击 **Add MCP Server** 或编辑 `settings.json`，添加以下配置：

```json
{
  "cline.mcpServers": {
    "agentseed": {
      "command": "agentseed",
      "args": ["serve"]
    }
  }
}
```

5. 保存设置后，Cline 会自动启动 AgentSeed MCP Server
6. 工具将出现在 Cline 的 MCP 工具列表中

### 5.4 Windsurf

Windsurf 支持两种 MCP 配置方式。

#### 方式一：通过 `.windsurfrules` 文件

在项目根目录创建 `.windsurfrules` 文件，添加 MCP Server 配置：

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

#### 方式二：通过 Windsurf 设置界面

1. 打开 Windsurf
2. 进入 **Settings** → **MCP** 配置页
3. 点击 **Add MCP Server**
4. 填写以下信息：
   - **Name**: `agentseed`
   - **Command**: `agentseed`
   - **Args**: `serve`
5. 保存并重启 Windsurf

### 5.5 Continue

Continue 通过 `config.json` 管理 MCP Server。

**配置文件路径**：`~/.continue/config.json`

**配置内容**：在 `mcpServers` 对象中添加：

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

**操作步骤**：

1. 打开 Continue 配置文件：在 VS Code 中按 `Ctrl+Shift+P` 搜索 "Continue: Open config.json"
2. 在 `mcpServers` 中添加 `agentseed` 配置
3. 保存文件，Continue 会自动重载配置

### 5.6 Gemini CLI

Google Gemini CLI 通过项目级配置文件管理 MCP Server。

**操作步骤**：

1. 确保已安装 Gemini CLI
2. 在项目根目录创建或编辑 Gemini CLI 的 MCP 配置文件（通常为 `.gemini/mcp.json` 或 `mcp_config.json`）：

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

3. 使用 `gemini mcp add` 命令注册（如 CLI 支持）：

```bash
gemini mcp add agentseed -- agentseed serve
```

4. 重启 Gemini CLI 会话

> **提示**：Gemini CLI 的 MCP 支持仍在快速迭代中，如上述路径有变更，请参考最新 [Gemini CLI 文档](https://cloud.google.com/gemini-cli)。

### 5.7 Codex CLI

OpenAI Codex CLI 支持通过 JSON 配置文件接入 MCP Server。

**操作步骤**：

1. 在项目根目录创建 `.codex/mcp.json`：

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

2. 或者直接在 Codex CLI 交互会话中注册：

```bash
codex mcp add agentseed -- agentseed serve
```

3. 重新启动 Codex CLI 会话即可生效

> **注意**：Codex CLI 需要 `agentseed` 命令在系统 PATH 中。如使用虚拟环境，请先激活虚拟环境或使用绝对路径。

### 5.8 Trae

Trae 支持通过 `.trae` 配置目录管理 MCP Server。

**配置文件路径**：`<项目根目录>/.trae/mcp.json`

**配置内容**：

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

**操作步骤**：

1. 在项目根目录创建 `.trae` 文件夹
2. 创建 `.trae/mcp.json`，写入上述配置
3. 重启 Trae 或重新加载项目

> **说明**：Trae 生成的项目规则文件位于 `.trae/rules/project_rules.md`，与 MCP 配置互不影响，二者可同时使用。

### 5.9 Claude Code

Claude Code（Anthropic 的命令行 AI 编程工具）也支持 MCP Server。

**推荐方式**：使用 `claude mcp add` 命令一键注册：

```bash
claude mcp add agentseed -- agentseed serve
```

**手动配置方式**：编辑 `~/.claude.json`（全局）或项目根目录的 `.mcp.json`：

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

## 6. 常见问题

### Q1: 启动报错 "agentseed: command not found"

**原因**：`agentseed` 未在系统 PATH 中。

**解决方案**：
- 使用 `which agentseed`（Linux/macOS）或 `where agentseed`（Windows）检查安装位置
- 使用绝对路径替换配置中的 `"command": "agentseed"`，例如：
  - Windows: `"command": "C:\\Users\\<用户名>\\AppData\\Local\\Programs\\Python\\Python310\\Scripts\\agentseed.exe"`
  - macOS/Linux: `"command": "/Users/<用户名>/Library/Python/3.10/bin/agentseed"` 或 `"command": "~/.local/bin/agentseed"`

### Q2: MCP 工具在客户端不显示

**排查步骤**：

1. 确认 `agentseed serve` 命令能单独启动（在终端运行测试）
2. 检查 JSON 配置文件语法是否正确（可用在线 JSON 校验工具验证）
3. 确认客户端已完全重启（而非仅重新加载窗口）
4. 查看客户端日志（Claude Desktop 日志路径：`~/Library/Logs/Claude/`）

### Q3: AgentSeed 占用了过多资源吗？

MCP Server 以 stdio 模式运行，仅在客户端发送请求时占用 CPU，空闲时几乎不消耗资源。内存占用通常 < 50MB。

### Q4: 可以同时为多个项目配置 AgentSeed 吗？

可以。AgentSeed MCP Server 是项目无关的——它使用内置的治理规则和人格包，不依赖特定项目的上下文。在所有支持 MCP 的客户端中配置相同的 `agentseed serve` 即可。

### Q5: 如何切换 Persona？

使用 `persona_activate` 工具传入目标 `persona_id`。当前可用 ID 可以通过 `persona_list` 查询。切换后，后续的 MCP 调用将使用新 Persona 的规则和约束。

---

> **参考**：本文档基于 AgentSeed v2.4.0 编写，项目仓库：[GitHub](https://github.com/weed33834/agentseed)（主仓库）· [Gitee](https://gitee.com/badhope/agentseed)（镜像）· [Gitcode](https://gitcode.com/badhope/agentseed)（镜像）
>
> 更多信息请参阅 [README.md](../README.md) 和 [AGENTSEED_ARCHITECTURE.md](AGENTSEED_ARCHITECTURE.md)。
*（内容由AI生成，仅供参考）*
