# 贡献指南

本仓库是一套**通用 AI 协作规则模板**。`AGENTS.md` 是所有规则的**唯一源头**，其余工具配置文件由同步脚本生成，请勿手工修改。

## 改动流程（必须遵守）

1. **只编辑 `AGENTS.md`**。任何规则、约束、红线的增删改，都先在 `AGENTS.md` 里完成。
2. 运行同步脚本，自动重生成工具文件：

   ```bash
   python scripts/sync_rules.py
   ```

   脚本会把 `AGENTS.md` 中的 `@引用` 内联展开，重新生成 `CLAUDE.md`、`GEMINI.md`、`.cursor/rules/project.mdc`、`.github/copilot-instructions.md`、`.trae/rules/project_rules.md`。
3. 提交时**不要手工改动** `CLAUDE.md` / `GEMINI.md` / `.cursor/rules/project.mdc` / `copilot-instructions.md` / `.trae/rules/project_rules.md` —— 它们由脚本生成，手改会被下次同步覆盖，并造成源头与派生文件不一致。

## 多语言 README

`README.md`（英文，默认）、`README_CN.md`（中文）、`README_JA.md`（日文）内容需保持一致。改动其中一份的说明性内容时，请同步另外两份；若暂时只改英文，在 PR 描述里注明「CN/JA 待补」。

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
