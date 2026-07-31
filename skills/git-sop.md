---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 98adaa6f98486df4666888a6691e7607_b7be6714883611f18766525400f8a581
    ReservedCode1: 5AxsopqcbXA03TCtTI/xhPzj1THmy/JLUbeSD6tUwxo9cR6DeCkPV/3i+yCAndbBl3m7f6ibsTZ4JbWumZD6kXLqz1ON6gNqvP5vkbjfgdGds2n4YQe378IvGL2r6EE/Wsvm38FE3rjQfLjLd6K9SofEeLK1RsM/XDMuY3v/atROGFUghHS5CREvCe0=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 98adaa6f98486df4666888a6691e7607_b7be6714883611f18766525400f8a581
    ReservedCode2: 5AxsopqcbXA03TCtTI/xhPzj1THmy/JLUbeSD6tUwxo9cR6DeCkPV/3i+yCAndbBl3m7f6ibsTZ4JbWumZD6kXLqz1ON6gNqvP5vkbjfgdGds2n4YQe378IvGL2r6EE/Wsvm38FE3rjQfLjLd6K9SofEeLK1RsM/XDMuY3v/atROGFUghHS5CREvCe0=
---

# Git SOP — 版本控制标准操作协议

> **触发条件**：任何 `git commit` / `push` / `pull` / `merge` / `rebase` 操作。
> **加载时机**：Agent 在执行任何 Git 写操作（commit, push, force push, merge, rebase）之前必须加载本 Skill。
> **优先级**：P1（与 core/governance.md §7 工程卫生联动）。

---

## 1. 提交前检查（Pre-Commit Checklist）

### 1.1 环境检查

```bash
git status
```

| 检查项 | 判断标准 | 异常处理 |
|--------|----------|----------|
| 临时文件 | 无 `*.tmp`, `*.bak`, `*.zip`, `*.log` 出现在 untracked | 立即清理或加入 `.gitignore` |
| 外部 `.git` 目录 | 无嵌套 `.git/` 被追踪 | 立即排除（core/governance.md §7） |
| 无关文件 | 无 `LICENSE`, `README.md`（非本项目）, `.github/` | 除非用户明确要求，否则排除 |
| 凭证泄露 | 无 `.env`, `token`, `password`, `secret` | P0 违规，立即阻止提交 |

### 1.2 差异审查

```bash
git diff          # 查看工作区改动（未暂存）
git diff --cached  # 查看暂存区改动
```

- 确认改动范围与本次意图一致，无夹带。
- 发现意外改动（如自动格式化、调试代码残留）→ 先 `git stash` 隔离再处理。

### 1.3 分支状态

```bash
git log origin/<branch>..HEAD --oneline  # 查看本地领先但未推送的提交
```

- 确认每个领先提交都是本次意图范围内的。

---

## 2. 提交操作

### 2.1 暂存原则

```
禁止 git add -A 或 git add .
必须 git add <具体文件路径>
```

- 逐文件添加，每次 `git add` 后确认文件列表与预期一致。
- 必须显式列出 `git add` 的每个文件，让用户可审计。

### 2.2 Commit Message 规范

采用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

| Type | 含义 | 场景 |
|------|------|------|
| `feat` | 新功能 | 新增文件、新增 API、新增模块 |
| `fix` | 修复 | Bug 修复 |
| `docs` | 文档 | 只改文档（README、Skill、规范文件） |
| `refactor` | 重构 | 不改功能、只改代码结构 |
| `chore` | 杂项 | 同步脚本、依赖更新、构建配置 |
| `test` | 测试 | 仅新增或修改测试 |
| `style` | 格式 | 格式化、代码风格、缺失分号等 |
| `perf` | 性能 | 性能优化 |

**约束**：
- subject 用祈使句（"add" 而非 "added"）
- scope 用小写、连字符分隔
- 中英文均可，保持项目一致

**示例**：
```
feat(rules): add git-sop skill for standardized version control
fix(parser): handle empty CSV rows gracefully
docs(skills): add five-roles workflow documentation
```

---

## 3. 推送操作

### 3.1 推送前确认

```bash
git log origin/<branch>..HEAD --oneline
```

逐条确认本地提交，确保：
- 无调试/实验性提交混入
- 无敏感信息
- 提交信息清晰可回溯

### 3.2 拒绝操作

以下操作**必须获得用户明确确认**后才可执行：

| 操作 | 风险 | 引用 |
|------|------|------|
| `git push --force` | 覆盖远程历史 | core/governance.md §3 澄清优先 |
| `git push --delete` | 删除远程分支 | core/governance.md §3 澄清优先 |
| `git reset --hard` | 丢弃本地改动 | core/governance.md §3 澄清优先 |
| `git rebase`（主分支） | 重写共享历史 | core/governance.md §3 澄清优先 |

### 3.3 安全保护

- 主分支 `main` / `master` 禁止 `force push`（除非用户明确授权且已备份）。
- 推送前自动检查 `.env` 等敏感文件是否在暂存区。

---

## 4. 合并操作

### 4.1 Merge

```bash
git merge <source-branch> --no-ff   # 保留分支历史
```

- 合并前 `git fetch origin` 确保远程最新。
- 冲突时暂停，列出冲突文件路径，等待用户指定解决策略。

### 4.2 Rebase

```bash
git rebase <target-branch>
```

- 仅限个人分支（feature / fix 分支），不在共享分支上 rebase。
- Rebasing 前建议 `git checkout -b backup/<branch>` 创建备份分支。

---

## 5. 安全删除

| 操作 | 工具 | 说明 |
|------|------|------|
| 删除本地文件 | `send2trash` / `git rm` | 送入回收站或 Git 追踪内删除 |
| 永久删除 | 先确认无进程占用 | 需用户明确确认 |
| 批量清理 | `git clean -n` 先预览 | `-n` dry-run 后再 `-f` 执行 |

---

## 6. 完整执行流程

```text
git status
  ├─ 发现脏文件 → 清理或排除
  └─ 干净
      ↓
git diff / git diff --cached
  ├─ 意外改动 → git stash 隔离
  └─ 符合预期
      ↓
git add <file1> <file2> ...  （具体文件，非 -A）
      ↓
git commit -m "<type>(<scope>): <subject>"
      ↓
[可选] git log origin/<branch>..HEAD --oneline
      ↓
git push
```

---

## 7. 交叉引用

| 引用 | 内容 |
|------|------|
| `core/governance.md §7` | 工程卫生：禁止嵌套 .git、清理临时文件、提交前 git status |
| `core/governance.md §3` | 澄清优先：高风险操作前必须确认 |
| `core/governance.md §1` | 安全与保密：不提交密钥、.env 在 .gitignore |
| `core/governance.md §4` | 变更范围：仅提交指定文件的改动 |

---

## 8. 失败恢复

- Push 被拒绝（non-fast-forward）→ 执行 `git fetch origin` + `git status`，分析差异后向用户报告，**不自动 rebase 或 force push**。
- 合并冲突 → 列出冲突文件路径和冲突片段，等待用户指定策略（ours/theirs/手动编辑）。
- 提交后发现敏感信息 → 立即 `git reset HEAD~1` 清除该提交，替换敏感内容后重新提交。
*（内容由AI生成，仅供参考）*
