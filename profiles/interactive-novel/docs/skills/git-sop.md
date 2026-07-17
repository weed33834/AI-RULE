# Git 标准操作流程（Git SOP）

> 本文档为互动小说游戏引擎的版本控制定义标准操作流程，涵盖提交前检查、分支管理、提交信息格式、推送确认、冲突解决和版本标签管理，确保代码变更安全可追溯。

## 1. 总则

### 1.1 核心原则

| 原则 | 说明 |
|------|------|
| 安全第一 | 绝不自动 push，绝不 push -f，绝不盲目 add . |
| 可追溯 | 每次变更都有清晰的提交信息和上下文 |
| 先查后做 | 任何 Git 操作前必须先查看状态和差异 |
| 最小变更 | 每次提交只包含逻辑相关的变更，不混杂无关修改 |

### 1.2 前置要求

执行 Git 操作前必须：

1. 检测当前操作系统（`uname -a` 判断 Linux/macOS，`$PSVersionTable` 判断 Windows）。
2. Windows 环境使用 PowerShell 语法，Linux/macOS 使用 Bash 语法。
3. 确认当前工作目录是项目根目录。
4. 阅读本文件了解操作规范。

## 2. 提交前检查

### 2.1 强制检查流程

每次提交前必须执行以下检查，缺一不可：

```text
提交前检查流程：

第一步：查看工作区状态
  $ git status
  → 确认哪些文件被修改/新增/删除

第二步：查看具体差异
  $ git diff           # 查看未暂存的修改
  $ git diff --cached  # 查看已暂存的修改
  → 逐行确认变更内容是否符合预期

第三步：确认无敏感信息
  → 检查差异中是否包含 API Key、密码、Token
  → 检查是否包含 .env、密钥文件等敏感文件
  → 检查是否包含游戏存档中的玩家隐私数据

第四步：确认变更范围
  → 变更是否逻辑相关（不混杂无关修改）
  → 是否有意外的自动生成文件被包含
  → .game-state/ 下的运行时文件是否被误提交

第五步：选择性暂存
  $ git add <具体文件>   # 逐个添加，不用 git add .
  → 只暂存经过检查的文件
```

### 2.2 禁止的暂存操作

```text
禁止的 git add 模式：

[禁止] git add .              — 盲目添加所有文件
[禁止] git add --all           — 同上，包含删除
[禁止] git add *.json          — 通配符批量添加
[禁止] git add .game-state/    — 添加运行时状态文件

正确做法：
  git add docs/skills/dialogue-system.md
  git add AGENTS.md
  → 逐个文件添加，确保每个都经过检查
```

### 2.3 .gitignore 配置

以下文件/目录必须在 `.gitignore` 中排除，不得提交：

```text
# .gitignore 必须包含：

# 游戏运行时状态（每个游戏会话独立，不入库）
.game-state/
.game-saves/

# 临时工作文件
/data/user/work/
*.tmp
*.bak

# 敏感配置
.env
.env.*
secrets.*
*.key
*.pem

# 系统文件
.DS_Store
Thumbs.db
__pycache__/
*.pyc
```

## 3. 分支管理策略

### 3.1 分支模型

采用简化的 Git Flow 模型：

| 分支类型 | 命名规范 | 用途 | 生命周期 |
|----------|----------|------|----------|
| main | main | 生产分支，稳定版本 | 永久 |
| develop | develop | 开发集成分支 | 永久 |
| feature | feature/<描述> | 新功能开发 | 合并后删除 |
| fix | fix/<描述> | 缺陷修复 | 合并后删除 |
| docs | docs/<描述> | 文档更新 | 合并后删除 |

### 3.2 分支命名示例

```text
分支命名示例：

feature/add-combat-system     — 新增战斗系统
feature/npc-emotion-model     — NPC 情感模型
fix/dialogue-info-leak        — 修复对话信息泄露
fix/inventory-stack-bug       — 修复物品堆叠 bug
docs/update-skill-docs        — 更新技能文档
docs/add-security-checklist   — 新增安全检查清单
```

### 3.3 分支操作规范

```text
分支操作规范：

创建分支：
  $ git checkout -b feature/<描述> develop
  → 从 develop 分支创建新分支

切换分支：
  $ git checkout <分支名>
  → 确认切换前工作区干净（git status 无未提交变更）

合并分支：
  $ git checkout develop
  $ git merge --no-ff feature/<描述>
  → 使用 --no-ff 保留分支历史
  → 合并后删除已合并的分支

删除分支：
  $ git branch -d feature/<描述>
  → 仅删除已合并的分支
  → -D 强制删除仅用于确信不需要的分支
```

### 3.4 分支保护规则

| 分支 | 保护规则 |
|------|----------|
| main | 禁止直接 push，只能通过 PR 合并；禁止 force push |
| develop | 禁止 force push；建议通过 PR 合并 |
| feature/fix/docs | 创建者可自由操作；合并后删除 |

## 4. 提交信息格式

### 4.1 格式规范

提交信息遵循约定式提交（Conventional Commits）格式：

