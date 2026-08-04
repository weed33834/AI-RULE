# AgentSeed Architecture v1.0

> **定位**: One command to give a blank agent a brain.
>
> `pip install agentseed && agentseed forge` → 空白 Agent 立刻拥有完整人格、规则体系、技能和工具配置。

---

## 架构全景图

```
┌──────────────────────────────────────────────────────────────────┐
│                        AgentSeed                                   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              ⚡ GOVERNANCE ENGINE (宪法层 — 不可插拔)          │ │
│  │                                                               │ │
│  │  governance.md        安全/保密/真实性/澄清/P0 红线            │ │
│  │  constraints.yaml     机器可执行约束 (PreToolUse hook)        │ │
│  │  agent-modes.md       Task/Project/Autonomous 模式机          │ │
│  │  attention-budget.md  Instruction Budget + RT 预算            │ │
│  │  interaction.md       交互协议                                │ │
│  │  language-mediation.md 语言中介                               │ │
│  │  mcp-integration.md   MCP 红线                                │ │
│  │  persona-router.md    画像路由                                │ │
│  │  dar-spec.md          域权威注册表 (搜索质量引擎)              │ │
│  │                                                               │ │
│  │  🧬 SELF-EVOLUTION ENGINE (自进化引擎) ★ 新增                 │ │
│  │  ┌───────────────────────────────────────────────────────┐   │ │
│  │  │  Capability Gap Detection → Scoring → Decision → Act  │   │ │
│  │  │  (见 §Self-Evolution Engine 详细设计)                  │   │ │
│  │  └───────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              ↓ 基于画像路由                       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │           🎭 PERSONA PACKS (可插拔画像插件)                    │ │
│  │                                                               │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │ │
│  │  │ 🧑‍💻 coding │ │ 📖 novel │ │ 💬 conv  │ │ 🎮 i-novel  │   │ │
│  │  │          │ │          │ │          │ │              │   │ │
│  │  │ SOUL.md  │ │ SOUL.md  │ │ SOUL.md  │ │ SOUL.md      │   │ │
│  │  │ AGENTS   │ │ AGENTS   │ │ AGENTS   │ │ AGENTS       │   │ │
│  │  │ Skills   │ │ Skills   │ │ Skills   │ │ Skills       │   │ │
│  │  │ MCP list │ │ MCP list │ │ MCP list │ │ MCP list     │   │ │
│  │  │ Prompts  │ │ Prompts  │ │ Prompts  │ │ Prompts      │   │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │ │
│  │                                                               │ │
│  │  ┌──────────┐ ┌──────────────┐ ┌──────────────────────┐     │ │
│  │  │ 📝 paper │ │ 🤖 agent-bld │ │ 🔮 你的自定义画像...  │     │ │
│  │  │          │ │              │ │ agentseed persona new  │     │ │
│  │  └──────────┘ └──────────────┘ └──────────────────────┘     │ │
│  │                                                               │ │
│  │  Persona Pack = SOUL (Who) + Rules (Boundary)                 │ │
│  │               + Skills (How) + MCP (Tools) + Prompts (Style)  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              ↓ 同步引擎                           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │           🚀 PLATFORM SYNC (13 平台一键生成)                   │ │
│  │                                                               │ │
│  │  Claude Code │ Cursor │ Copilot │ Trae │ Gemini │ Windsurf   │ │
│  │  Cline │ Continue │ Amazon Q │ Qodo │ Lingma │ Comate │      │ │
│  │  AGENTS.md (通用)                                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## §1 Governance Engine (宪法层)

### 定位
Agent 的"永久大脑"，不被任何 Persona Pack 覆盖。定义了 Agent 的绝对边界和决策框架。

### 包含模块
| 模块 | 功能 | 不可覆盖等级 |
|------|------|------------|
| `governance.md` | P0 安全红线、真实性、澄清、变更范围 | P0 |
| `constraints.yaml` | 机器可执行约束 (PreToolUse hooks) | P0 |
| `agent-modes.md` | Task/Project/Autonomous 模式 | P0 |
| `attention-budget.md` | Instruction Budget + RT 推理预算 | P0 |
| `interaction.md` | 交互协议 | P0 |
| `language-mediation.md` | 语言中介 | P0 |
| `mcp-integration.md` | MCP 配置红线 | P0 |
| `persona-router.md` | 画像路由与选择 | P0 |
| `dar-spec.md` | 搜索权威打分协议 | P0 |
| **`self-evolution.md`** | ★ 自进化引擎 (新增) | P0 |

### 优先级
```
P0 Governance > P1 用户确认 > P2 Persona Pack > P3 Capabilities > P4 模型默认
```

---

## §2 Self-Evolution Engine (自进化引擎) ★核心新增

### 2.1 设计哲学

AgentSeed 不只是一个"预设注入器"。当一个空白 Agent 面对 GOVERANCE ENGINE 里没有覆盖的场景（比如：用户问了一个需要特定工具的问题，但当前 Persona 没配这个工具），Agent 不应该卡住——它应该**自主检测能力缺口、评估解决方案、执行获取动作**。

这就是 Self-Evolution Engine 做的事。

### 2.2 Capability Gap Score (能力缺口评分)

当 Agent 无法用现有资源满足用户请求时，计算缺口分数：

```
GapScore = Σ( w_i × factor_i )

