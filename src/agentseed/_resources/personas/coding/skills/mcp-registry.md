# MCP 服务注册表 (MCP Registry)

> ⚠️ **红线**：MCP 是常驻后台服务，涉及环境变量、端口、权限。**AI 禁止自下载、自安装、自启动、自配置 MCP**。
> 本文件只列出「经过筛选、可放心手动接入」的 MCP 服务，供你在各 AI 工具（Trae / Claude Desktop / Cursor / VS Code 等）里手动配置时参考。
> 配置权永远在你（用户）手里。

## MCP 是什么

MCP（Model Context Protocol）让 AI 通过标准化协议直连外部系统（数据库、GitHub、Notion、文件系统）。
它像一条「输血管」：高频、稳定的外部对接用 MCP 比 AI 临时拼命令行更可靠、更安全。
但 MCP 需要你手动在各 AI 工具的 MCP 设置里启动，AI 只能给出安装命令与配置 JSON 供你审阅。

## 使用原则

1. 仅从下表挑选经过筛选的服务，不随意接入未知 MCP。
2. Token / 密钥一律用环境变量（如 `${GITHUB_TOKEN}`）注入，不得硬编码进仓库。
3. 配置 JSON 由你手动粘贴到对应工具的 MCP 配置文件（路径见下方「配置位置」）；AI 不代你写入或启动。

## 推荐清单（手动配置参考）

| 服务 | 用途 | 官方源 | 接入方式 |
|------|------|--------|----------|
| GitHub MCP | 仓库 / Issue / PR 操作 | github/github-mcp-server | npx 启动，需 `GITHUB_TOKEN` |
| Filesystem MCP | 受控目录文件读写 | modelcontextprotocol/servers | stdio，限定根目录 |
| SQLite / Postgres MCP | 本地 / 远程数据库查询 | modelcontextprotocol/servers | stdio，需连接串 |
| Puppeteer / Playwright MCP | 浏览器自动化 | microsoft 官方 | npx 启动 |
| Notion MCP | Notion 读写 | makenotion/notion-mcp-server | 需 `OPENAPI_MCP_HEADERS` |

> 上表为「可信来源」示例，具体到某个服务请以官方文档为准。新增任何 MCP 前先确认其来源可信、代码开源可审阅。

## 配置位置（各工具通用）

本仓库的 MCP 示例模板为根目录 `mcp.example.json`（占位 token，各工具格式通用）。把它对应到你所用的工具即可：

| 工具 | 配置文件路径 |
|------|--------------|
| Trae | `.trae/mcp.json` |
| Claude Desktop | `claude_desktop_config.json` |
| Cursor | `.cursor/mcp.json` |
| VS Code | `.vscode/mcp.json`（或 settings.json 的 `mcp` 字段） |

三者关系与本仓库落地结构见 `tool-skill-mcp.md`。
