# Trae 会话护栏 (Trae Session Guardrails)

> 本文件定义 **Trae 平台专属**的会话护栏规则。仅在检测到当前运行环境为 Trae 时生效。
> 跨平台通用的远程沙箱工程规范见 `profiles/coding/docs/skills/remote-sandbox-sop.md`，本文件只补充 Trae 独有的陷阱。
> 来源：真实 Trae 会话复盘，非臆测。

## 0. 平台检测（何时应用本文件）

满足以下**任一**特征即判定为 Trae 环境，应用本文件全部条款：

| 特征 | 检测方式 |
|------|---------|
| 沙箱环境变量 | 环境中存在 `TRAE_SANDBOX=1` 或 `CI=true` + `stdin=EOF` 的 non-interactive shell |
| 工作目录特征 | 默认 cwd 为 `/workspace`，且工具说明中明确"Primary working directory: /workspace" |
| Edit 工具路径限制 | Edit/Write 工具对 `/tmp/*` 路径报错（如"old_string not found"但 Read 能读到）或明确限定在 `/workspace` |
| 命令输出特征 | RunCommand 结果被 `<system-reminder>` 标记为 "Results from RunCommand have been CLEARED by system-reminders" |
| 操作系统特征 | linux + 非 TTY + stdin=EOF 的远程沙箱 |

> 检测到任一特征后，**主动告知用户**："检测到 Trae 沙箱环境，已启用 Trae 会话护栏。" 然后执行以下条款。

## 1. 工作目录硬约束（Trae 专属）

- **克隆仓库一律放到 `/workspace/` 下**，禁止放 `/tmp`。
  - `/tmp` 在 Trae 沙箱中会被周期性清理（实测：会话中途 `/tmp/traveler` 整个目录消失）。
  - `/tmp` 下的文件 Edit/Write/Grep/Glob 工具可能拒绝访问（实测：Edit 对 `/tmp/traveler/README.md` 报"old_string not found"，但 Read 能读到）。
  - `/workspace` 是 Trae 内置工具（Read/Edit/Write/Grep/Glob/SearchCodebase）的唯一稳定可用范围。
- 命令示例：
  ```bash
  # 正确
  git clone <url> /workspace/<项目名>
  # 错误（会被清理 + 工具拒绝）
  git clone <url> /tmp/<项目名>
  ```

## 2. 命令输出被清空（Trae 专属）

- Trae 的 RunCommand 结果有时被 `<system-reminder>` 标签清空，表现为 `<toolcall_result>` 显示 "Results from RunCommand have been CLEARED by system-reminders"。
- **防范**：
  1. 关键命令末尾 `echo` 显式打印结果（见 remote-sandbox-sop.md §3）。
  2. 若输出被清空，用 `CheckCommandStatus` 按 command_id 重取输出（而非重跑命令浪费轮次）。
  3. 对于需要确认结果的命令，用独立的验证命令（如 `curl API` 验证远程状态）替代依赖本地输出。

## 3. zsh read-only 变量（Trae 专属）

- Trae 沙箱的默认 shell 是 zsh，以下变量名是 read-only，**禁止用作循环变量或赋值目标**：
  ```
  status  ?  #  $  *  @  -  ARGC  HISTCMD  LINENO
  ```
- 实测报错：`zsh:15: read-only variable: status`
- **防范**：循环变量改用 `code`/`result`/`idx`/`item`/`entry` 等普通名。
- 完整 read-only 列表可用 `typeset -r` 查看（但记住上述常见项即可）。

## 4. Edit 工具对 /tmp 路径的行为（Trae 专属）

- Trae 的 Edit 工具对 `/tmp/*` 路径报错"old_string not found"，即使 Read 能正常读到内容。
- **防范**：
  1. 如 §1 所述，把仓库放 `/workspace` 下，Edit 即可正常工作。
  2. 若已误放 `/tmp`，改用 python3 脚本或 sed 在 bash 中完成编辑：
     ```bash
     python3 -c "
     p='/tmp/<file>'
     s=open(p,encoding='utf-8').read()
     s=s.replace('<old>','<new>')
     open(p,'w',encoding='utf-8').write(s)
     "
     ```

## 5. Subagent 在 Trae 中的工具限制（Trae 专属）

- Trae 的 Task subagent（general_purpose_task）在沙箱中 Grep/Glob/Write/Edit 工具被限定在 `/workspace`，无法访问 `/tmp`。
- subagent 若需访问 `/tmp` 下的文件，只能改用 RunCommand（bash 的 cat/sed/grep）。
- **防范**：主 agent 委派任务时，确保工作目录在 `/workspace` 下；在 query 里明确告知 subagent 工作目录路径，避免 subagent 自己探索时踩坑。

## 6. node_modules 缺失与临时依赖（Trae 专属）

- Trae 沙箱克隆的仓库通常没有 `node_modules`（被 .gitignore 忽略）。
- 需要做 JSX 校验但缺 `@babel/parser` 时，可临时安装但不改 package.json：
  ```bash
  npm install --no-save @babel/parser  # 不写入 package.json
  ```
- 校验 JSX：
  ```bash
  node -e "
  const fs=require('fs');const parser=require('@babel/parser');
  parser.parse(fs.readFileSync('<file>','utf8'),{sourceType:'module',plugins:['jsx']});
  console.log('OK');
  "
  ```
- 临时安装的包在 node_modules 里，.gitignore 已忽略，不会被 commit。

## 7. Trae 不支持的 hook 能力（已知限制）

- Trae 不支持自定义 PreToolUse hook（与 Claude Code/Cursor 不同），只能配置平台内置沙箱策略（见 `adapters/hooks/trae/sandbox-policy.json`）。
- 以下能力在 Trae 中**无法实现**，不要尝试：
  - 跨轮 stateful 状态（如失败熔断计数器）
  - runtime 输入检测（prompt injection guard）
  - 提交前软警告输出
- 需要这些能力时，靠 AI 自身遵守规则（即本文件 + remote-sandbox-sop.md）替代 hook 强制。

## 参考

- 通用工程规范：`profiles/coding/docs/skills/remote-sandbox-sop.md`
- Trae 沙箱策略配置：`adapters/hooks/trae/sandbox-policy.json`
- Git 提交规范：`profiles/coding/docs/skills/git-sop.md`
