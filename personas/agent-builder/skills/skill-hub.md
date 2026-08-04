# Skill Hub / 技能导航索引

## One-line Description / 一句话描述

> 将散落在各大开源仓库和平台中的 AI 技能、提示词、MCP 工具资源整理为统一导航索引，让智能体按需精准定位，而非盲目搜索。
>
> A unified navigation index that organizes scattered AI skills, prompts, and MCP tool resources across major open-source repositories and platforms, enabling agents to locate what they need precisely instead of searching blindly.

---

## When to Use / 适用场景

- 智能体需要某个领域的专业技能（如 Stripe 支付集成、Cloudflare Workers 部署）时，查找已验证的现成技能 / Finding verified ready-made skills for a specific domain
- 需要为大厂 AI 平台（Claude Code、Codex、Cursor 等）安装技能时，查找各平台的正确安装路径 / Finding correct installation paths for major AI platforms
- 需要参考大厂真实系统提示词设计时，查找合法来源 / Finding legitimate sources for major-vendor system prompt references
- 需要 MCP 工具扩展智能体外部能力时，查找可用的 MCP 服务器 / Finding available MCP servers to extend agent capabilities
- 评估一个技能是否值得安装时，使用质量评估标准 / Evaluating whether a skill is worth installing

---

## Core Methodology / 核心方法论

### 资源分类体系 / Resource Classification

AI 技能生态目前分散在四类仓库中，每类解决不同层面的问题：

```
┌─────────────────────────────────────────────────────┐
│              用户需求 / User Need                     │
└──────────────────────┬──────────────────────────────┘
                       ▼
    ┌──────────────────┼──────────────────┐
    ▼                  ▼                  ▼
┌────────┐     ┌────────────┐     ┌──────────┐
│ 开发技能 │     │ 提示词/角色  │     │ MCP 工具  │
│ Coding │     │ Prompts    │     │ MCP      │
│ Skills │     │ & Roles    │     │ Servers  │
└───┬────┘     └─────┬──────┘     └────┬─────┘
    ▼                ▼                 ▼
┌────────┐     ┌────────────┐     ┌──────────┐
│awesome-│     │f/awesome-  │     │awesome-  │
│agent-  │     │chatgpt-    │     │mcp-      │
│skills  │     │prompts     │     │servers   │
│        │     │            │     │          │
│obra/   │     │ai-boost/   │     │MCPgee    │
│super-  │     │awesome-    │     │          │
│powers  │     │prompts     │     │abordage/ │
│        │     │            │     │awesome-  │
│Composio│     │系统提示词   │     │mcp       │
│HQ/     │     │泄露收集    │     │          │
│awesome-│     │            │     │          │
│claude- │     │            │     │          │
│skills  │     │            │     │          │
└────────┘     └────────────┘     └──────────┘
```

---

## Category 1: Coding Skills (开发技能) / 开发技能仓库

### 1.1 awesome-agent-skills