因子                         权重   说明
──────────────────────────────────────────────
MissingToolScore             0.35   需要的工具不存在于当前技能/MCP 列表中
MissingKnowledgeScore        0.25   现有知识/规则无法覆盖请求领域
UserIntentUrgency            0.20   用户需求的紧迫度（显式要求 > 隐式需要）
AlternativeExhaustedScore    0.10   已有替代方案是否已尝试失败
RiskOfActionScore            0.10   自行获取的动作风险（操作越安全分数越高）
```

**GapScore 阈值决策树**：

```
GapScore < 0.30  → 不做任何事，用现有能力尽力回答
GapScore 0.30-0.55 → 输出建议命令供用户手动执行
GapScore 0.55-0.75 → 执行低风险获取（搜索/clone 只读仓库/下载公开包）
                      但需告知用户正在做什么
GapScore > 0.75  → 全自动获取 + 配置 + 热加载，完成后告知用户
                    （P0 红线例外：MCP 不自安装、密钥不自配）
```

### 2.3 Action Decision Matrix (动作决策矩阵)

| 能力缺口类型 | GapScore 范围 | 动作 | 工具/方法 | 约束 |
|------------|-------------|------|----------|------|
| 缺少领域知识 | 0.30-0.75 | web_search | DAR 打分、T1 优先 | 最多 3 次搜索 |
| 缺少领域知识 | >0.75 | web_search→web_fetch→整合 | DAR + 多源交叉验证 | 标注来源 |
| 缺少技能/模板 | 0.30-0.75 | 推荐克隆/下载命令 | 仅输出命令供用户执行 | 不自动克隆 |
| 缺少技能/模板 | >0.75 | `git clone` / `pip install` / 下载 | 自动执行 | 排除 .git，验证 checksum |
| 缺少 MCP 工具 | 任意 | 输出配置 JSON | 仅输出，用户手动粘贴 | 绝对不自安装 MCP (P0) |
| 缺少环境依赖 | 0.55-0.75 | 推荐安装命令 | 输出命令 | 不自动 sudo |
| 缺少环境依赖 | >0.75 | 自动安装（非 sudo） | `pip/npm/brew install` | 先检查是否已存在 |
| 现有效能不足 | >0.55 | 自我评估→替换 | 卸载旧→安装新 | 备份配置 |

### 2.4 Quality Gate (获取后验证)

任何自动获取的内容必须通过三关验证：

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Gate 1      │     │ Gate 2       │     │ Gate 3          │
│ 安全检查     │ →   │ 质量检查      │ →   │ 兼容性检查       │
│             │     │              │     │                 │
│ • 无恶意代码 │     │ • 测试通过   │     │ • 与现有规则    │
│ • .git 已清  │     │ • lint 通过  │     │   无冲突        │
│ • 密钥无泄露 │     │ • 文档完整   │     │ • 与画像兼容    │
└─────────────┘     └──────────────┘     └─────────────────┘
  ❌ → 拒绝+报告      ❌ → 降级告知用户    ❌ → 隔离+建议
```

### 2.5 Confidence-Weighted Action Model (置信度加权动作模型)

对于不确定场景，使用贝叶斯更新的简化版本：

