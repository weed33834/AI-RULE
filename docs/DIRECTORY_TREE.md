# 仓库目录结构

> 生成时间：2026-08-04  
> 说明：本仓库为 **AgentSeed / AI-RULE** 项目，是 AI Agent 规则引擎与多 Persona 管理框架。

---

```
workspace-tfxjjhfnjialcuju/                 ← 🏠 仓库根目录
│
├── .consolidate-state.json                 # 会话合并状态跟踪
├── .qclaw-version                          # QClaw 版本标识
├── AGENTS.md                               # AI Agent 行为规范与技能路由入口
├── HEARTBEAT.md                            # 心跳/活跃度记录
├── IDENTITY.md                             # Agent 身份定义
├── MEMORY.md                               # 长期记忆存储
├── SOUL.md                                 # Agent 灵魂/人格设定
├── TOOLS.md                                # 本地工具与开发环境备注
├── USER.md                                 # 用户画像与偏好
├── AgentKit转型方案_20260803.md             # AgentKit 转型方案文档
├── AgentSeed_v2产品化重构_20260804.md        # AgentSeed v2 产品化重构方案
├── AI-RULE开发记录_20260803.md              # AI-RULE 开发日志
│
├── .openclaw/                              # 🔧 QClaw 运行时内部配置
│   └── workspace-state.json                # 工作区状态快照
│
├── .pytest_cache/                          # 🧪 Pytest 缓存目录（自动生成）
│   └── v/
│       └── cache/
│
├── memory/                                 # 📝 会话记忆日志（按日期）
│   ├── 2026-07-11.md
│   ├── 2026-07-12.md
│   ├── 2026-07-24.md
│   └── 2026-07-26.md
│
├── skills/                                 # 🧩 Agent 内置技能插件
│   └── 09-python全栈工程师/
│       └── SKILL.md                        # Python 全栈工程师技能定义
│
└── AI-RULE/                                # ⭐ 核心项目：AI Agent 规则引擎
    │
    ├── 📄 项目级文档
    │   ├── README.md                       # 英文项目说明
    │   ├── README.zh.md                    # 中文项目说明
    │   ├── PROJECT.md / project.md         # 项目概览
    │   ├── CHANGELOG.md                    # 变更日志
    │   ├── CITATION.cff                    # 学术引用格式
    │   ├── CONTRIBUTING.md                 # 贡献指南
    │   ├── CODE_OF_CONDUCT.md              # 行为准则
    │   ├── SECURITY.md                     # 安全策略
    │   ├── LICENSE                         # 开源许可证
    │   ├── best_practices.md               # 最佳实践
    │   ├── copilot-instructions.md         # GitHub Copilot 指令
    │   └── mcp.example.json                # MCP 配置示例
    │
    ├── 🔨 构建与安装
    │   ├── setup.py                        # Python setuptools 安装脚本
    │   ├── pyproject.toml                  # Python 项目元数据
    │   └── MANIFEST.in                     # 分发包文件清单
    │
    ├── 🧠 Agent 指引（面向主流 AI IDE / 平台）
    │   ├── AGENTS.md                       # agents.md 规则
    │   ├── CLAUDE.md                       # Claude Code 规则
    │   ├── GEMINI.md                       # Gemini CLI 规则
    │   ├── project.md                      # 项目级指令（通用）
    │   └── .windsurfrules                  # Windsurf 规则入口
    │
    ├── 📁 .amazonq/                        # Amazon Q 适配
    │   └── rules/
    │       └── project.md                  # 项目规则注入
    │
    ├── 📁 .clinerules/                     # Cline 适配（目录占位）
    │
    ├── 📁 .comate/                         # Comate 适配
    │   └── rules/
    │       ├── project.mdr                 # 项目规则
    │       └── project.d/                  # 项目子规则目录
    │
    ├── 📁 .continue/                       # Continue 适配
    │   └── rules/
    │       └── project.md                  # 项目规则注入
    │
    ├── 📁 .cursor/                         # Cursor 适配
    │   └── rules/
    │       └── project.mdc                 # Cursor 项目规则
    │
    ├── 📁 .github/                         # GitHub 社区文件
    │   ├── FUNDING.yml                     # 赞助配置
    │   ├── PULL_REQUEST_TEMPLATE.md        # PR 模板
    │   └── ISSUE_TEMPLATE/
    │       ├── bug_report.md               # Bug 报告模板
    │       ├── config.yml                  # 议题配置
    │       ├── new_tool_support.md         # 新工具支持模板
    │       └── rule_improvement.md         # 规则改进模板
    │
    ├── 📁 .lingma/                         # Lingma (通义灵码) 适配
    │   └── rules/
    │       ├── project.md                  # 项目规则
    │       └── project.d/                  # 项目子规则
    │
    ├── 📁 .trae/                           # Trae (字节) 适配
    │   └── rules/
    │       └── project_rules.md            # Trae 项目规则
    │
    ├── 📁 .windsurfrules.d/                # Windsurf 规则集
    │   ├── INDEX.md                        # 规则索引入口
    │   ├── 01-core-layer-01.md ~ 04.md     # 核心层规则 1-4
    │   ├── 05-profile-layer-01.md ~ 03.md  # Profiling 层规则 1-3
    │   └── 08-on.md                        # 上线开关规则
    │
    │
    ├── 📁 core/                            # 🏛️ 核心规则引擎（规范化配置文件）
    │   ├── agent-modes.md                  # Agent 模式定义
    │   ├── attention-budget.md             # 注意力预算/Token 管理
    │   ├── constraints.yaml                # 约束规则
    │   ├── dar-spec.md                     # DAR (Dynamic Agent Rules) 规范
    │   ├── governance.md                   # 治理与合规规则
    │   ├── interaction.md                  # 人机交互协议
    │   ├── language-mediation.md           # 语言中介/翻译规则
    │   ├── mcp-integration.md              # MCP 集成规范
    │   ├── mode-overrides.yaml             # 模式覆盖配置
    │   ├── persona-router.md               # Persona 路由规则
    │   ├── policy.rego                     # OPA 策略引擎规则
    │   └── self-evolution.md               # 自我进化/Auto-tuning 规则
    │
    ├── 📁 capabilities/                    # 🎯 原子能力模块（可插拔）
    │   ├── adaptive-difficulty/            # 自适应难度调节
    │   ├── agent-governance/               # Agent 治理
    │   ├── creative/                       # 创意生成
    │   ├── engineering/                    # 工程化 + MCP (mcp.json)
    │   ├── game-engine/                    # 游戏引擎
    │   ├── novel-chapter-deliverable-mode/ # 小说章节交付模式
    │   ├── npc-simulation/                 # NPC 模拟
    │   ├── orchestration/                  # 编排/工作流
    │   ├── research/                       # 研究能力
    │   │   └── dar/                        # DAR 研究配置
    │   │       ├── README.md               # DAR 使用说明
    │   │       ├── dar-agent-builder.yaml
    │   │       ├── dar-coding.yaml
    │   │       ├── dar-conversation.yaml
    │   │       ├── dar-interactive-novel.yaml
    │   │       ├── dar-novel.yaml
    │   │       └── dar-paper.yaml
    │   ├── review/                         # 代码/内容评审 + MCP (mcp.json)
    │   ├── state-machine/                  # 状态机驱动
    │   ├── testing/                        # 测试自动化 + MCP (mcp.json)
    │   └── worldbuilding/                  # 世界观构建
    │
    ├── 📁 personas/                        # 👤 Persona 定义（人格模板）
    │   ├── _template/                      # 模板
    │   │   └── default/                    # 默认模板
    │   ├── agent-builder/                  # Agent 构建者
    │   │   ├── prompts/                    # 提示词
    │   │   ├── skills/                     # 技能定义
    │   │   └── templates/                  # 模板文件
    │   ├── coding/                         # 编程助手
    │   │   ├── prompts/
    │   │   └── skills/
    │   ├── conversation/                   # 对话助手
    │   │   ├── prompts/
    │   │   └── skills/
    │   ├── interactive-novel/              # 互动小说
    │   │   ├── prompts/
    │   │   └── skills/
    │   ├── novel/                          # 小说创作
    │   │   ├── prompts/
    │   │   └── skills/
    │   └── paper/                          # 学术论文
    │       ├── prompts/
    │       └── skills/
    │
    ├── 📁 provenance/                      # 📦 Persona 配置资产（分平台/角色 JSON）
    │   ├── agent-builder-claude-code.json  # Agent Builder → Claude Code
    │   ├── agent-builder-comate.json       # Agent Builder → Comate
    │   ├── agent-builder-lingma.json       # Agent Builder → Lingma
    │   ├── agent-builder-windsurf.json     # Agent Builder → Windsurf
    │   ├── coding-agents-md.json           # Coding → agents.md
    │   ├── coding-amazon-q.json            # Coding → Amazon Q
    │   ├── coding-claude-code.json         # Coding → Claude Code
    │   ├── coding-cline.json               # Coding → Cline
    │   ├── coding-comate.json              # Coding → Comate
    │   ├── coding-continue.json            # Coding → Continue
    │   ├── coding-copilot.json             # Coding → Copilot
    │   ├── coding-cursor.json              # Coding → Cursor
    │   ├── coding-gemini.json              # Coding → Gemini
    │   ├── coding-lingma.json              # Coding → Lingma
    │   ├── coding-qodo.json                # Coding → Qodo
    │   ├── coding-trae.json                # Coding → Trae
    │   ├── coding-windsurf.json            # Coding → Windsurf
    │   ├── conversation-agents-md.json     # Conversation → agents.md
    │   ├── conversation-amazon-q.json      # Conversation → Amazon Q
    │   ├── conversation-claude-code.json   # Conversation → Claude Code
    │   ├── conversation-cline.json         # Conversation → Cline
    │   ├── conversation-comate.json        # Conversation → Comate
    │   ├── conversation-continue.json      # Conversation → Continue
    │   ├── conversation-copilot.json       # Conversation → Copilot
    │   ├── conversation-cursor.json        # Conversation → Cursor
    │   ├── conversation-gemini.json        # Conversation → Gemini
    │   ├── conversation-lingma.json        # Conversation → Lingma
    │   ├── conversation-qodo.json          # Conversation → Qodo
    │   ├── conversation-trae.json          # Conversation → Trae
    │   ├── conversation-windsurf.json      # Conversation → Windsurf
    │   ├── interactive-novel-claude-code.json
    │   ├── novel-claude-code.json
    │   ├── novel-cursor.json
    │   └── paper-claude-code.json
    │
    ├── 📁 adapters/                        # 🔌 平台适配器
    │   ├── hooks/                          # 钩子脚本
    │   │   ├── claude-code/                # Claude Code 钩子
    │   │   │   ├── pre_tool_use.py         # 工具调用前置钩子
    │   │   │   └── settings.json.template  # 设置模板
    │   │   ├── cline/                      # Cline 钩子
    │   │   │   ├── hooks.json.template     # 钩子配置模板
    │   │   │   └── pre_tool_use.py         # 工具调用前置钩子
    │   │   ├── codex/                      # Codex 钩子
    │   │   │   ├── hooks.json.template
    │   │   │   └── pre_tool_use.py
    │   │   ├── cursor/                     # Cursor 钩子
    │   │   │   ├── hooks.json.template
    │   │   │   └── pre_tool_use.py
    │   │   ├── gemini/                     # Gemini 钩子
    │   │   │   ├── hooks.json.template
    │   │   │   └── pre_tool_use.py
    │   │   ├── shared/                     # 共享检查逻辑
    │   │   │   └── check.py                # 通用校验函数
    │   │   └── trae/                       # Trae 钩子
    │   │       └── sandbox-policy.json     # 沙箱策略
    │   └── trae/                           # Trae 适配
    │       └── session-guardrails.md       # 会话护栏规则
    │
    ├── 📁 scripts/                         # 🛠️ 运维/注入/同步脚本
    │   ├── build_dar_md.py                 # 构建 DAR markdown
    │   ├── generate_mcp_config.py          # 生成 MCP 配置
    │   ├── inject_memory.py                # 注入记忆到 Agent
    │   ├── inject_rules.py                 # 注入规则到 Agent
    │   ├── sync_rules.py                   # 同步规则
    │   ├── validate_rules.py               # 验证规则完整性
    │   └── rule_injection_guide.md         # 规则注入指南
    │   └── __pycache__/                    # Python 缓存
    │
    ├── 📁 src/                             # 📦 Python 包源码（agentseed）
    │   ├── agentseed/
    │   │   ├── __init__.py                 # 包入口
    │   │   ├── cli.py                      # CLI 入口
    │   │   ├── core.py                     # 核心引擎
    │   │   ├── evolution.py                # 规则进化/突变
    │   │   ├── forge.py                    # 规则锻造/生成
    │   │   ├── llm_judge.py                # LLM 评判器
    │   │   ├── market.py                   # 规则市场/分发
    │   │   ├── policy_engine.py            # OPA 策略引擎封装
    │   │   ├── router.py                   # Persona 路由器
    │   │   ├── sandbox.py                  # 沙箱执行
    │   │   ├── sync_rules.py               # 规则同步
    │   │   ├── output_schemas.py           # 输出 Schema 定义
    │   │   └── __pycache__/                # Python 缓存
    │   └── agentseed.egg-info/             # setuptools 元数据
    │       ├── dependency_links.txt
    │       ├── entry_points.txt
    │       ├── PKG-INFO
    │       ├── SOURCES.txt
    │       └── top_level.txt
    │
    ├── 📁 tests/                           # 🧪 测试套件
    │   ├── conftest.py                     # Pytest 共享 fixtures
    │   ├── test_audit.py                   # 审计测试
    │   ├── test_dar.py                     # DAR 引擎测试
    │   ├── test_packaged.py                # 打包/分发测试
    │   ├── test_persona_router.py          # Persona 路由测试
    │   ├── test_scenarios.py               # 场景测试
    │   ├── test_skeleton.py                # 骨架测试
    │   ├── test_structure.py               # 结构完整性测试
    │   ├── test_sync.py                    # 同步测试
    │   ├── dar-evaluation/                 # DAR 评估数据集
    │   │   └── logs/                       # 评估日志
    │   └── __pycache__/
    │
    ├── 📁 docs/                            # 📚 项目文档
    │   ├── AGENTSEED_ARCHITECTURE.md       # AgentSeed 架构设计文档
    │   ├── architecture.svg                # 架构图 SVG
    │   ├── usage.svg                       # 使用图 SVG
    │   ├── V2_REFACTOR_REPORT.md           # v2 重构报告
    │   ├── DIRECTORY_TREE.md               # 📌 本文件：目录结构树
    │   └── research/
    │       └── agent-concepts-survey.md    # Agent 概念调研
    │
    └── .pytest_cache/                      # Pytest 缓存（顶层 AI-RULE 内）
        └── v/
            └── cache/
```

