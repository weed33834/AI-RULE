# Git 提交规范 (Git SOP)

> AI 提交前必须遵循；提交前先 `git status` 确认无冗余文件。

## 提交前检查

1. `git status`：确认没有把临时文件、外部 `.git`、无关文件（LICENSE / README / `.github`）带进来。
2. `git diff`：确认改动符合本次意图，没有夹带。
3. 不提交密钥：`.env`、token、凭证一律排除（仓库已配 `.gitignore`）。

## 提交粒度

- 一次提交只做一件事，便于回溯与 revert。
- 禁止 `git add -A` 无脑全加；用 `git add <具体文件>` 精确添加（避免误带 `.workbuddy/` 等）。

## Commit Message

采用 Conventional Commits（中英文均可，保持项目一致）：

```
<type>(<scope>): <subject>
```

- `feat`：新功能
- `fix`：修复
- `docs`：文档
- `refactor`：重构（非功能变更）
- `chore`：杂项（同步脚本等）

示例：`feat(rules): 新增 Tool/Skill/MCP 管理策略`

## 分支与推送

- 主分支通常为 `main`，不随意 `force push`。
- 推送前确认本地领先的提交都是你想要的（`git log origin/main..HEAD`）。

## 安全删除

- 删除文件用 `send2trash`（送回收站），不要直接 `rm -rf`。
- 确需彻底删除前，先确认无进程占用。
