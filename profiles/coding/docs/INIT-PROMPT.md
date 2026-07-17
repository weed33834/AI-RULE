# 新项目初始化配置指令（复制发给任意 AI 工具）

> 用途：开新项目时，把这套规则模板一次性注入项目，让 Codex / Claude Code / Cursor / Trae / OpenCode / Qoder / GitHub Copilot 等工具都按你的铁律开发。
> 规则唯一源头：`https://gitcode.com/badhope/AI-RULE`

## 直接复制下面这段发给智能体

```
【任务】初始化本项目 AI 开发规则
【来源】规则模板仓库：https://gitcode.com/badhope/AI-RULE
【要求】
1. 把仓库里的以下文件/目录原样拷贝到当前项目根目录（不要改写内容）：
   - AGENTS.md
   - CLAUDE.md
   - GEMINI.md
   - .github/ （含 copilot-instructions.md）
   - docs/ （含 prompts/ 下的系统提示词与子角色定义）
2. 你可以用 `git clone` 临时拉取再拷贝，或用 API / curl 直接下载对应文件；完成后删除临时文件，不要提交 git。
3. 拷贝完成后，完整读取 AGENTS.md，并用一句话向我确认：「规则已生效，当前项目的核心开发铁律为：<用你自己的话归纳 3 条最关键的点>」。
【约束】禁止改写模板内容；禁止额外创建文件；禁止自动 git commit / push。
```

## 验证是否生效

初始化完成后，直接问智能体：

> 当前项目的编码规范和我定的开发铁律是什么？

若它准确答出「先规划后代码 / 歧义即停 / 禁 AI 味 / 用成熟库禁止手写底层 / 改动后必须跑测试验证」等要点，说明规则已注入成功。

## 桌面端快捷方式（本机已 clone 此仓库时）

如果本机已克隆 `AI` 仓库，可直接在终端执行等价拷贝（在**新项目根目录**下运行）：

```bash
SRC=/path/to/AI-RULE   # 改成你的规则模板仓库实际路径（不要写死个人绝对路径）
cp "$SRC/AGENTS.md" "$SRC/CLAUDE.md" "$SRC/GEMINI.md" ./
cp -r "$SRC/.github" ./
cp -r "$SRC/docs" ./
```

## 改了规则怎么同步

只改 `AI` 仓库里的 `AGENTS.md`（它是唯一源头），然后：

```bash
cd /path/to/AI-RULE
python scripts/sync_rules.py   # 同步到 CLAUDE.md / GEMINI.md / .github/copilot-instructions.md
git add -A && git commit -m "更新规则" && git push
```

新项目重新执行上面的「初始化配置指令」即可拿到最新规则。
