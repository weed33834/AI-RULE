# 远程沙箱工程规范 (Remote Sandbox SOP)

> 本文件汇总在远程沙箱环境（CI/non-interactive shell）中执行开发任务时**跨平台通用**的工程教训与防范措施。
> 平台专属陷阱（如 Trae 沙箱的 /tmp 清理、Edit 工具路径限制）见 `adapters/<platform>/` 下对应文件，仅在检测到对应平台时生效。
> 来源：真实会话复盘，非臆测。

## 1. 工作目录选择（根因防范）

- **克隆仓库一律放到允许工具访问的工作目录下**，不要放 `/tmp`。
  - `/tmp` 在多数沙箱中会被周期性清理，且部分内置工具（Edit/Write）可能被沙箱策略限制访问 `/tmp`。
  - 推荐路径：当前工作目录的子目录（如 `/workspace/<repo>`），确保 Read/Edit/Write/Grep/Glob 全部可用。
- 涉及"备份再改大文件"时，备份文件也要放在工作目录内，不要放 `/tmp`。

## 2. Push 时机（防丢工作）

- **每个阶段 commit 后立即 `git push`**，不积压本地 commit。
  - 远程是唯一可信源；本地工作目录可能因沙箱清理、会话结束、磁盘回收而丢失。
  - 尤其是大改造项目：分阶段 commit + push，比"全部做完再一次性 push"安全得多。
- push 前仍遵守 `git-sop.md`：`git status` + `git diff` 确认无夹带，`git log origin/main..HEAD` 确认领先提交都是预期内的。
- 仅在用户明确要求"不要 push"或"最后统一 push"时才延后，否则默认每 commit 即 push。

## 3. 命令输出可见性（防盲跑）

- 沙箱的命令输出有时会被系统提醒截断或清空，导致看不到实际结果。
- **关键命令末尾用 `echo` 显式打印关键结果**，把结果钉在输出末尾：
  ```bash
  git push origin main 2>&1 | tail -3
  echo "PUSH_EXIT:$?"           # 退出码
  echo "FILES_CHANGED:$(git diff --stat origin/main..HEAD | tail -1)"  # 改动统计
  ```
- 对多步骤命令，每步打印标记：`echo "=== STEP 2 DONE ==="`。
- 若发现输出被清空，不要靠"再跑一条间接验证"浪费轮次，直接用 `CheckCommandStatus` 按 command_id 重取输出。

## 4. RunCommand 工作目录

- **始终用 `cwd` 参数显式指定工作目录**，不依赖 `cd <dir> &&` 前缀。
  - 默认 cwd 可能不是你期望的目录（常见为 /workspace 而非上次 cd 的目录）。
  - 跨命令的状态持久性不可靠，显式 cwd 更安全。

## 5. Subagent 任务拆分

- **单次委派给 subagent 的任务控制在 5-8 个文件以内**，避免超时或遗漏。
  - 大任务（一次 10+ 文件）容易让 subagent 超时或遗漏部分文件，事后补齐成本高。
- subagent 无对话上下文，query 里必须写完整背景：项目定位、已完成阶段、技术栈、关键决策（如"已选 recharts"）、文件路径。
- 要求 subagent 用 TodoWrite 自跟踪进度，避免遗漏。

## 6. 依赖环境缺失的处理

- 仓库若没有 `node_modules` / `.venv`，先 `npm install` / `pip install -r requirements.txt`（若沙箱允许）。
- 若无法安装依赖，接受"静态校验通过"为充分条件，并在交付报告中明确标注：
  > "已通过 `node --check` / 语法校验，未进行运行时校验。运行前需在有依赖环境执行 `npm install` + `prisma generate` 等。"
- 不要谎称"真实可运行"——区分"语法校验通过"与"运行时验证通过"。

## 7. Git user 未配置的处理

- 沙箱常未配置 git user.email/user.name，commit 会失败。
- **不要全局配置**（规则约束 NEVER update the git config），改用：
  ```bash
  git -c user.email=agent@local -c user.name=agent commit -m "..."
  ```
  或环境变量：
  ```bash
  GIT_AUTHOR_NAME=agent GIT_AUTHOR_EMAIL=agent@local \
  GIT_COMMITTER_NAME=agent GIT_COMMITTER_EMAIL=agent@local \
  git commit -m "..."
  ```

## 8. 静态校验作为无依赖环境的替代

- `node --check <file.js>` — JS 语法校验（不需 node_modules）。
- `@babel/parser`（jsx 插件）— JSX 文件校验（需临时 `npm install --no-save @babel/parser`，不改 package.json）。
- `npx prisma format` — Prisma schema 语法校验（不需 DATABASE_URL）。
- `npx prisma validate` — 需要 `DATABASE_URL` 环境变量才能解析 `env("DATABASE_URL")`，否则报错；用 `DATABASE_URL="file:./dev.db" npx prisma validate` 绕过。

## 9. 资源文件重命名（保留历史）

- 用 `git mv <old> <new>` 重命名，而非 `mv` 后重新 `git add`。
  - git mv 保留文件历史，diff 显示为 rename 而非 delete+add。
- 整目录重命名同样用 `git mv <old_dir> <new_dir>`。

## 10. 批量文本替换的顺序

- sed/replace 时**长串优先于短串**，避免半截替换：
  ```
  正确顺序：
  1. anythingllm.com  → traveler.app     （先替换域名）
  2. anything-llm     → traveler          （再替换短串）
  
  错误顺序（会导致 anything-llm.com 被先替换成 traveler.com，域名丢失）：
  1. anything-llm     → traveler
  2. anythingllm.com  → traveler.app      （此时已无 anythingllm.com 可匹配）
  ```
- 替换后做多轮 grep 校验（大小写不敏感、下划线/连字符/驼峰多种变体），不止一轮。

## 参考

- 平台专属陷阱：`adapters/<platform>/` 下对应文件。
- Git 提交规范：`@docs/skills/git-sop.md`。
