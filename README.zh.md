# AgentSeed

> **`pip install https://github.com/weed33834/agentseed/releases/download/v2.4.1/agentseed-2.4.1-py3-none-any.whl && agentseed forge`**

**🌐 [English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md)**

**📦 [GitHub](https://github.com/weed33834/agentseed) (主站) · [Gitee](https://gitee.com/badhope/agentseed) · [Gitcode](https://gitcode.com/badhope/agentseed)**

![License](https://img.shields.io/badge/license-MIT-blue)
![Personas](https://img.shields.io/badge/personas-6-green)
![Platforms](https://img.shields.io/badge/platforms-14-orange)
![Tests](https://img.shields.io/badge/tests-143%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-informational)

---

每次开一个新的 AI 编程会话，前十分钟都在干同一件事：告诉它别幻觉、别跑 `rm -rf`、你的技术栈是什么。AgentSeed 把这件事做一遍，然后同步到你用的所有工具里。

一条命令检测你的项目类型，选好对应的"人设"，给你用的 Claude Code、Cursor、Copilot、Windsurf、Trae 全部生成好规则文件。

```bash
agentseed forge
```

就这一条。空目录进去，出来一个 1200 行的 AGENTS.md，包含安全规则、项目专属技能、各平台配置。不管你是在写代码、写小说、写论文、还是写另一个 agent，都一样用。

---

## 它能干什么

**安全底线不会丢。** 核心安全规则（禁止 `rm -rf`、禁止捏造密钥、禁止不经确认装东西）是写死在 AgentSeed 里的，换什么人设都覆盖不掉。

**六个预设人设，随时切。** `coding`（默认）、`novel`、`paper`、`conversation`、`interactive-novel`、`agent-builder`。每个自带提示词、技能列表、工具偏好。项目做到一半想换口味？`agentseed switch --profile novel`。

**14 个平台，一次同步。** 不同工具要不同格式，AgentSeed 自己搞定：
- Claude Code → `CLAUDE.md`
- Cursor → `.cursor/rules/project.mdc`
- Copilot → `.github/copilot-instructions.md`
- Windsurf → `.windsurfrules`
- Gemini → `GEMINI.md`
- Trae → `.trae/rules/project_rules.md`
- Cline → `.clinerules/project.md`
- Continue → `.continue/rules/project.md`
- Amazon Q → `.amazonq/rules/project.md`
- Qodo → `best_practices.md`
- 通义灵码 → `.lingma/rules/project.md`
- 腾讯云代码助手 → `.comate/rules/project.mdr`
- Codex → `.codex/rules.md`
- AGENTS.md（20+ 工具原生读取）

**每个平台都有拦截钩子。** `adapters/hooks/` 下 14 个平台的 `pre_tool_use.py`，在危险操作执行前拦截。fail-open 设计：钩子崩了操作照常，不会误伤。

**MCP Server。** `agentseed serve` 启动，任何支持 MCP 的客户端可以直接调用 `governance_check`（安全红线检查）、`persona_list`（人设列表）、`persona_activate`（切换人设）、`gap_detect`（能力缺口检测）。

**自进化。** AgentSeed 会给你的项目打分——缺什么工具、哪些领域不懂——然后告诉你该装什么。不是魔法，就是一个加权公式，你装的能力越多它建议越准。

---

## 安装

```bash
pip install https://github.com/weed33834/agentseed/releases/download/v2.4.1/agentseed-2.4.1-py3-none-any.whl
```

源码安装：

```bash
git clone https://github.com/weed33834/agentseed.git
cd agentseed
pip install -e .
```

国内网络慢的话用 Gitee 镜像：

```bash
git clone https://gitee.com/badhope/agentseed.git
```

---

## 常用命令

```bash
agentseed forge              # 检测项目 → 装配 → 生成
agentseed forge --dry-run    # 预览，不写文件
agentseed forge --profile coding
agentseed forge --profile novel

agentseed switch --profile paper

agentseed sync               # 同步到所有平台
agentseed sync --platform cursor

agentseed status             # 看看装了啥、缺啥

agentseed serve              # 启动 MCP server (stdio)
agentseed serve --port 8080  # 启动 MCP server (HTTP)

agentseed platform list      # 14 个内置平台
agentseed platform import my-ide --entry .myide/rules.md --format markdown

agentseed persona list       # 当前所有人设
agentseed persona search "产品经理"
```

---

## 接入你自己的平台

```bash
agentseed platform import my-editor --entry .myeditor/rules.md --format markdown --hook-dir .myeditor
```

一步注册平台 + 生成拦截钩子 + 纳入每次 `agentseed sync`。

---

## 目录结构

```
core/                  安全底线（P0 红线、决策公式、路由规则）
personas/              各人设独立目录（coding、novel、paper...）
capabilities/          模块化能力包（testing、research、creative...）
adapters/hooks/        各平台的工具拦截钩子
src/agentseed/         CLI、同步引擎、路由、装配、自进化
```

---

## 跟同类项目比

- **agent-rules (steipete)** — 已归档，只做 Cursor 编码规则。
- **agents.md** — 文件格式提案，只有格式没内容没工具链。
- **ACP** — agent 配置管理器，没治理没自进化。
- **Cursor Directory** — 社区规则片段合集，不支持多平台同步。
- **AgentSeed** — 安全规则 + 六种人设 + 14 平台同步 + 拦截钩子 + 自进化，一个 CLI 全包。

---

## 参与开发

看 [CONTRIBUTING.md](CONTRIBUTING.md)。简单说：改源文件（`core/`、`personas/`、`capabilities/`）→ 跑 `agentseed sync` 重生成平台文件 → 别手动改生成产物。

跑测试：`python -m pytest tests/`（143 通过）。

---

MIT