```text
提交信息格式：

类型(范围): 描述

[可选] 详细说明正文

[可选] 脚注（如 BREAKING CHANGE）
```

### 4.2 类型清单

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | feat(combat): 新增战斗系统伤害计算 |
| fix | 缺陷修复 | fix(dialogue): 修复 NPC 信息泄露问题 |
| docs | 文档变更 | docs(skills): 新增安全检查清单文档 |
| style | 代码格式（不影响功能） | style(format): 统一缩进为 2 空格 |
| refactor | 重构（不改功能） | refactor(state): 重构状态文件校验逻辑 |
| perf | 性能优化 | perf(npc): 优化 NPC 记忆检索效率 |
| test | 测试相关 | test(dialogue): 新增对话系统测试用例 |
| chore | 构建/工具变更 | chore(deps): 升级 pip-audit 版本 |
| revert | 回退提交 | revert: 回退 feat(combat) 提交 |

### 4.3 范围（Scope）清单

| 范围 | 对应模块 |
|------|----------|
| combat | 战斗系统 |
| dialogue | 对话系统 |
| inventory | 物品系统 |
| npc | NPC AI 系统 |
| state | 游戏状态机 |
| narrative | 叙事引擎 |
| world | 世界模拟 |
| session | 会话管理 |
| skills | 技能文档 |
| prompts | 提示词文档 |
| security | 安全相关 |
| deps | 依赖管理 |

### 4.4 提交信息示例

```text
好的提交信息示例：

feat(dialogue): 新增说服/欺骗/威胁/贿赂判定机制

- 实现基于属性和好感度的综合判定公式
- 新增欺骗的后续验证机制
- 添加对话标签系统存储到 NPC 档案
- 关联文档: docs/skills/dialogue-system.md

---

fix(npc): 修复 NPC 跨区域知道未传播信息的问题

NPC 在无传播渠道情况下获知了玩家在其他区域的行为。
新增 knowledge 字段校验，对话前检查信息来源合法性。

---

docs(skills): 新增 7 个技能文档

新增 dialogue-system、inventory-system、security-checklist、
evolution-policy、path-scoped-rules、tool-skill-mcp、git-sop
共 7 个技能文档，完善引擎规则体系。
```

### 4.5 提交信息质量要求

| 要求 | 说明 |
|------|------|
| 描述用祈使句 | "新增..." 而非 "新增了..." |
| 描述不超过 50 字符 | 标题行简洁 |
| 正文换行说明 | 每条变更一行，用 - 开头 |
| 说明为什么 | 不仅说做了什么，还说明为什么 |
| 关联文档/issue | 有相关文档或 issue 时注明 |

## 5. 推送前确认流程

### 5.1 推送红线

```text
推送绝对禁止：

[禁止] git push — 自动推送（未经确认）
[禁止] git push -f — 强制推送（覆盖远程历史）
[禁止] git push --force-with-lease — 即使是安全强制推送也需确认
[禁止] git push 到非当前分支 — 必须明确指定目标分支
```

### 5.2 推送前确认流程

```text
推送前确认流程：

第一步：确认本地状态
  $ git status
  → 确认工作区干净，所有变更已提交

第二步：确认提交历史
  $ git log --oneline -5
  → 查看最近 5 条提交，确认提交信息正确

第三步：拉取远程更新
  $ git pull --rebase origin <分支名>
  → 先拉取远程变更，避免冲突

第四步：向用户确认
  → 告知用户即将推送的内容摘要
  → 等待用户明确确认（"确认推送"）
  → 未获确认绝不推送

第五步：执行推送
  $ git push origin <分支名>
  → 明确指定远程和分支
  → 推送后确认结果
```

### 5.3 推送确认示例

```text
推送确认对话示例：

AI: 即将推送到 origin/feature/add-combat-system
    包含 3 个提交：
    - feat(combat): 新增伤害计算公式
    - feat(combat): 新增战术选项系统
    - docs(skills): 更新战斗系统文档
    
    确认推送吗？

用户: 确认推送

AI: [执行 git push origin feature/add-combat-system]
    推送成功。远程分支已更新。
```

## 6. 冲突解决步骤

### 6.1 冲突检测

拉取或合并时出现冲突，Git 会标记冲突文件：

```text
冲突检测：

$ git pull --rebase origin develop
CONFLICT (content): Merge conflict in docs/skills/dialogue-system.md

→ 出现 CONFLICT 提示即表示有冲突需解决
```

### 6.2 冲突解决流程

```text
冲突解决流程：

第一步：查看冲突文件
  $ git status
  → 列出所有冲突文件（unmerged paths）

第二步：查看冲突内容
  打开冲突文件，查找冲突标记：
  <<<<<<< HEAD
  当前分支的内容
  =======
  传入分支的内容
  >>>>>>> branch-name

第三步：解决冲突
  → 逐个冲突点人工判断保留哪部分
  → 可能合并两边内容，可能选择其一
  → 删除冲突标记 <<<<<<< ======= >>>>>>>
  → 确保解决后的内容语法正确

第四步：标记已解决
  $ git add <冲突文件>
  → 解决后用 git add 标记

第五步：继续操作
  $ git rebase --continue   # 如果是 rebase 冲突
  $ git merge --continue    # 如果是 merge 冲突

第六步：验证
  → 解决冲突后测试相关功能
  → 确认未引入新问题
```

