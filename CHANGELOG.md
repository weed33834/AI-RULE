# Changelog

## [1.0.0] — 2026-08-08

AgentSeed 首个正式版本。此前内部迭代（2.x / 1.x 实验版本）已整合归档，全部能力收口到 1.0.0。

### 产品定位（v1.0.0 起）

面向自主智能体的高约束规则治理框架：**治理内核（不可协商）+ 场景规则包（可插拔）+ 三注册表（场景/能力/平台）**。一次装配，15 个智能体工具同步生效。

### Added
- 千问办公 (QwenWork) 注册为第 15 个内置平台：`qwenwork`（entry=AGENTS.md，与 agents-md 同源）。
- CLI `--json` 结构化输出：`list` / `forge` / `sync` / `status` / `platform list` / `persona list` 支持 `--json`，UTF-8 纯净流，供脚本与 Agent 直接消费。
- MCP Server HTTP 传输（`agentseed serve --port N`）：stdlib 实现 `POST /mcp`（JSON-RPC）+ `GET /healthz`。
- MCP 场景规则包别名工具：`scenario_list` / `scenario_activate`（`persona_*` 保留兼容）。
- 场景规则包清单规范 `docs/SCENARIO_PACK_SPEC.md` + 校验器 `scripts/validate_packs.py`（manifest 结构/引用完整性/能力有效性/互斥对称性，防 forge 产物 [missing]）。
- 对外术语统一为"场景规则包 (Scenario Pack)"：README/PROJECT/架构文档重写定位；CLI 文案、MCP 工具描述同步；命令名与 JSON 字段保持兼容。
- 场景包目录双路径兼容：资源根探测与包目录解析支持 `scenarios/`（优先）与 `personas/`（回退）。
- `docs/PUBLISH.md`：PyPI（计划）/ MCP 注册表与市场 / Homebrew / Docker 的分发提交指南。

### Fixed
- **MCP Server 资源根解析**：wheel 安装下资源根指向错误层级，导致 `persona_list` 返回空、`governance_check` 报 "No P0 constraints loaded"。按 `AGENTSEED_REPO → <pkg>/_resources → dev 仓库根` 三级回退，wheel 安装开箱即用。
- **governance_check 工具名无关匹配**：破坏性操作/密钥/MCP 自装检查不再要求特定工具名，从任意工具参数中递归提取命令字符串匹配。
- **Windows 中文环境编码**：stdio/HTTP 启动强制 stdout/stderr 为 UTF-8，CLI `--json` 输出同样强制 UTF-8。
- **场景协议源文件缺失（基线缺陷）**：6 个 `personas/<id>/AGENTS.md` 此前被 `.gitignore` 无锚定规则静默忽略、从未入库，导致 forge 产物出现 `[missing]` 标记。已补全 6 份源文件并把 `.gitignore` 锚定为 `/AGENTS.md`（根级生成文件）。
- coding 包 manifest 补 `agent_mode` 声明。

### Infrastructure
- GitHub Releases 清理历史 2.x 版本，v1.0.0 作为唯一正式发布（wheel 随 Release 分发）。
- 全量测试：162 passed / 1 skipped（此前 151 passed + 5 基线失败）。

## 历史版本

- 2.4.1 / 2.3.0 / 2.0.0 / 1.4.0 ~ 1.0.0（2026-07 内部迭代）：已整合至 1.0.0，不再单独维护。
