# Git 提交规范 (Git SOP)

> 小说创作仓库的 Git 规范。稿件也是代码——版本管理是创作安全的基础。

## 提交信息格式

```
<type>(<scope>): <subject>

<body>
```

### type
| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新增内容/功能 | 新增第 3 章初稿 |
| fix | 修复问题 | 修复第 2 章角色 A 的 OOC |
| refactor | 重构/重写 | 重写第 5 章对话段落 |
| docs | 文档变更 | 更新角色档案 |
| chore | 杂项 | 更新 .gitignore |

### scope
- 章节号：`ch3`, `ch5`
- 模块名：`characters`, `worldbuilding`, `plot`
- 工具：`sync`

### 示例
```
feat(ch3): 新增第三章初稿——主角首次遭遇反派

- 场景：废弃仓库对峙
- 新出场角色：反派"灰鸦"
- 伏笔：灰鸦左手缺失（待回收）
- 字数：~3500
```

## 分支策略
- `main`：稳定版本，每次合并前确认稿件完整性。
- `draft/chN`：第 N 章草稿分支。
- `fix/issue-description`：修复特定问题的分支。

## 禁止事项
- 绝不自动 `git push`。
- 绝不 `git push -f` 到 main。
- 绝不 `git add .`（必须逐个确认）。
- 绝不提交 `.env` 文件。
- 绝不提交 `.ai-memory/` 中的敏感创作数据（如包含真实人物原型的角色档案）。
