# Tool / Skill / MCP：三者关系与落地结构

> 改写自项目架构设计。核心目的：让 AI 清楚「什么该自己干、什么该读说明书、什么必须交给你配」。

## 一句话区分

| 概念 | 比喻 | 谁提供 | 谁负责启动 | 本质 |
|------|------|--------|------------|------|
| **Tool** | 手和脚 | AI 内置 | AI 内置 | 开箱即用的能力（Terminal、文件读写…） |
| **Skill** | 菜谱 | 本仓库 `docs/skills/` | 你读即可 | 教 AI 做复杂事的文本 / SOP |
| **MCP** | 输血管 | 外部系统 | **你手动** | 常驻后台、直连外部系统的服务 |

## Tool（手和脚）

内置工具（Terminal、Read、Edit、Grep、Glob、WebFetch…）不需要任何安装，AI 直接调用。
**Skill 的落地必须靠 Tool 执行**——没有 Tool，AI 读了 Skill 也执行不了。
因此本仓库不把 Tool 列册，只在 `AGENTS.md` 的 Coding Standards 里约束怎么用好它们。

## Skill（菜谱）

`docs/skills/` 下的文本 / 脚本，把「复杂但可复用」的事沉淀成 SOP：

- `registry.md`：经审核的工具白名单 + 受限搜索协议
- `git-sop.md`：Git 提交规范
- `powershell-tips.md`：Windows 下 PowerShell 语法要点
- `mcp-registry.md`：可手动接入的 MCP 清单

AI 按需读取，但**不自动执行未知脚本**——下载来的 `.ps1/.py/.sh` 必须先隔离审查（见 `AGENTS.md` § Engineering Hygiene 与 Skill Acquisition Protocol）。

## MCP（输血管）

MCP 让 AI 标准化直连外部系统，比临时拼命令行更稳更安全。但它：

- 需要常驻进程、环境变量、端口、权限；
- 启动权在你手里，**AI 只能给命令和 JSON 供你审阅后粘贴**。

红线与各工具配置路径见 `mcp-registry.md`。

## 三者如何协作（一次典型任务）

```
你下指令
  └─ AI 用 Tool 读 Skill（如 git-sop.md）了解规范
       └─ AI 用 Tool 执行具体动作（Terminal 跑 git、跑测试）
            └─ 若需直连外部系统，由你启动 MCP，AI 通过它安全调用
```

## 本仓库落地结构

```
AGENTS.md                      # 规则唯一源头（含 Tool/Skill/MCP 管理策略）
docs/prompts/system-prompt.md  # 英文 XML 系统提示词（含 <mcp_policy>）
docs/skills/
  ├─ registry.md               # 工具白名单 + 受限搜索协议
  ├─ git-sop.md                # Git 规范
  ├─ powershell-tips.md        # PowerShell 要点
  └─ mcp-registry.md           # 可手动接入的 MCP 清单
mcp.example.json              # MCP 配置示例模板（占位 token，各工具通用）
```

> 改规则只动 `AGENTS.md`，然后 `python scripts/sync_rules.py` 同步到各工具专属文件。
