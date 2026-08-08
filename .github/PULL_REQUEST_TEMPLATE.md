## 改动类型
- [ ] **新场景包**（`personas/<id>/`，填下方"场景包贡献"区）
- [ ] 规则源头（core/ 或 场景包 AGENTS.md）有改动
- [ ] 仅文档（README / 说明）
- [ ] 新增文件（模板 / 治理文件）
- [ ] 其他：

## 场景包贡献（新增/修改场景包时填写）
- **包 ID / 分类**：`<id>` / `general|dev|creative|research|strategic`
- **适用场景**：一句话说明
- **校验**：已运行 `python scripts/validate_packs.py` 且通过
- **装配验证**：已运行 `agentseed forge --profile <id>` 且产物无 `[missing]`
- [ ] 互斥清单对称；能力引用存在；无硬编码密钥；不含 `.git`

## 是否动了规则源头
- [ ] 是，已编辑源文件（core/ 或 personas/<id>/）并运行 `python scripts/sync_rules.py` 重生成工具文件
- [ ] 否

## 同步校验
- [ ] 已确认 `CLAUDE.md` / `GEMINI.md` / `.cursor/rules/project.mdc` / `.github/copilot-instructions.md` / `.trae/rules/project_rules.md` 由脚本生成，未手工修改

## 多语言 README
- [ ] 三语言 README（中/英/日）已同步更新
- [ ] 本次未涉及 README 内容

## 验证方式
（描述你如何验证规则生效，例如注入某工具后询问约束）

## 自查
- [ ] `git status` 无意外文件
- [ ] 无 Token / 密钥硬编码
- [ ] MCP 相关仅改说明，无自动下载/启动指令
