> 本文件是统一规则中枢的唯一入口。其他工具配置文件（CLAUDE.md、GEMINI.md、.cursor/rules/*.mdc 等）由 `python scripts/sync_rules.py` 从本文件和 selected profile 生成，请勿直接编辑它们。
> 引用语法：`@路径` 表示内联展开（同步时嵌入生成文件），裸路径表示参见链接（不展开）。
> **AI 入口**：被导入本仓库作为规则时，先读 `PROJECT.md` 了解仓库用途和工作方式，再读本文件。

# Rule Hub — 统一规则中枢

本仓库整合了 5 套独立规则体系，通过 **核心层 + 单一主 Profile + 能力包** 的分层加载，保留每套规则的独立定制能力，同时避免互相冲突。

## 1. 规则分层与优先级

```text
P0：core/ 安全、权限、真实性、MCP 红线、失败熔断
> P1：用户当前明确确认
> P2：主 Profile 领域规则
> P3：能力包按需规则
> P4：模型默认行为
```

冲突时高优先级胜出；同优先级出现相反约束时停止并询问用户。

## 2. 可用 Profile

| Profile | 适用场景 | 来源 |
|---|---|---|
| `coding` | 软件开发、Bug 修复、重构、测试 | `profiles/coding/` |
| `conversation` | 通用问答、调研、方案对比 | `profiles/conversation/` |
| `novel` | 小说写作、章节创作、角色/世界观 | `profiles/novel/` |
| `interactive-novel` | 互动小说游戏、分支叙事、状态机 | `profiles/interactive-novel/` |
| `agent-builder` | 设计/评估/部署智能体 | `profiles/agent-builder/` |

## 3. 加载顺序

1. 加载 `@core/governance.md`、`@core/interaction.md`、`@core/profile-router.md`、`@core/language-mediation.md`。
2. 确定 `active_profile`；未确定时按 `core/profile-router.md` 的锚点和关键词推断；推断不唯一时只问一个最小澄清问题。
3. 加载 `@manifests/<active_profile>.yaml` 声明的全部文件。
4. 仅在用户明确要求或任务匹配时加载 `capabilities/` 下的能力包。
5. 每次会话只能有一个主 Profile；`novel` 与 `interactive-novel` 互斥；`agent-builder` 仅用于构建智能体。

## 4. 使用方式

克隆本仓库后，按以下方式指定规则：

```text
# 方式一：显式指定
"按 Rule Hub 加载 coding Profile。"

# 方式二：由项目锚点自动识别
在含 pyproject.toml 的项目目录启动 → 自动选 coding

# 方式三：同步生成各工具入口
python scripts/sync_rules.py --profile coding --tool claude-code
```

## 5. 核心硬约束（不可覆盖）

@core/governance.md

## 6. 交互规范（所有 Profile 共享）

@core/interaction.md

## 7. Profile 选择与能力包白名单

@core/profile-router.md

## 8. 语言中介协议（所有 Profile 共享）

@core/language-mediation.md

## 9. 跨工具同步

- `AGENTS.md` 为规范源；`CLAUDE.md`、`GEMINI.md`、`.cursor/rules/*.mdc`、`.github/copilot-instructions.md`、`.trae/rules/project_rules.md` 均由 `scripts/sync_rules.py` 按 selected profile 生成。
- 生成文件头部带来源、生成时间、输入哈希与"禁止手工编辑"标记。
- 禁止手工编辑生成文件。

## 10. 项目隔离

- 本仓库是协作规则中枢，不属于任何具体开发项目。
- 规则文件与项目文件分开识别：除非用户明确要求修改规则，否则不得因开发任务改动本仓库。
- 执行具体项目任务前，先确认项目根目录；项目代码、依赖、Git 操作仅在该项目根目录内进行。

## 11. 验证

- 结构测试：`python tests/test_structure.py`
- Profile 选择测试：`python tests/test_profile_router.py`
- 同步测试：`python tests/test_sync.py`
- 复杂场景测试：`python tests/test_scenarios.py`
