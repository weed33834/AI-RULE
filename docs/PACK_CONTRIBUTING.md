# 场景包贡献指南（PACK_CONTRIBUTING）

> 面向想要**自建场景包**或**向市场贡献包**的开发者。配套规范见 `docs/SCENARIO_PACK_SPEC.md`，市场机制见 `docs/PACK_MARKET.md`。

---

## 1. 包的类型体系

AgentSeed 的"包"分四类，贡献前先分清你要做的是哪一种：

| 类型 | 层级 | 特性 | 位置 | 谁能加 |
|---|---|---|---|---|
| **场景规则包 (Scenario Pack)** | L1 | 互斥、可插拔，面向任务场景 | `personas/<id>/` | 任何人（市场机制） |
| **能力插件 (Capability Plugin)** | L2 | 叠加、按需加载 | `capabilities/<cap>/` | 任何人（评审） |
| **平台适配 (Platform Adapter)** | L3 | 输出格式 + 拦截钩子 | `adapters/` + `platform import` | 任何人（PR） |
| **内核规则 (core/)** | L0 | 不可变、全场景生效 | `core/*.md` | 仅 maintainer 评审 |

### 场景包的分类（persona.yaml 的 `category` 字段，可选）

| category | 含义 | 示例 |
|---|---|---|
| `dev` | 开发类：编码/工程/运维 | coding |
| `creative` | 创作类：小说/文案/设计 | novel |
| `research` | 研究类：论文/调研/分析 | paper |
| `strategic` | 战略类：Agent 构建/架构/治理 | agent-builder |
| `general` | 通用/未归类 | （内核 default） |

## 2. 三种贡献路径

### 路径 A：自建包，自己用（推荐入门）

```bash
cd <你的项目>
agentseed pack new my-scenario --name "我的场景" --scenario "面向 XX 场景" --category research
# 编辑 personas/my-scenario/ 下的清单/协议/提示词
agentseed pack publish my-scenario      # 结构校验，通过即可在本地 forge 使用
agentseed forge --profile my-scenario   # 装配出规则文件
```

自用包建议：
- 分类写清楚（`category`），便于日后发布时归类。
- 互斥清单按真实冲突声明（不互斥就不要列）。
- 能力白名单只启用真需要的能力（`enables_capabilities`），禁用的写 `forbids_capabilities`。

### 路径 B：发布到市场（仓库即市场）

```bash
agentseed pack publish my-scenario   # 校验通过 → 生成 git/PR 材料
```

然后：
1. Fork `https://github.com/weed33834/agentseed`
2. 检出你的 fork，`git add personas/my-scenario` → commit → push
3. 开 Pull Request（PR 模板见 `.github/PULL_REQUEST_TEMPLATE.md`，选"场景包贡献"）
4. 合并后任何用户 `agentseed pack add my-scenario` 即可获取

### 路径 C：贡献能力插件 / 平台适配

- 能力插件：新建 `capabilities/<cap>/{cap.yaml,prompt.md,mcp.json}`，cap.yaml 声明 id/name/适用场景；被某场景包 `enables` 引用即可生效。
- 平台适配：`agentseed platform import <id> --entry <path> --format markdown --hook-dir <dir>`，按提示补 hook。

## 3. 提交 PR 前自查清单（CI 会拦什么）

- [ ] `python scripts/validate_packs.py` 通过（结构/引用/能力/互斥）
- [ ] persona.yaml 的 id == 目录名，`mutually_exclusive_with` 对称
- [ ] includes 引用的文件全部存在且非空（缺失会直接导致 forge 产物 `[missing]`）
- [ ] 无硬编码密钥；不包含 `.git` 目录；MCP 只给配置 JSON 不自动安装
- [ ] 若改了 core/，附理由（内核变更需 maintainer 评审）
- [ ] 本地 `python -m pytest tests/ -q` 全绿

## 4. 评审标准（maintainer 视角）

- **可装配**：`forge --profile <新包>` 产物无 `[missing]`。
- **不越权**：P2 场景层不覆盖 P0 红线；互斥合理。
- **可维护**：prompts/skills 文件有清晰职责；引用路径正确。
- **文档齐**：包内 AGENTS.md 有场景协议与 References。

## 5. 常见坑

- 引用未入库文件 → 产物 `[missing]`（校验器会拦）。
- 互斥不对称（A 列 B、B 不列 A）→ 校验器会拦。
- 改动 core/ 后未重新生成平台产物 → `agentseed sync --profile coding` 重新生成。
- 自建包 ID 用 `^[a-z0-9-]+$`（小写+连字符），不要用中文/空格。
