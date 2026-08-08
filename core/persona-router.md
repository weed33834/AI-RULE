# Persona Router（Profile 选择器）

> 本文件定义如何从用户意图或项目锚点确定唯一主 Profile，以及可叠加的能力包白名单。
> 每次会话只能有一个主 Profile；`novel`、`paper` 互斥；`agent-builder` 仅用于构建/评估/部署智能体。

## 1. 主 Profile 一览

| Profile ID | 来源仓库 | 适用场景 | 互斥 |
|---|---|---|---|
| `coding` | AI | 软件开发、Bug 修复、重构、测试、代码审查 | novel |
| `conversation` | universal | 通用问答、调研、方案对比、信息检索 | novel、agent-builder |
| `novel` | novel | 小说写作、章节创作、角色/世界观维护 | coding、conversation、agent-builder、paper |
| `paper` | badhope/paper | 学术论文写作、文献综述、投稿、审稿回复 | novel |
| `agent-builder` | AgentCreater | 设计/评估/部署智能体，产出 config、工具、测试 | conversation、novel |

## 2. 选择优先级

```text
1. 用户或项目配置显式指定 active_profile → 绝对优先
2. 目录锚点自动识别（仅在未指定时）
3. 用户当前意图关键词匹配
4. 识别不唯一时必须澄清，只问一个最小问题，不重复已确认项。
```

## 3. 目录锚点自动识别

| 锚点信号 | 推断 Profile |
|---|---|
| `pyproject.toml`、`package.json`、`requirements.txt` + 源码/测试目录 | `coding` |
| `.ai-memory/creative-blueprint.md`、`chapters/`、`outline.md` | `novel` |
| `.ai-memory/paper-blueprint.md`、`manuscript/`、`references.bib` | `paper` |
| `config.yaml` + `tools.json` + `test-cases.md` 的智能体资产目录 | `agent-builder` |
| 无上述锚点 | `conversation` |

## 4. 意图关键词匹配

| 关键词 | 推断 Profile |
|---|---|
| 修复/重构/测试/部署/接口/Bug/CI | `coding` |
| 写一章/续写/人物/伏笔/文风/世界观 | `novel` |
| 论文/文献综述/摘要/引言/方法/结果/讨论/引用/投稿/审稿 | `paper` |
| 设计 Agent/智能体配置/工具权限/评估 | `agent-builder` |
| 查询/对比/分析/调研/总结 | `conversation` |

## 5. 能力包叠加白名单

| 主 Profile | 可叠加能力包 | 禁止默认叠加 |
|---|---|---|
| `coding` | `research`、`testing`、`review`、`agent-governance`、`dar` | `worldbuilding` |
| `conversation` | `research`、`dar` | `engineering`、`creative` |
| `novel` | `research`（真实背景时）、`worldbuilding`、`creative`、`dar` | — |
| `paper` | `research`、`dar` | — |
| `agent-builder` | `research`、`agent-governance`、`engineering`、`testing`、`dar` | — |

> **DAR（域权威注册表）**：所有 Profile 默认可叠加。DAR 提供各领域权威源名录、打分规则、检索通道和领域知识，嵌入深度搜索和真实性验证流程。详见 `core/dar-spec.md`。

## 6. 冲突解决

```text
P0：core/ 安全与权限
> P1：用户当前明确确认
> P2：主 Profile 规则
> P3：能力包规则
> P4：模型默认行为
```

同一优先级出现相反约束时：
- 若一方是 P0，P0 胜出。
- 若同属 P2 但分属不同 Profile，主 Profile 胜出，能力包让位。
- 若仍无法裁决，停止并向用户说明冲突，请求裁决。

## 7. Profile 切换

- 用户可在会话中显式切换：`switch profile to <id>`。
- 切换时必须清除前一 Profile 的上下文状态标记，避免状态污染。
- `paper` 与 `novel` 互斥，切换时必须清除前一 Profile 的全部创作状态。

## 8. Agent 模式路由

> 推理深度与 Agent 模式的完整定义见 `core/agent-modes.md` 与 `core/attention-budget.md`。
> 本路由由 Profile 的 `personas/*.yaml` 中 `agent_mode` 字段控制默认值。

### 8.1 选择流程

```
1. 用户显式指定模式（switch mode to <task|project|autonomous>）→ 绝对优先
2. core/mode-overrides.yaml 中的条件匹配（profile/repo/时间窗口/产物类型）
3. 读取当前 Profile manifest 中的 agent_mode.default
4. 根据用户意图推断（见 agent-modes.md §3）
5. 推断失败时降级为 task
```

> `core/mode-overrides.yaml` 为边缘场景覆写层，优先级高于 manifest 默认值，低于用户显式指定。默认全部注释，按需启用。

### 8.2 Profile 默认模式与推理深度

| Profile | 默认模式 | 允许模式 | 默认推理深度 |
|---------|---------|---------|-------------|
| `coding` | `project` | task, project, autonomous | STANDARD→DEEP |
| `conversation` | `task` | task, project | QUICK→STANDARD |
| `novel` | `project` | task, project, autonomous | STANDARD→DEEP |
| `paper` | `project` | task, project, autonomous | STANDARD→DEEP |
| `agent-builder` | `project` | task, project, autonomous | STANDARD→DEEP |

### 8.3 推理深度标记（RT）

推理深度通过 RT 标记注入上下文（定义见 `core/attention-budget.md`），Profile 切换或模式升级时自动调整：
- `RT:QUICK` — 简单任务（格式转换、数据提取、简单问答）
- `RT:STANDARD` — 常规任务（代码生成、方案对比、文档编写）
- `RT:DEEP` — 复杂任务（架构重构、多步规划、自主纠偏）
