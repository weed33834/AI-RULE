# 贡献指南

本仓库是 **AgentSeed — AI Agent 人格治理平台**。规则源文件位于 `core/`、`personas/<id>/`、`capabilities/<cap>/`，平台入口文件（AGENTS.md / CLAUDE.md 等）由 `agentseed sync` 生成，请勿手工修改。

## 快速上手

```bash
# 一键装配：自动检测环境 → 路由画像 → 生成平台文件
agentseed forge

# 查看状态 / 验证 / 同步
agentseed status
agentseed verify
agentseed sync
```

## 改动流程（必须遵守）

1. **只编辑规则源文件**（`core/`、`personas/<id>/`、`capabilities/<cap>/`）。`AGENTS.md` / `CLAUDE.md` 等平台文件由同步脚本生成，请勿手工修改。
2. 运行同步脚本，自动重生成工具文件：

   ```bash
   python scripts/sync_rules.py
   # 或等价 CLI：
   agentseed sync --profile <id>
   ```

   脚本会把规则源内联展开，重新生成 `CLAUDE.md`、`GEMINI.md`、`.cursor/rules/project.mdc`、`.github/copilot-instructions.md`、`.trae/rules/project_rules.md` 等 13 个平台入口文件。
3. 提交时**不要手工改动**生成产物（`CLAUDE.md` / `GEMINI.md` / `.cursor/rules/` / `copilot-instructions.md` / `.trae/rules/` 等）——它们由脚本生成，手改会被下次同步覆盖，并造成源头与派生文件不一致。

## 多语言 README

`README.md`（英文，默认）、`README.zh.md`（中文）、`README.ja.md`（日文）内容需保持一致。改动其中一份的说明性内容时，请同步其他两份；若暂时只改英文，在 PR 描述里注明「zh/ja 待补」。

## 目录结构与新画像开发

```
core/                  # P0 宪法层（不可插拔）
personas/<id>/         # 画像包：persona.yaml + prompts/ + skills/ (+ templates/)
capabilities/<cap>/    # 能力包：cap.yaml + prompt.md (+ mcp.json)
adapters/              # 平台适配器
src/agentseed/         # Python 实现（CLI/同步/路由/装配/自进化）
tests/                 # pytest 套件
```

新增画像：复制 `personas/_template/default/` 脚手架 → 填写 `persona.yaml`（含 `includes` / `enables_capabilities` / `activation_anchors` / `intent_keywords`）→ 在 `src/agentseed/router.py` 的 `PERSONAS` 注册表登记锚点与关键词 → 运行 `agentseed verify` 验证。

## 运行时资源

v2 重构后，`skills/` 与 `mcp/` 顶层目录已融入各画像（`personas/<id>/skills/`）与能力包（`capabilities/<cap>/`）。修改画像内技能文件后直接提交即可，无需重跑同步脚本。

## 提交规范

使用 Conventional Commits：

- `feat:` 新增规则或文件
- `fix:` 修正错误
- `docs:` 文档变更
- `refactor:` 结构调整
- `chore:` 杂项

示例：`feat(rules): 新增失败熔断条款`。

## 提交前自查

- `git status` 确认没有意外文件（如 `.workbuddy/`、`.bak`、`.env`）。
- 不在源码或配置里硬编码任何 Token / 密钥；一律用环境变量。
- MCP 相关变更只改说明文本，**绝不添加自动下载或自启动指令**（见 `core/governance.md` MCP 红线）。

## 提 PR

按 `.github/PULL_REQUEST_TEMPLATE.md` 填写，说明是否动了 `AGENTS.md` 源头、是否重跑同步、验证方式。