```
置信度 = 基础先验 × (匹配信号 / 信号噪声)

基础先验：
- 已知权威源(T1)命中: 0.85
- 搜索命中 > 3 个相关源: 0.70
- 搜索命中 1-2 个: 0.50
- 未命中: 0.20

信号：
- 内容语义相关度（0-1，由模型估算）
- 来源一致性（多源内容一致 +0.1/源，矛盾 -0.15/源）
- 时效性（< 6 月 +0.1，> 2 年 -0.1）

最终决策：
  置信度 >= 0.80: 直接采纳并整合
  0.50 <= 置信度 < 0.80: 采纳但标注"待验证"
  置信度 < 0.50: 仅输出建议，不自动采纳
```

### 2.6 触发时序

```
用户请求
  │
  ▼
当前 Persona + Skills + MCP 能否满足？
  │
  ├─ 能 → 正常执行
  │
  └─ 不能 → 计算 GapScore
              │
              ├─ < 0.30 → 尽力回答，告知局限
              │
              ├─ 0.30-0.55 → 输出建议命令
              │
              └─ > 0.55 → 执行获取动作
                            │
                            ├─ web_search (知识缺口)
                            ├─ git clone (技能/模板缺口)
                            └─ pip/npm install (依赖缺口)
                              │
                              ▼
                           Quality Gate (3关)
                              │
                              ├─ 通过 → 热加载到当前会话
                              │         写入 memory/ 供后续复用
                              └─ 失败 → 降级告知用户
```

---

## §3 Persona Packs (可插拔画像)

### 3.1 定义

```
Persona Pack = SOUL + RULES + SKILLS + MCP + PROMPTS
```