| 属性 | 值 |
|------|-----|
| **仓库** | `VoltAgent/awesome-agent-skills` |
| **收录量** | 1000+ SKILL.md |
| **来源** | Anthropic、Google Labs、Vercel、Stripe、Cloudflare、Netlify 等官方团队 + 社区 |
| **兼容平台** | Claude Code、Codex、Antigravity、Gemini CLI、Cursor、Windsurf、GitHub Copilot、OpenCode |
| **协议** | 开源 |
| **核心优势** | 100% 真实工程团队产出（非 AI 批量生成），有标准安装路径表，每个技能含 YAML frontmatter + 真实代码示例 |
| **适用场景** | 需要框架特定最佳实践、API 参考、代码模式、工具工作流 |
| **浏览方式** | GitHub 仓库 / [LobeHub Skills](https://lobehub.com/skills) / [officialskills.sh](https://officialskills.sh) |
| **局限** | 偏重开发类技能，缺少对话型/业务型智能体技能 |
| **URL** | https://github.com/VoltAgent/awesome-agent-skills |

### 1.2 ComposioHQ/awesome-claude-skills

| 属性 | 值 |
|------|-----|
| **收录量** | 社区最全的 Claude Skills 合集 |
| **Stars** | 21.7k+（截至 2026 年） |
| **兼容平台** | Claude Code 为主 |
| **核心优势** | 一站式收录官方 + 社区技能，被称为 Claude Skills 生态的"应用商店" |
| **适用场景** | 专门给 Claude Code 找技能 |
| **局限** | 偏 Claude 生态，其他平台兼容性未验证 |
| **URL** | https://github.com/ComposioHQ/awesome-claude-skills |

### 1.3 obra/superpowers

| 属性 | 值 |
|------|-----|
| **收录量** | 工程化方法论技能集 |
| **Stars** | 210k+（截至 2026 年） |
| **兼容平台** | Claude Code、Codex 等 8 个平台 |
| **协议** | MIT |
| **核心优势** | 不是单个技能，而是一整套工程化方法论：TDD red/green、YAGNI、DRY、子 Agent 隔离（spec → plan → tasks → implement） |
| **适用场景** | 需要系统化提升 AI 编程交付质量，而非单个功能技能 |
| **局限** | 偏方法论，不提供具体框架/API 的技能 |
| **URL** | https://github.com/obra/superpowers |

### 1.4 mattpocock/skills

| 属性 | 值 |
|------|-----|
| **收录量** | TypeScript 为主 |
| **Stars** | 110k+（截至 2026 年） |
| **兼容平台** | Claude Code（`.claude/skills/`） |
| **核心优势** | 覆盖代码审查、测试、重构等 TypeScript 开发场景 |
| **适用场景** | TypeScript/JavaScript 项目开发 |
| **局限** | 语言覆盖面窄 |
| **URL** | https://github.com/mattpocock/skills |

---

## Category 2: Prompts & Roles (提示词/角色) / 提示词仓库

### 2.1 f/awesome-chatgpt-prompts

| 属性 | 值 |
|------|-----|
| **收录量** | 1000+ 提示词 |
| **覆盖领域** | 编程、写作、教育、设计、商业等 20+ 领域 |
| **核心优势** | GitHub 上 Star 数最高的提示词仓库，社区活跃 |
| **适用场景** | 找角色扮演提示词、对话型智能体人设模板 |
| **局限** | 偏 ChatGPT 早期格式，部分提示词未针对 Agent 场景优化 |
| **URL** | https://github.com/f/awesome-chatgpt-prompts |

### 2.2 ai-boost/awesome-prompts

| 属性 | 值 |
|------|-----|
| **收录量** | 从 GPTs Store 高分作品中提取的提示词 |
| **核心优势** | 来源是实际高评分 GPTs，质量有市场验证 |
| **适用场景** | 参考高质量 GPTs 的提示词设计 |
| **URL** | https://github.com/ai-boost/awesome-prompts |

### 2.3 系统提示词参考收集

| 属性 | 值 |
|------|-----|
| **收录范围** | Anthropic(Claude)、OpenAI(GPT-5.x)、Google(Gemini)、xAI(Grok)、Microsoft(Copilot)、Cursor 等的真实系统提示词 |
| **关注量** | 53k+ 开发者关注 |
| **核心优势** | 了解大厂真实系统提示词的结构和约束设计 |
| **重要警告** | 这些是泄露/逆向工程获取的提示词，**非官方授权**。仅可作为设计参考，不得直接复制使用。参考时需遵守各厂商服务条款。 |
| **URL** | https://www.everydev.ai/tools/system-prompts-leaks |

---

## Category 3: MCP Servers (MCP 工具) / MCP 工具仓库

### 3.1 awesome-mcp-servers (mcpservers.org)

| 属性 | 值 |
|------|-----|
| **收录量** | 数百个精选 MCP 服务器 |
| **覆盖领域** | 代码执行、数据库查询、浏览器自动化、文件系统、版本控制、家庭控制、医疗数据、金融分析等 |
| **核心优势** | 高质量精选（非全量索引），每个 MCP 有分类标签和官方/社区标注 |
| **适用场景** | 找特定领域的 MCP 工具扩展智能体能力 |
| **URL** | https://mcpservers.org/ |

### 3.2 MCPgee

| 属性 | 值 |
|------|-----|
| **收录量** | 7625+ 开发者工具 MCP 服务器 |
| **核心优势** | 全量索引，搜索能力强，可按平台/语言/安装方式筛选 |
| **适用场景** | 需要尽可能多的选择时 |
| **局限** | 收录量大但质量参差，需自行评估 |
| **URL** | https://www.mcpgee.com/ |

### 3.3 abordage/awesome-mcp

| 属性 | 值 |
|------|-----|
| **核心优势** | 每日自动更新，涵盖 MCP 服务器/客户端/框架 |
| **适用场景** | 跟踪 MCP 生态最新动态 |
| **URL** | https://github.com/abordage/awesome-mcp |

---

## Category 4: Skill Browsing Platforms (技能浏览平台) / 浏览平台

| 平台 | URL | 特点 |
|------|-----|------|
| **LobeHub Skills** | https://lobehub.com/skills | 可搜索的技能浏览平台，按分类组织，支持在线预览 SKILL.md |
| **officialskills.sh** | https://officialskills.sh | 浏览/搜索/复制技能 URL，支持按分类筛选 |
| **ClaudSkills** | https://claudskills.com | Claude 技能对比和评级，多维度横向比较 |
| **agentskillshub.dev** | https://agentskillshub.dev | 提示词库评测和推荐，含 Top 10 榜单 |

---

## Decision Tree: Where to Find What / 选型决策树

```
你需要什么？
│
├─ 框架/API 的开发技能（如 Stripe、Cloudflare、React Native）
│  └─ awesome-agent-skills (VoltAgent)
│     → 找官方团队产出的 SKILL.md，按安装路径表复制到对应 Agent 目录
│
├─ Claude Code 专用技能
│  └─ ComposioHQ/awesome-claude-skills
│     → 社区最全的 Claude Skills 合集
│
├─ 工程化方法论（TDD、代码审查流程、子 Agent 隔离）
│  └─ obra/superpowers
│     → 安装整套方法论，不是单个功能技能
│
├─ 角色扮演提示词 / 对话型智能体人设
│  └─ f/awesome-chatgpt-prompts
│     → 20+ 领域 1000+ 提示词，按角色查找
│
├─ 参考大厂系统提示词设计（仅参考，不直接复制）
│  └─ everydev.ai/system-prompts-leaks
│     → 了解结构，自行设计原创提示词
│
├─ MCP 工具（数据库、浏览器、文件系统等外部能力）
│  ├─ 精选高质量 → awesome-mcp-servers (mcpservers.org)
│  └─ 全量搜索 → MCPgee (7625+ 索引)
│
├─ 浏览/对比技能（不知道选哪个）
│  └─ LobeHub Skills / officialskills.sh / ClaudSkills
│
└─ 本仓库 AgentCreater 没有的技能
   └─ 先查 awesome-agent-skills，再查 awesome-claude-skills
      → 找到后评估质量（见下方评估标准），合格才安装
```

---

## Installation Paths by Agent / 各 Agent 平台技能安装路径

| Agent | Skill 路径 | 文档 |
|-------|-----------|------|
| **Claude Code** | `.claude/skills/` | https://docs.anthropic.com/claude/docs/skills |
| **Codex** | `.codex/skills/` | https://codex.ai/docs/skills |
| **Antigravity** | `.antigravity/skills/` | https://antigravity.dev/docs |
| **Gemini CLI** | `.gemini/skills/` | https://gemini.google.com/cli |
| **Cursor** | `.cursor/skills/` | https://cursor.sh/docs |
| **Windsurf** | `.windsurf/skills/` | https://windsurf.ai/docs |
| **GitHub Copilot** | `.github/copilot-instructions.md` | https://docs.github.com/copilot |
| **Trae** | `.trae/rules/` | https://docs.trae.ai |
| **OpenCode** | `.opencode/skills/` | https://opencode.ai/docs |

### 安装示例 / Installation Example

```bash
# Claude Code 安装 Stripe 技能示例
mkdir -p .claude/skills
curl -o .claude/skills/stripe-best-practices.md \
  https://raw.githubusercontent.com/VoltAgent/awesome-agent-skills/main/skills/stripe/stripe-best-practices.md

# 验证技能文件格式
head -10 .claude/skills/stripe-best-practices.md
# 应包含 YAML frontmatter: name, description, triggers
```

---

## Skill Quality Evaluation / 技能质量评估标准

安装前按以下标准评估技能质量：

| 评估维度 | 合格标准 | 不合格信号 |
|---------|---------|-----------|
| **来源** | 官方团队或知名社区贡献者 | 匿名账号、无维护记录 |
| **真实性** | 含真实代码示例（非占位符 `// TODO`） | 全是伪代码或 `placeholder` |
| **文档** | 有 YAML frontmatter（name/description/triggers） | 无元数据，纯文本 |
| **测试** | 声明已在至少一个 AI Agent 上测试过 | 无测试说明 |
| **维护** | 最近 3 个月内有更新 | 超过 1 年未更新 |
| **安全** | 密钥用环境变量，无硬编码 | 硬编码 API Key / Token |
| **实用性** | 解决实际问题，有使用场景说明 | 纯理论，无落地场景 |
| **许可证** | 明确开源协议（MIT/Apache/BSD） | 无许可证或 proprietary |

### 质量评估检查清单

- [ ] 来源可追溯（官方团队或知名贡献者）
- [ ] 含真实代码示例（非占位符）
- [ ] 有 YAML frontmatter 元数据
- [ ] 声明已在 AI Agent 上测试
- [ ] 最近 3 个月内有更新
- [ ] 无硬编码密钥
- [ ] 有明确的实用场景
- [ ] 有开源许可证

---

## Common Pitfalls / 常见陷阱

| 陷阱 | 后果 | 解决方案 |
|------|------|---------|
| 直接复制泄露的系统提示词 | 违反厂商服务条款，法律风险 | 仅作设计参考，自行编写原创提示词 |
| 安装未经测试的社区技能 | 可能含错误指令或安全漏洞 | 安装前用质量评估标准检查 |
| 技能安装到错误路径 | Agent 无法识别技能 | 查安装路径表，确认目标 Agent 的正确目录 |
| 安装过多技能 | 上下文窗口被占满，核心指令被稀释 | 只安装当前项目需要的技能，按需加载 |
| 不检查技能许可证 | 引入 GPL/AGPL 依赖，影响项目商用 | 检查许可证，商业项目只用 MIT/Apache/BSD |
| 盲信技能内容 | 技能中的 API 可能过时或错误 | 安装后验证关键 API 是否真实可用（AGENTS.md §1 真实性铁律） |

---

## Truthfulness Requirements / 真实性要求（对应 AGENTS.md §1）

- **仓库地址真实**：本文档列出的所有 GitHub 仓库 URL 均来自实际搜索结果，但安装前建议再次访问确认仓库存在且活跃。
- **Stars 数据有时效性**：标注的 Stars 数量是截至 2026 年 7 月的数据，实际数量可能已变化。
- **不盲目推荐**：本导航索引只收录有实际证据的仓库，不编造不存在的资源。
- **局限性标注**：每个仓库都标注了局限，不隐瞒缺陷。
- **泄露提示词警告**：系统提示词收集类仓库已明确标注"非官方授权，仅可参考"，不得直接复制使用。

---

## Checklist / 检查清单

- [ ] 已明确需要哪类资源（开发技能/提示词/MCP 工具）
- [ ] 按选型决策树找到了对应的仓库
- [ ] 确认目标 Agent 的技能安装路径
- [ ] 对找到的技能执行了质量评估（8 项标准）
- [ ] 确认技能许可证兼容项目要求
- [ ] 安装后验证了技能内容的关键 API 是否真实可用
- [ ] 未直接复制泄露的系统提示词
