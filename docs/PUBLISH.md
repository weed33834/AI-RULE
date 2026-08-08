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

> ⚠️ 更新（2026-08-08）：Registry **不接受 PR 提交**，必须用官方 `mcp-publisher` CLI。
> 且 PyPI 类型的所有权校验 = 检查 **pypi.org 上已发布包**的 README 是否含 `mcp-name: io.github.weed33834/agentseed`。
> 因此正式提交**依赖 PyPI 先上线**（见 §3）。当前已备好：
> - `mcp/server.json`：Registry 当前 schema（2025-12-11，`packages[].registryType: pypi`，reverse-DNS 命名）
> - README.md 已埋所有权令牌 `<!-- mcp-name: io.github.weed33834/agentseed -->`

PyPI 上线后的提交步骤：

```bash
# 1. 安装 mcp-publisher（Windows PowerShell）
$arch = if ([System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture -eq "Arm64") { "arm64" } else { "amd64" }
Invoke-WebRequest -Uri "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_windows_$arch.tar.gz" -OutFile "mcp-publisher.tar.gz"
tar xf mcp-publisher.tar.gz mcp-publisher.exe; rm mcp-publisher.tar.gz

# 2. 认证（GitHub token）
$env:GITHUB_TOKEN = "<fine-grained token>"

# 3. 提交 server 元数据（在仓库根执行）
mcp-publisher publish --file mcp/server.json
```

通过后，任何 MCP 客户端/聚合器可通过注册表 API 发现本 server。

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