| 组件 | 内容 | 文件 |
|------|------|------|
| SOUL | 角色身份、语气风格 | SOUL.md |
| RULES | 领域约束 (Profile 级别) | AGENTS.md / 领域规则 |
| SKILLS | 可执行技能工作流 | skills/*.md |
| MCP | 推荐工具配置 | 配置 JSON |
| PROMPTS | 子代理/专业化提示词 | prompts/*.md |

### 3.2 核心画像（当前 6 个）

| Pack ID | 名称 | 核心能力 | 互斥 |
|---------|------|---------|------|
| `coding` | 软件工程师 | 开发、重构、测试、CI/CD | novel, interactive-novel |
| `conversation` | 通用助手 | 问答、调研、分析 | novel, interactive-novel, agent-builder |
| `novel` | 小说家 | 章节创作、角色、世界观 | coding, conversation, interactive-novel, agent-builder, paper |
| `interactive-novel` | 互动叙事 | 分支叙事、NPC、状态机 | coding, conversation, novel, agent-builder, paper |
| `paper` | 学术写手 | 论文、文献综述、投稿 | novel, interactive-novel |
| `agent-builder` | Agent 构建师 | 设计/评估/部署 Agent | conversation, novel, interactive-novel |

### 3.3 画像装配

#### 自动装配（默认）
```
agentseed forge
  → 检测项目锚点 (persona-router.md)
  → 推断最佳 Persona Pack
  → 生成所有平台入口文件
  → Agent 即刻拥有完整人格
```

#### 交互选择
```
agentseed forge --interactive
  → 列出所有可用画像
  → 用户选择
  → 装配并生成
```

#### 切换画像
```
agentseed switch --profile novel
  → 清除旧画像状态
  → 装载新画像
  → 重新生成平台文件
```

#### 创建自定义画像 ★新增
```
agentseed persona new my-role
  → 交互式向导：
    1. 定义 SOUL (Who I Am)
    2. 选择基础画像作为模板
    3. 添加/移除 Skills
    4. 配置 MCP 工具
    5. 设定互斥关系
  → 生成 personas/my-role/ 完整目录
```

### 3.4 Persona 市场 ★远期

```
agentseed persona search "data science"
  → 搜索社区画像

agentseed persona install data-scientist
  → 下载并安装社区画像
  → 自动通过 Quality Gate
```

---

## §4 发布与易用性设计

### 4.1 安装方式（按优先级）

```
# 方式 1: pip (主力)
pip install agentseed

# 方式 2: pipx (隔离安装，推荐给非 Python 用户)
pipx install agentseed

# 方式 3: 一键脚本 (零门槛)
curl -sSL https://agentseed.dev/install.sh | bash
# 或 PowerShell:
irm https://agentseed.dev/install.ps1 | iex
```

### 4.2 核心命令

```
agentseed forge           # 一键装配（自动检测环境）
agentseed forge --interactive  # 交互式选择画像（规划中）
agentseed forge --profile coding  # 指定画像
agentseed forge --intent "写小说"   # 意图路由画像
agentseed forge --dry-run     # 预览但不写入

agentseed switch --profile novel  # 切换画像（含互斥检查）

agentseed persona list        # 列出所有画像（含默认模式/能力）
agentseed persona search <q>  # 搜索社区画像
agentseed persona install <name> [--source URL]  # 从市场安装（过三关验证）
agentseed persona new <name>  # 创建自定义画像（规划中）

agentseed sync           # 同步到所有平台
agentseed sync --platform cursor  # 仅同步到某个平台

agentseed status         # 查看当前装配状态（锚点/画像/平台）
agentseed verify         # 验证规则完整性（CI 硬断言）
agentseed setup          # 零配置默认链路（检测 profile+tool+emit-constraints）
agentseed apply --profile coding --tool claude-code  # 指定画像+平台生成
```

### 4.3 发布渠道

| 渠道 | 目标用户 | 优先级 |
|------|---------|--------|
| PyPI (`pip install agentseed`) | 所有 Python 用户 | 🔴 P0 |
| GitHub Releases | 开发者 | 🔴 P0 |
| Homebrew (`brew install agentseed`) | macOS 用户 | 🟡 P2 |
| Scoop (`scoop install agentseed`) | Windows 用户 | 🟡 P2 |
| npm (`npx agentseed`) | Node.js 用户 | 🟢 P3 |
| 官网 (agentseed.dev) | 普通用户发现 | 🟡 P2 |

### 4.4 仓库结构（重构后）

```
AgentSeed/
├── README.md                    # 项目首页：定位 + 快速开始
├── pyproject.toml               # Python 包配置
├── LICENSE
│
├── core/                        # 宪法层 (不可插拔)
│   ├── governance.md            # P0 红线 & 安全协议
│   ├── constraints.yaml         # 机器可执行约束
│   ├── self-evolution.md        # ★ 自进化引擎
│   ├── agent-modes.md           # Task/Project/Autonomous
│   ├── attention-budget.md      # 指令预算 & RT 预算
│   ├── interaction.md           # 交互协议
│   ├── language-mediation.md    # 语言中介
│   ├── mcp-integration.md       # MCP 红线
│   ├── persona-router.md        # 画像路由
│   ├── dar-spec.md              # 域权威注册表
│   └── policy.rego              # OPA 策略规则
│
├── personas/                    # ★ 重命名 profiles → personas
│   ├── coding/
│   │   ├── persona.yaml        # 画像声明（manifest.yaml → persona.yaml v2 迁移）
│   │   ├── SOUL.md              # 角色身份
│   │   ├── AGENTS.md            # 领域规则
│   │   └── docs/
│   │       ├── skills/          # 技能
│   │       ├── prompts/         # 子代理提示词
│   │       └── mcp/             # 推荐 MCP 配置
│   ├── conversation/
│   ├── novel/
│   ├── interactive-novel/
│   ├── paper/
│   └── agent-builder/
│
├── capabilities/                # 能力包 (可叠加)
│   ├── research/                # 深度搜索 (含 dar/ 域权威注册)
│   │   ├── dar/                 # 域权威注册配置
│   │   ├── cap.yaml             # 能力包声明
│   │   └── prompt.md            # 能力提示词
│   ├── testing/                 # 测试
│   ├── review/                  # 代码审查
│   ├── creative/                # 创意写作
│   ├── worldbuilding/           # 世界观构建
│   ├── state-machine/           # 状态机
│   ├── npc-simulation/          # NPC 模拟
│   ├── adaptive-difficulty/     # 自适应难度
│   ├── engineering/             # 工程实践
│   ├── agent-governance/        # Agent 治理
│   └── ...
│
├── adapters/                    # 平台适配器
│   ├── claude-code/
│   ├── cursor/
│   ├── copilot/
│   └── ...
│
├── src/agentseed/                # Python 包
│   ├── __init__.py
│   ├── cli.py                   # CLI 入口 (list/setup/forge/switch/persona/status/sync/apply/verify/...)
│   ├── core.py                  # 核心 API 再导出
│   ├── sync_rules.py            # 同步引擎 (规则集构建 + 13 平台生成)
│   ├── forge.py                 # ★ 装配引擎: forge() 一键装配
│   ├── router.py                # ★ 画像路由: route()/锚点/关键词/互斥
│   ├── evolution.py             # ★ 自进化引擎: GapScore + 决策树 + Quality Gate
│   ├── market.py                # ★ Persona 市场: search/install + 三关验证
│   ├── policy_engine.py         # 约束引擎
│   ├── output_schemas.py        # 输出 Schema 校验
│   ├── sandbox.py               # 沙箱执行
│   └── llm_judge.py             # LLM-as-judge 语义合规
│
├── tests/
├── docs/
│   ├── AGENTSEED_ARCHITECTURE.md # 架构设计文档
│   ├── DIRECTORY_TREE.md         # 目录树
│   ├── V2_REFACTOR_REPORT.md     # v2 重构报告
│   └── AUDIT_LEGACY.md           # 遗留审计
│
└── scripts/
    ├── sync_rules.py            # shim（转发到 agentseed.sync_rules）
    ├── validate_rules.py        # 规则验证
    ├── inject_rules.py          # 规则注入
    └── ...
```

---

## §5 与现有仓库的映射

| 现有路径 | 新路径 | 变更说明 |
|---------|--------|---------|
| `AI-RULE/` | `AgentSeed/` | 仓库改名 |
| `core/` | `core/` | 保持，新增 `self-evolution.md`、`persona-router.md` |
| `profiles/` | `personas/` | 重命名，更直观 |
| `ai_rule/` | `src/agentseed/` | 包名改为 agentseed |
| `manifests/*.yaml` | `personas/<id>/persona.yaml` | 清单合并进画像目录 |
| `personas/<id>/docs/prompts/` | `prompts/`（画像内） | 扁平化 |
| `personas/<id>/skills/` | `skills/`（画像内） | 扁平化提升一级 |
| `capabilities/*.md` | `capabilities/<cap>/{cap.yaml,prompt.md,mcp.json}` | 能力包目录化 |
| `core/profile-router.md` | `core/persona-router.md` | 改名 |
| `adapters/` | `adapters/` | 保持 |
| `scripts/sync_rules.py` | `src/agentseed/cli.py` | CLI 统一入口 |
| `tests/` | `tests/` | 保持，更新 import 路径 |

---

## §6 下一步行动计划

### Phase 1: 品牌重塑（已完成 ✅）
- [x] 架构文档完成
- [x] 确认名字 AgentSeed
- [x] 注册 PyPI 包名 `agentseed`（可用）
- [x] 更新 `pyproject.toml` 包名
- [x] 更新 README.md 首页
- [x] `profiles/` → `personas/` 重命名
- [x] `ai_rule/` → `src/agentseed/` 重构
- [x] 全部测试通过 (69 passed, 1 skipped)

### Phase 2: 自进化引擎（已完成 ✅）
- [x] 编写 `core/self-evolution.md`（规范文档）
- [x] 实现 `src/agentseed/evolution.py`（GapScore 计算 + 决策树）
- [x] 实现 `src/agentseed/forge.py`（装配引擎，forge() 已对接 sync_rules 真实生成）
- [x] Quality Gate 三关验证骨架

### Phase 3: 画像路由 + 市场（已完成 ✅）
- [x] 实现 `src/agentseed/router.py`（锚点/关键词/显式/互斥/模式路由）
- [x] 实现 `src/agentseed/market.py`（search/install + 三关验证 + P0 约束）
- [x] CLI: `agentseed forge / switch / persona / status / sync`

### Phase 4: 发布
- [ ] PyPI 首次发布
- [ ] 一键安装脚本
- [ ] 官网/文档站

### Phase 5: Persona 市场扩展
- [ ] `agentseed persona new` 交互式向导
- [ ] 社区画像索引（注册表 API）
- [ ] Quality Gate 接入 constraints.yaml 引擎（目前为独立实现）

| 竞品 | 定位 | AgentSeed 优势 |
|------|------|-------------|
| agent-rules (steipete) | Cursor/Claude Code 统一规则文件 | 已废弃；仅编码 |
| agent-rules-books | 从书籍蒸馏编程规则 | 仅编码；无角色/无技能/无自进化 |
| ACP (AI Config Platform) | 管理 Agent 配置 + MCP | 无治理层、无多画像、无约束验证 |
| agents.md 项目 | AGENTS.md 格式标准 | 仅格式；不提供内容 |
| chatgpt_system_prompt | 收藏 system prompt | 仅收藏；无工具链 |
| **AgentSeed** | **一键给空白 Agent 注入完整大脑** | **Governance+Packs+Evolution+13平台** |

**核心差异**：别人给零件，AgentSeed 给整机。

---

*最后更新: 2026-08-03*
