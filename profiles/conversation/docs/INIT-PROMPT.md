# 新项目初始化配置指令（复制发给任意 AI 工具）

> 用途：将通用对话规则模板注入任意 AI 工具或项目，让对话质量全面提升。
> 规则唯一源头：`https://gitcode.com/badhope/AI-RULE`

## 直接复制下面这段发给智能体

```
【任务】初始化通用 AI 对话规则
【来源】规则模板仓库：https://gitcode.com/badhope/AI-RULE
【要求】
1. 把仓库里的以下文件/目录原样拷贝到当前项目根目录（不要改写内容）：
   - AGENTS.md
   - CLAUDE.md
   - GEMINI.md
   - scripts/sync_rules.py
   - .github/ （含 copilot-instructions.md）
   - docs/ （含 prompts/ 下的系统提示词、skills/ 下的 16 个技能文档）
   - .env.example
   - .pre-commit-config.yaml
2. 你可以用 `git clone` 临时拉取再拷贝，或用 API / curl 直接下载对应文件；完成后删除临时文件，不要提交 git。
3. 拷贝完成后，完整读取 AGENTS.md，并用一句话向我确认：「规则已生效，当前通用对话铁律为：<用你自己的话归纳 3 条最关键的点>」。
4. 确认时需包含以下关键词中的至少 3 个：真实性铁律、深度搜索、反降智、意图澄清、置信度标注。
【约束】禁止改写模板内容；禁止额外创建文件；禁止自动 git commit / push。
```

## 验证是否生效

初始化完成后，直接问智能体：

> 你的对话规则是什么？如果我问你一个你不知道的问题，你会怎么做？

若它准确答出「禁造假 / 不确定即问 / 深度搜索多源验证 / 反降智 5 项基准线 / 默认严谨简洁高效语气」等要点，说明规则已注入成功。

## 叠加在领域仓库之上

本仓库可与其他领域仓库叠加使用。叠加时：
- 领域仓库的规则优先（P2 领域 > P2 通用）
- 本仓库的真实性红线（P0）始终生效
- 建议先加载领域仓库，再加载本仓库作为增强层

## 桌面端快捷方式（本机已 clone 此仓库时）

如果本机已克隆 `universal` 仓库，可直接在终端执行等价拷贝（在**目标项目根目录**下运行）：

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
git commit -m "feat(rules): 更新规则"
git push
```

目标项目重新执行上面的「初始化配置指令」即可拿到最新规则。
