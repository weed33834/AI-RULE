# Scenario Pack 规范（SCENARIO_PACK_SPEC）

> 版本：1.0（2026-08-08）｜ 状态：生效
> 配套校验器：`scripts/validate_packs.py`（CI 硬断言）
> 术语：**场景规则包 (Scenario Pack)** 是 AgentSeed 的 L1 可插拔单元；代码目录沿用 `personas/`（兼容），对外统一称"场景规则包"。

---

## 1. 什么是场景规则包

一个场景规则包 = 面向特定任务场景的 **场景协议 + 提示词 + 技能引用 + 能力白名单 + 路由锚点**，由一份 manifest（`persona.yaml`）声明，放在 `personas/<id>/` 目录。

- **互斥**：同一会话只有一个主场景包；`mutually_exclusive_with` 声明互斥关系，路由层强制。
- **可插拔**：新增场景 = 新增一个目录 + 一份 manifest，不改内核（`core/`）、不改路由代码。
- **叠加**：能力插件（L2）由场景包通过 `enables_capabilities` / `forbids_capabilities` 声明启用/禁用。

## 2. 目录结构

```
personas/<id>/
├── persona.yaml          # 包清单（本规范 §3）
├── AGENTS.md             # 场景协议（本包工作协议，装配时内联，必选）
├── prompts/              # 子代理/专业化提示词（system-prompt.md 内联，其余进 ON-DEMAND INDEX）
└── skills/               # 技能引用（按需加载）
```

## 3. manifest 规范（persona.yaml）

```yaml
# 顶部注释：来源仓库 + 适用场景（必填，便于市场与审计）

profile:                       # ← 兼容键名保留；语义 = pack
  id: coding                   # 必填，== 目录名，小写连字符
  name: 软件开发规则             # 必填，显示名
  category: dev                # 可选：general/dev/creative/research/strategic（PACK_CONTRIBUTING.md §1）
  source_repo: badhope/xxx      # 必填，内容来源仓库
  mutually_exclusive_with:      # 必填，互斥清单（需对称：A 列 B，B 必列 A）
    - novel
  agent_mode:
    default: project            # task | project | autonomous
    allowed: [task, project, autonomous]

includes:                      # 必填，三类引用；所有路径相对仓库根
  core:                        # 必填 ≥1：内核文件（一般直接列 governance 全家桶）
    - core/governance.md
  profile:                     # 必填 ≥2：本包协议 + system-prompt
    - personas/<id>/AGENTS.md
    - personas/<id>/prompts/system-prompt.md
  skills:                      # 可选 ≥0：技能（按需加载，不预载）
    - personas/<id>/skills/xxx.md

enables_capabilities:          # 可选：启用的 L2 能力插件（id 必须存在于 capabilities/）
  - research
forbids_capabilities:          # 可选：禁用的 L2 能力插件
  - game-engine

activation_anchors: []         # 可选：项目锚点文件（存在则自动路由到本包）
intent_keywords:               # 可选：意图关键词（命中则自动路由到本包）
  - 查询
```

### 字段校验规则（validator 强制）

| 字段 | 必填 | 规则 |
|---|---|---|
| `profile.id` | 是 | == 目录名，匹配 `^[a-z0-9-]+$` |
| `profile.name` | 是 | 非空 |
| `profile.source_repo` | 是 | 非空 |
| `profile.mutually_exclusive_with` | 是 | 列表；对称性校验（A⇄B） |
| `profile.agent_mode.default` | 是 | ∈ {task, project, autonomous} |
| `profile.agent_mode.allowed` | 是 | 非空，包含 default |
| `includes.core` | 是 | 非空；每个路径存在 |
| `includes.profile` | 是 | 非空；每个路径存在且非空（**缺失 AGENTS.md 会被拦下**） |
| `includes.skills` | 否 | 每个路径存在且非空 |
| `enables_capabilities` | 否 | 每个 id 存在于 `capabilities/<id>/` |
| `forbids_capabilities` | 否 | 同上 |
| `activation_anchors` | 否 | 字符串列表 |
| `intent_keywords` | 否 | 非空字符串列表 |

## 4. 能力插件规范（capabilities/<cap>/）

```
capabilities/<cap>/
├── cap.yaml          # 声明：id、name、description、适用场景（见 capabilities/<cap>/cap.yaml 实际格式）
├── prompt.md         # 能力提示词（按需加载）
└── mcp.json          # 可选：推荐 MCP（仅参考，配置权在用户）
```

校验：被任一场景包 `enables`/`forbids` 引用的能力 id 必须存在且 cap.yaml 可解析。

## 5. 如何新增一个场景规则包（扩展指南）

```bash
# 1) 建目录与清单
mkdir personas/my-scenario
cp personas/_template/default/persona.yaml personas/my-scenario/persona.yaml
# 2) 编辑 manifest：id/name/source_repo/mutually_exclusive/includes/caps/anchors/keywords
# 3) 写场景协议
touch personas/my-scenario/AGENTS.md
# 4) 写提示词（至少 system-prompt.md）
mkdir personas/my-scenario/prompts
# 5) 本地校验
python scripts/validate_packs.py
# 6) 装配验证（产物不得出现 [missing] 标记）
agentseed forge --profile my-scenario --dry-run
# 7) 需要时同步到平台
agentseed sync --profile my-scenario
```

新增场景**不需要**改动：`core/`（内核）、路由代码、同步引擎、任何平台适配器。

## 6. 校验与 CI

```bash
python scripts/validate_packs.py          # 校验全部场景包 + 能力引用，失败退出码 1
python scripts/validate_packs.py --json   # JSON 报告（供脚本消费）
```

校验器覆盖：manifest 结构、引用文件存在性与非空、能力 id 有效性、互斥对称性、模式合法性。任何"引用漂移"（文件被删、路径写错、能力被移除）都会在 CI 拦下——这正是防止"forge 产物出现 [missing] / 跑不通"的机制。
