# AgentSeed 分发与提交指南（PUBLISH.md）

> 状态：v1.0.0 已发布（GitHub Releases + wheel）。
> 原则：**CLI 完整可用是底线**（`pip install <wheel> && agentseed forge` 一条命令跑通）；MCP 走"材料齐备 + 各市场提交 + 用户可手动导入"；PyPI 按计划后置。

---

## 1. 已上线（v1.0.0）

- **GitHub Releases**：v1.0.0 唯一正式版本，wheel 随 Release 分发。
  `https://github.com/weed33834/agentseed/releases/download/v1.0.0/agentseed-1.0.0-py3-none-any.whl`
- **自动构建**：`.github/workflows/release.yml` —— 打 tag 自动 build wheel + 附到 Release。
- 历史 2.x/1.x release 与 tag 已清理。

## 2. MCP 分发（进行中）

### 2.1 官方 Registry（modelcontextprotocol/registry）

1. 仓库已备好 `mcp/server.json`（reverse-DNS 命名 `io.github.weed33834/agentseed`）。
2. 提交方式：Fork `modelcontextprotocol/registry` → 在 `servers/io.github.weed33834/agentseed/server.json` 放置 → PR。
3. 命名空间校验：注册表会用 GitHub 账号/域名验证所有权（本仓库 GitHub 账号即为 weed33834，无需额外验证）。
4. 通过后，任何 MCP 客户端/聚合器可通过注册表 API 发现本 server。

### 2.2 下游市场（聚合器，重点投）

| 市场 | 地址 | 提交方式 |
|---|---|---|
| Smithery | smithery.ai | 账号注册后 "Add Server"，填 git 仓库地址，自动扫描 |
| PulseMCP | pulsemcp.com | 提交表单（name/description/command/args） |
| mcp.so | mcp.so | 提交表单或 API（支持国内访问，重点） |
| Glama | glama.ai | 填仓库 URL 自动收录 |
| mcpcn（中文） | mcpcn.com | 中文站提交表单（国内开发者主入口，重点） |
| agentlist.top（中文） | agentlist.top | 提交收录 |

> 各市场仅需要：名称、一句话描述、`command: agentseed`、`args: [serve]`、仓库链接。
> 无需收入与 API Key；用户在任何 MCP 客户端搜到后即可**手动导入**：
> ```json
> { "mcpServers": { "agentseed": { "command": "agentseed", "args": ["serve"] } } }
> ```

### 2.3 手动导入（已就绪）

- 客户端配置指南：`docs/INTEGRATION.zh.md` §5（含千问办公 §5.10、Claude Desktop、Cursor、Cline、Windsurf、Continue、Gemini CLI、Codex、Trae、Claude Code）。
- Windows 注意：`agentseed` 不在 PATH 时 `command` 用绝对路径（如 `python -m agentseed.cli`）。

## 3. PyPI（计划中，暂不发布）

按产品决策后置。上线时：
1. 取消 `.github/workflows/release.yml` 中 publish job 的注释。
2. 在 GitHub 仓库 Settings → Environments 配置 `pypi`（trusted publishing 或 `PYPI_API_TOKEN`）。
3. 首次发布：`python -m build` → `twine upload dist/*.whl`（或直接用 CI）。

## 4. 其他渠道（计划）

- **Homebrew**：提供 formula（tap 或 core），`brew install agentseed`。
- **Scoop**：Windows manifest，`scoop install agentseed`。
- **Docker**：HTTP 模式镜像（`agentseed serve --port 8080`），供远程治理调用。

## 5. 版本策略

- 首个正式版 v1.0.0（已发布）。
- 小修改：patch/minor 递增（`v1.0.1`、`v1.1.0`），打 tag 即自动发布。
- 大修改：仅当用户明确要求时升 major。
