# Forge 装配全链路（Forge Workflow）

> `agentseed forge` 是一条完整的"空白 Agent → 装备齐全"流水线。
> 本文档定义装配时的**检测 → 路由 → 进化补能力 → 质量门 → 生成 → 钩子**全链路。

## 1. 概览

```
┌────────────────────────────────────────────────────────────┐
│                    agentseed forge                         │
│                                                            │
│  ① detect_environment()   检测锚点 + 平台 + 能力信号 + 缺口   │
│            │                                               │
│  ② route()                路由画像                          │
│     显式 > 锚点 > 意图 > fallback；歧义则要求澄清             │
│            │                                               │
│  ③ 进化补能力 (Evolution in forge)  ★核心新增               │
│     detect_gap() → GapScore → 建议/推荐能力包                │
│     - 检测到 tests/ → 建议 testing 能力包                    │
│     - 检测到 references.bib → 建议 research                 │
│     - 检测到 chapters/ → 建议 creative                      │
│            │                                               │
│  ④ 用户确认（interactive 模式）                             │
│     - 展示环境报告 + 画像列表 + GapScore + 建议能力包          │
│     - 用户可确认当前 / 切换画像 / 中止                       │
│            │                                               │
│  ⑤ build_ruleset()       组装规则集（宪法+画像+能力包）       │
│            │                                               │
│  ⑥ Quality Gate          三关验证（安全/质量/兼容）           │
│            │                                               │
│  ⑦ write_tool_file()     生成 13 平台入口文件                │
│  ⑧ emit_constraints()    分发平台钩子（6 平台）              │
└────────────────────────────────────────────────────────────┘
```

## 2. 各阶段详解

### ① 环境检测（detect_environment）

| 检测项 | 信号 | 输出 |
|--------|------|------|
| 目录锚点 | `pyproject.toml`→coding、`chapters/`→novel、`references.bib`→paper… | `anchors_found` |
| 平台配置 | `.claude`、`.cursor`、`.github/copilot-instructions.md`… | `platforms_detected` |
| 已有入口 | `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` | `existing_rules` |
| **能力信号** ★ | `tests/`→testing、`docs/`→research、`chapters/`→creative… | `detected_capabilities` |
| **工具缺口** ★ | 有无 `.mcp.json` / `skills/` / `requirements.txt` | `tool_gap` (0-1) |

### ② 画像路由（route）

按 `persona-router.md §2` 优先级：显式 > 锚点 > 意图 > fallback。
歧义（多锚点冲突）→ 抛错要求 `--profile` 显式指定。

### ③ 进化补能力（Evolution in forge）★ 核心新增

**设计理念**：装配不是"选个画像就完事"——AgentSeed 在装配时就用自进化引擎评估"这个画像配这个项目够不够"。

```
GapScore = 0.35×MissingTool + 0.25×MissingKnowledge + 0.20×Urgency
         + 0.10×AlternativeExhausted + 0.10×RiskOfAction

装配时计算：
  MissingTool      = 1.0 - (项目工具信号得分)   → 无任何工具信号=1.0
  MissingKnowledge = 检测到能力信号但画像未覆盖的比例
  Urgency          = 0.6（装配场景默认）
  Risk             = LOW（装配是低风险写文件）
```

**能力包建议逻辑**：

```
遍历 detected_capabilities（项目里检测到的能力信号）：
  若 cap ∉ 当前画像的 allowed_capabilities
  且 cap ∉ forbidden_capabilities
  且 capabilities/<cap>/ 存在
  → 加入 capabilities_suggested（建议装配）
```

例如：项目里有 `tests/` 目录 + 检测到 `game-state-machine.md`，但当前路由到 coding 画像 → 建议加 `testing`（已在 coding 白名单）但**不**建议 `state-machine`（coding 禁止项）。

### ④ 用户确认（interactive 模式）

`agentseed forge --interactive` 打印：

```
AgentSeed forge: 环境检测报告
  工作目录  : /path/to/project
  检测锚点  : pyproject.toml
  检测平台  : claude-code, cursor
  推断画像  : coding (mode=project, rt=STANDARD)
  当前能力  : research, testing, review, agent-governance, dar
  检测到信号: testing
  GapScore  : 0.45 → recommend
  建议      : 输出搜索关键词 / 推荐链接供用户手动查阅
  建议能力包: testing (检测到但当前画像未启用)
  可用画像: (6 个列表 + 当前/推荐标记)
请选择画像 [直接回车确认为 'coding']:
```

用户可：回车确认 / 输入其他画像 ID 切换 / `a` 中止。

### ⑤⑥ 规则集组装 + 质量门

- `build_ruleset()`：CORE（P0 宪法，始终内联）+ PROFILE 主层 + ON-DEMAND INDEX。
- Quality Gate 三关（evolution.py 真实实现）：
  - **安全关**：扫描密钥 / .git 残留 / 可疑可执行文件
  - **质量关**：结构完整（persona.yaml / SOUL.md）
  - **兼容关**：与活跃画像互斥检查
- 安全关失败 → 警告但仍生成（供用户检查）；质量/兼容失败 → 记录警告。

### ⑦⑧ 生成 + 钩子

- `write_tool_file()`：13 平台入口（限长平台自动分片）。
- `emit_constraints()`：6 个支持 hook 的平台分发 pre-tool-use 检查脚本 + constraints.yaml。

## 3. CLI 接口

```
agentseed forge                    # 自动检测 → 路由 → 装配（非交互）
agentseed forge --interactive      # 环境报告 + 用户确认
agentseed forge --profile coding   # 显式指定画像
agentseed forge --intent "写小说"   # 意图路由
agentseed forge --tool claude-code # 指定平台
agentseed forge --dry-run          # 预览（不写入）
agentseed forge --output /path     # 输出到指定目录
```

## 4. 设计原则

1. **装配即进化**：装大脑时就用自进化引擎评估缺口，不是事后诸葛亮。
2. **建议而非强制**：能力包建议只提示，不自动添加（除非用户确认）。
3. **P0 红线不变**：Quality Gate 三关约束，密钥/MCP 红线始终生效。
4. **非交互默认安全**：无 `--interactive` 时自动装配，不阻塞用户。
5. **单一事实源**：锚点/白名单/互斥全部来自 router.py 注册表，forge 只消费不复制。

## 5. 与运行时进化的关系

| 阶段 | 引擎 | 触发 | 动作 |
|------|------|------|------|
| 装配时 | forge + evolution | `agentseed forge` | 检测缺口 → 建议能力包 → 三关验证 |
| 运行时 | Agent 按 self-evolution.md 协议 | 会话中遇能力缺口 | 算 GapScore → 搜索/克隆/安装/建议 |
| 会话中 | session-refresh.md 协议 | 规则更新 | 重新读取入口文件应用新规则 |

三者构成完整闭环：**装的时候补好 → 用的时候自己补 → 规则变了会刷新**。
