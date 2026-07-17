# 新项目初始化配置指令（复制发给任意 AI 工具）

> 用途：开新小说创作项目时，把这套规则模板一次性注入项目，让 Codex / Claude Code / Cursor / Trae / OpenCode / Qoder / GitHub Copilot 等工具都按你的小说创作铁律辅助创作。
> 规则唯一源头：本仓库（novel）

## 直接复制下面这段发给智能体

```
【任务】初始化本项目小说创作规则
【来源】规则模板仓库：novel（通用小说创作规则模板）
【要求】
1. 把仓库里的以下文件/目录原样拷贝到当前项目根目录（不要改写内容）：
   - AGENTS.md
   - CLAUDE.md
   - GEMINI.md
   - scripts/sync_rules.py
   - .github/ （含 copilot-instructions.md）
   - docs/ （含 prompts/ 下的系统提示词与子角色定义[explorer/writer/reviewer]、skills/ 下的全部技能文档[含 anti-ai-patterns.md、writing-techniques.md、web-novel-guide.md、world-building.md、character-crafting.md、creative-evaluation.md 等 17 个文档]）
   - .env.example
   - .pre-commit-config.yaml
2. 你可以用 `git clone` 临时拉取再拷贝，或用 API / curl 直接下载对应文件；完成后删除临时文件，不要提交 git。
3. 拷贝完成后，完整读取 AGENTS.md，并用一句话向我确认：「规则已生效，当前项目的核心小说创作铁律为：<用你自己的话归纳 3 条最关键的点>」。
4. 确认时需包含以下关键词中的至少 3 个：内部一致性、内容分级、去AI文学味、创作种子、伏笔追踪、故事知识图谱。
【约束】禁止改写模板内容；禁止额外创建文件；禁止自动 git commit / push；禁止在收集创作种子前自行脑补内容。
```

## 验证是否生效

初始化完成后，直接问智能体：

> 当前项目的小说创作规范和我定的创作铁律是什么？

若它准确答出「内部一致性优先 / 内容分级合规 / Show don't tell / 创作种子必须先收集 / 伏笔追踪与回收 / 去AI文学味 / 安全红线」等要点，说明规则已注入成功。

## 桌面端快捷方式（本机已 clone 此仓库时）

```bash
SRC=/path/to/AI-RULE   # 改成你的规则模板仓库实际路径
cp "$SRC/AGENTS.md" "$SRC/CLAUDE.md" "$SRC/GEMINI.md" ./
cp "$SRC/.env.example" "$SRC/.pre-commit-config.yaml" ./
cp -r "$SRC/.github" ./
cp -r "$SRC/docs" ./
cp -r "$SRC/scripts" ./
```

## 改了规则怎么同步

只改 `AGENTS.md`（它是唯一源头），然后：

```bash
cd /path/to/AI-RULE
python scripts/sync_rules.py   # 同步到 CLAUDE.md / GEMINI.md / .github/copilot-instructions.md
git add AGENTS.md CLAUDE.md GEMINI.md .github/copilot-instructions.md docs/ scripts/
git commit -m "feat(rules): 更新小说创作规则"
git push
```
