# 贡献指南

改 AgentSeed 就三步：

## 1. 只改源文件，不改生成产物

源文件在这几个地方：
- `core/` — 安全底线、路由规则、决策公式
- `personas/<id>/` — 各人设（persona.yaml + prompts + skills）
- `capabilities/<cap>/` — 能力包（cap.yaml + prompt.md）

`AGENTS.md`、`CLAUDE.md`、`.cursor/rules/` 这些是 `agentseed sync` 自动生成的，手改了下次同步就覆盖掉了。别改它们。

## 2. 改完跑同步

```bash
agentseed sync
```

会自动重生成全部 14 个平台的入口文件。

## 3. 提交

用 Conventional Commits：

```
feat: 加了啥新功能
fix: 修了啥 bug
docs: 文档改动
refactor: 结构调整
chore: 杂活
```

提交前自查：
- `git status` 看看有没有不该提交的文件（`.env`、临时脚本之类的）
- 别把 Token / 密钥写死在代码里，用环境变量
- `python -m pytest tests/` 全绿再推

## 多语言 README

`README.md`（英文，默认）、`README.zh.md`、`README.ja.md` 内容要对齐。改一个的时候尽量把另外两个也改了；要是暂时只改英文，在 PR 描述里说一下。

## 新增人设

```bash
# 复制脚手架
cp -r personas/_template/default/ personas/my-role/

# 编辑 persona.yaml，填好：
#   - profile.name / profile.description
#   - includes（要加载的规则文件）
#   - enables_capabilities（要开的能力包）
#   - activation_anchors（什么文件/目录触发这个人设）
#   - intent_keywords（用户说什么关键词触发）

# 在 src/agentseed/router.py 的 PERSONAS 表里登记
# 跑验证
agentseed verify
```

## 新增平台

```bash
agentseed platform import 平台名 --entry 入口文件路径 --format 格式
```

支持的格式：`markdown`、`cursor`、`comate`。加 `--hook-dir` 参数会自动生成拦截钩子。

## 跑测试

```bash
python -m pytest tests/
```

144 个测试用例，涉及路由、装配、进化引擎、平台导入、DAR 评分等领域。PR 必须全绿。