### 6.3 冲突解决原则

| 原则 | 说明 |
|------|------|
| 不盲目选择一方 | 理解两边变更的意图，综合判断 |
| 保留双方意图 | 尽量合并两边的有效变更 |
| 保持语法正确 | 解决后文件必须能正常解析 |
| 记录解决决策 | 复杂冲突在提交信息中说明解决方式 |
| 中止选项 | 冲突过于复杂时可用 `git rebase --abort` 放弃 |

### 6.4 冲突预防

- 频繁拉取远程更新（每天开始工作前 `git pull`）。
- 功能分支生命周期尽量短（3-5 天内合并）。
- 大改动前与协作者沟通，避免并行修改同一文件。
- 文档按模块分文件，减少单文件多人修改。

## 7. 版本标签管理

### 7.1 版本号规范

遵循语义化版本（Semantic Versioning）：

```text
版本号格式：MAJOR.MINOR.PATCH

MAJOR: 破坏性变更（规则结构重组、红线重新定义），旧版项目需手动迁移
MINOR: 新增规则或增强，向后兼容
PATCH: 修正措辞、补充说明

示例：
1.0.0 — 初始版本
1.1.0 — 新增战斗系统（MINOR）
1.1.1 — 修正战斗系统措辞（PATCH）
2.0.0 — 规则结构重组（MAJOR）
```

### 7.2 标签操作

```text
版本标签操作：

创建标签：
  $ git tag -a v1.1.0 -m "新增战斗系统和物品系统"

  → 使用附注标签（-a），包含标签信息
  → 标签名以 v 开头，后跟语义化版本号

查看标签：
  $ git tag -l              # 列出所有标签
  $ git show v1.1.0         # 查看标签详情

推送标签：
  $ git push origin v1.1.0  # 推送单个标签
  $ git push origin --tags  # 推送所有标签（需确认）

删除标签：
  $ git tag -d v1.1.0       # 删除本地标签
  $ git push origin :refs/tags/v1.1.0  # 删除远程标签（需确认）
```

### 7.3 标签使用场景

| 场景 | 操作 | 示例 |
|------|------|------|
| 里程碑发布 | 在 main 分支打标签 | v1.0.0 初始发布 |
| 规则大版本 | MAJOR 变更时打标签 | v2.0.0 规则重组 |
| 功能集完成 | MINOR 变更可打标签 | v1.1.0 战斗系统完成 |

### 7.4 版本变更日志

每个版本标签应配套变更日志（CHANGELOG.md）：

```markdown
## [1.1.0] - 2026-07-13

### 新增
- 战斗系统：伤害计算、战术选项、伤害类型
- 物品系统：分类、稀有度、效果、交易
- 对话系统：说服/欺骗/威胁/贿赂机制

### 修复
- 修复 NPC 跨区域信息泄露问题
- 修复物品堆叠数量异常

### 变更
- 状态文件校验逻辑重构
- 审计日志格式标准化
```

## 8. 常用操作速查

### 8.1 日常操作速查表

| 操作 | 命令 | 备注 |
|------|------|------|
| 查看状态 | `git status` | 每次操作前必做 |
| 查看差异 | `git diff` | 提交前必做 |
| 暂存文件 | `git add <文件>` | 逐个添加 |
| 提交 | `git commit -m "类型(范围): 描述"` | 遵循格式 |
| 查看日志 | `git log --oneline -10` | 最近 10 条 |
| 拉取 | `git pull --rebase` | 推送前必做 |
| 推送 | `git push origin <分支>` | 需用户确认 |
| 创建分支 | `git checkout -b feature/<描述>` | 从 develop 创建 |
| 合并分支 | `git merge --no-ff <分支>` | 保留历史 |
| 解决冲突 | 编辑文件后 `git add` | 逐个解决 |

### 8.2 紧急操作

| 场景 | 操作 | 备注 |
|------|------|------|
| 撤销未暂存修改 | `git checkout -- <文件>` | 恢复到最后提交 |
| 撤销已暂存修改 | `git reset HEAD <文件>` | 取消暂存 |
| 修改最近提交 | `git commit --amend` | 仅未推送时 |
| 回退到某提交 | `git reset --hard <commit>` | 危险，需确认 |
| 查看某文件历史 | `git log -- <文件>` | 追溯变更 |

## 9. 检查清单

- [ ] Git 操作前是否检测了操作系统？
- [ ] 提交前是否执行了 git status + git diff？
- [ ] 是否逐个文件 git add 而非 git add .？
- [ ] 提交信息是否遵循"类型(范围): 描述"格式？
- [ ] 推送前是否拉取了远程更新？
- [ ] 推送前是否获得了用户确认？
- [ ] 是否绝不使用 git push -f？
- [ ] 冲突解决后是否验证了语法正确性？
- [ ] 版本标签是否使用附注标签（-a）？
- [ ] .game-state/ 等运行时文件是否被 .gitignore 排除？