---

## 目录角色速览

| 路径 | 角色 |
|------|------|
| **根目录 7 个 .md** | Agent 身份 / 记忆 / 行为准则 / 用户画像 |
| `AI-RULE/` | 核心项目：AI Agent 规则引擎 |
| `AI-RULE/core/` | 规则引擎核心配置：模式、约束、治理、进化等 |
| `AI-RULE/capabilities/` | 14 个可插拔原子能力模块 (cap.yaml + prompt.md) |
| `AI-RULE/personas/` | 6 种 Persona 模板 (agent-builder / coding / conversation / novel / interactive-novel / paper) |
| `AI-RULE/provenance/` | 34 个 JSON - Persona × 平台 的交叉配置资产 |
| `AI-RULE/adapters/hooks/` | 各 AI IDE 的 pre_tool_use 钩子脚本 |
| `AI-RULE/scripts/` | 规则注入 / 同步 / 校验运维脚本 |
| `AI-RULE/src/agentseed/` | Python 包：CLI、路由、进化、策略引擎、评判器等 |
| `AI-RULE/tests/` | Pytest 测试套件 |
| `AI-RULE/docs/` | 架构文档、重构报告、调研 |
| `skills/` | Agent 内置技能插件 |
| `memory/` | 按日期记录的会话记忆日志 |
| `.github/` | Issue/PR 模板、赞助配置 |
