# AgentSeed 场景包市场（PACK_MARKET）

> 仓库即市场：用户拿到的是**最小基础内核**，上层场景包按需选择安装，不要求全量克隆。

---

## 1. 使用模型

```
用户（克隆/安装）                AgentSeed 仓库 = 市场
┌────────────────────┐          ┌────────────────────────────┐
│ 最小基础内核          │          │  personas/                 │
│  core/ 治理内核       │  ──按需──▶ │    coding      ✓ 基础包    │
│  adapters/ 平台适配   │  pack add  │    conversation 可安装     │
│  src/ CLI+引擎       │          │    novel        可安装     │
│  personas/coding    │          │    paper        可安装     │
└────────────────────┘          │    agent-builder 可安装     │
  你的项目里：                    └────────────────────────────┘
  personas/<自建包>/     ←── pack new + pack publish 回传市场
```

- **最小基础**：core + 平台适配 + coding 开发包。开箱即用：`agentseed forge` 即出规则。
- **按需增强**：`pack add novel` 只拉取 novel 一个包（sparse 单目录），不克隆全仓库。
- **自建包**：`pack new` 生成模板 → 编辑 → `pack publish` 校验并生成回传市场的 PR 材料。
- **互斥引用宽容**：本地未安装但市场存在的包，校验只警告不报错。

## 2. 最小基础克隆（sparse，推荐）

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/weed33834/agentseed.git
cd agentseed
git sparse-checkout set core adapters src scripts docs .github \
  personas/coding \
  capabilities/engineering capabilities/testing capabilities/review \
  capabilities/agent-governance capabilities/research \
  pyproject.toml setup.py LICENSE
agentseed forge --profile coding        # 立即可用
```

## 3. pack 命令速查

```bash
agentseed pack list                     # 市场包清单（含已安装状态）
agentseed pack list --json              # JSON 输出（供脚本/Agent 消费）
agentseed pack add novel                # 按需安装单个场景包（Quality Gate 前置）
agentseed pack add <id> --source <url>  # 从任意 git 仓库/市场源安装
agentseed pack remove novel             # 移除（git 仓库内 git rm 可恢复；否则入 .trash）
agentseed pack new my-scenario --name "我的场景" --scenario "数据分析"
agentseed pack publish my-scenario      # 校验 + 生成回传市场的提交/PR 材料
```

> 兼容：`agentseed persona install/search` 仍可用（社区包安装），pack 是其演进形态。

## 4. 创建新场景包（用户视角）

```bash
cd <你的项目>
agentseed pack new my-scenario --name "我的场景" --scenario "面向 XX 场景的规则包"
# 生成:
#   personas/my-scenario/persona.yaml       # 包清单（互斥/能力白名单/路由锚点/关键词）
#   personas/my-scenario/AGENTS.md          # 场景协议（P2 层，不得覆盖 P0）
#   personas/my-scenario/prompts/system-prompt.md
#   personas/my-scenario/skills/            # 技能（可选，按需加载）
```

编辑后发布：

```bash
agentseed pack publish my-scenario   # 结构校验通过 → 输出 git/PR 指引
```

回传市场（发布回路）：Fork 主仓库 → `git add personas/<id>` → commit → PR。
合并后任何用户 `agentseed pack add <id>` 即可获取。

## 5. 安全与约束

- **Quality Gate 前置**：从市场拉取的包先过安全/质量/兼容三关才落盘（复用 `market.run_gates`）。
- **MCP 红线**：包内 MCP 仅输出配置 JSON，绝不自动安装。
- **互斥宽容**：`validate_packs` 对"市场存在但本地未安装"的互斥引用只警告（装内核后可用）。
- 自建包结构规范：见 `docs/SCENARIO_PACK_SPEC.md`。

## 6. 实现

- 市场源：默认 `https://github.com/weed33834/agentseed.git`，可用 `AGENTSEED_MARKET` 环境变量或 `--source` 覆盖。
- 单包拉取：`git clone --depth 1 --filter=blob:none --sparse` + `sparse-checkout set personas/<id>`。
- 代码：`src/agentseed/pack.py`；CLI：`agentseed pack`；校验：`scripts/validate_packs.py`（市场感知）。
