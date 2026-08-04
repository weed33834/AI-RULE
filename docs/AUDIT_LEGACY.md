# AgentSeed Legacy Audit Report

> 审计日期：2026-08-04 01:09 GMT+8
> 审计范围：全量（所有 `.py`, `.md`, `.toml`, `.yaml`, `.yml`, `.json`, `.cfg`, `.ini`, `.txt`, `.sh`）
> 审计方式：只读，未修改任何文件
> 仓库根：`C:\Users\Administrator\.qclaw\workspace-tfxjjhfnjialcuju\AI-RULE`

---

## 审计摘要

| 类别 | 问题数 | 严重程度 |
|------|--------|---------|
| 中文乱码（GBK） | 0 | ✅ 无 |
| 旧路径/旧名称残留 | 26+ | 🔴 高 |
| 配置文件错误 | 5 | 🔴 高 |
| 占位文件 | 2 | 🟡 中 |
| README/文档问题 | 2 | 🟡 中 |
| 生成产物治理 | 1 | 🟡 中 |
| scripts/旧引用 | 4 | 🟡 中 |
| 版本号不一致 | 1 | 🟡 中 |
| manifests/ 目录残留 | 6 文件 | 🔴 高 |

---

## 详细审计

### 问题 1: manifests/ 目录已被删除但 git 追踪残留

**说明**：`manifests/` 目录已在 v2 重构中合并进 `personas/*/persona.yaml`。磁盘上 `manifests/` 不存在，但 git 仍追踪 6 个已删除文件（`git status --short manifests/` 显示 `D` 状态）。同时，多个源文件仍引用 `manifests/` 路径。

**git 追踪的残留文件**：
- `manifests/agent-builder.yaml` (D)
- `manifests/coding.yaml` (D)
- `manifests/conversation.yaml` (D)
- `manifests/interactive-novel.yaml` (D)
- `manifests/novel.yaml` (D)
- `manifests/paper.yaml` (D)

**代码中对 `manifests/` 的引用**：

| 文件 | 行号 | 内容 |
|------|------|------|
| `scripts/validate_rules.py` | 17 | `MANIFEST_DIR = REPO_ROOT / "manifests"` |
| `tests/test_dar.py` | 26 | `MANIFEST_DIR = os.path.join(REPO_ROOT, "manifests")` |
| `tests/test_dar.py` | 49 | `assert "profile-router" in content.lower()` |
| `tests/test_dar.py` | 134-139 | `test_manifests_enable_dar()` 函数整体 |
| `tests/test_structure.py` | 3 | `验证 core、profiles、manifests 的完整性` |
| `tests/test_structure.py` | 48 | `def test_manifests_exist():` |
| `tests/test_structure.py` | 111 | `test_manifests_exist,` |
| `core/agent-modes.md` | 4 | `Profile 可通过 manifests 声明` |
| `setup.py` | 25 | `"manifests",` — PACKAGED_SOURCES 列表中 |
| `MANIFEST.in` | - | `graft manifests` |
| `src/agentseed.egg-info/SOURCES.txt` | 61-66 | 仍列出 manifests/*.yaml 文件 |
| `CHANGELOG.md` | 38 | `在 manifests 中注册` |
| `docs/V2_REFACTOR_REPORT.md` | 多行 | 多处提及 manifests 历史变更（标记为已完成） |

**严重程度**：🔴 高 — `scripts/validate_rules.py`、`tests/test_dar.py`、`tests/test_structure.py` 现在会在 `manifests/` 不存在的环境中**必然崩溃**。

---

### 问题 2: 旧名称 `ai-rule` (pip 包名) 残留

| 文件 | 行号 | 内容 |
|------|------|------|
| `adapters/hooks/README.md` | 47 | `pip install ai-rule` |
| `adapters/hooks/README.md` | 49 | `git clone https://gitcode.com/badhope/AI-RULE.git` |
| `adapters/hooks/README.md` | 50 | `export AI_RULE_REPO=/path/to/AI-RULE` |
| `adapters/hooks/README.md` | 57 | `cp -r $AI_RULE_REPO/adapters/hooks/ ~/my-project/.ai-rule-hooks/` |
| `adapters/hooks/README.md` | 72 | `python .ai-rule-hooks/claude-code/pre_tool_use.py` |
| `adapters/hooks/README.md` | 104 | `.ai-rule/session-state.json` |
| `adapters/hooks/README.md` | 107 | `.ai-rule/session-allowed.txt` |
| `core/constraints.yaml` | 27 | `generated_by: ai-rule (hand-authored, do not auto-regenerate)` |
| `core/constraints.yaml` | 125 | `session_allowed_file: ".ai-rule/session-allowed.txt"` |
| `core/constraints.yaml` | 126 | `path_patterns: [".ai-rule/**", "tests/**", "tmp/**", "temp/**"]` |
| `core/constraints.yaml` | 236 | `请改源文件后运行 ai-rule apply` |
| `adapters/hooks/trae/sandbox-policy.json` | 26 | `这些文件由 ai-rule 自动生成` |
| `src/agentseed/sync_rules.py` | 837 | `若是 pip 安装的 ai-rule 包` |
| `personas/agent-builder/skills/advanced-patterns-safety.md` | 338 | `"args": ["-m", "ai_rule.rules_validator_mcp"]` |

**严重程度**：🔴 高 — `pip install ai-rule` 已不可用（现为 `pip install agentseed`），用户按 README 操作会失败。`.ai-rule/` 状态目录名也应迁移到 `.agentseed/`。

---

### 问题 3: 旧名称 `AI-RULE` (仓库名) 残留

| 文件 | 行号 | 内容 |
|------|------|------|
| `adapters/hooks/README.md` | 49 | `git clone https://gitcode.com/badhope/AI-RULE.git` |
| `adapters/hooks/README.md` | 50 | `export AI_RULE_REPO=/path/to/AI-RULE` |
| `adapters/hooks/README.md` | 57 | `cp -r $AI_RULE_REPO/...` |
| `.github/FUNDING.yml` | 1 | `# Funding for AI-RULE` |
| `.github/FUNDING.yml` | 6 | `custom: ["https://gitcode.com/badhope/AI-RULE"]` |
| `.github/ISSUE_TEMPLATE/config.yml` | 4 | `url: https://gitcode.com/badhope/AI-RULE/issues` |
| `personas/agent-builder/INIT-PROMPT.md` | 7,11,13 | 多处 `gitcode.com/badhope/AI-RULE` |
| `personas/coding/INIT-PROMPT.md` | 4,10,36,47 | 多处 `AI-RULE` 和 `gitcode.com/badhope/AI-RULE` |
| `personas/conversation/INIT-PROMPT.md` | 4,10,47,60 | 同上 |
| `personas/novel/INIT-PROMPT.md` | 38,51 | 同上 |
| `scripts/rule_injection_guide.md` | 15,29,41,71 | 多处 `AI-RULE` |
| `docs/DIRECTORY_TREE.md` | 4,22,41,288,300-309 | `AI-RULE/` 作为目录名 |
| `docs/V2_REFACTOR_REPORT.md` | 41 | `AI-RULE/` 目录树 |
| `docs/AGENTSEED_ARCHITECTURE.md` | 420 | 重命名对照表 `AI-RULE/ → AgentSeed/` |
| `personas/agent-builder/skills/industry-source-map.md` | 13,15,19,184,193 | `AI-RULE` 引用 |
| `docs/research/agent-concepts-survey.md` | 803,807 | 系统绝对路径中的 `AI-RULE` 目录名 |

**严重程度**：🟡 中 — `INIT-PROMPT.md` 文件引用的 URL `gitcode.com/badhope/AI-RULE` 需确认是否仍然有效（可能已重定向）。`.github` 目录下的 FUNDING/ISSUE 引用建议更新。

---

### 问题 4: 旧名称 `Rule Hub` 残留

| 文件 | 行号 | 内容 |
|------|------|------|
| `adapters/hooks/README.md` | 1 | `# Rule Hub Hook 适配器` |
| `adapters/hooks/README.md` | 44 | `### 1. 安装 Rule Hub` |
| `core/mcp-integration.md` | 3 | `Rule Hub 能力包 → MCP` |
| `core/mcp-integration.md` | 8-9 | `Rule Hub 通过...` |

**严重程度**：🟡 中 — "Rule Hub" 是废弃品牌名，应统一为 AgentSeed。

---

### 问题 5: 旧名称 `profile-router` 残留

| 文件 | 行号 | 内容 |
|------|------|------|
| `src/agentseed/sync_rules.py` | 842 | `# ── Meta Rules (按需的 core 元规则，如 profile-router) ──` |
| `src/agentseed.egg-info/SOURCES.txt` | 60 | `core/profile-router.md` |
| `src/agentseed.egg-info/SOURCES.txt` | 286 | `tests/test_profile_router.py` |
| `tests/test_dar.py` | 49 | `assert "profile-router" in content.lower()` |
| `tests/test_scenarios.py` | 23 | `"""模拟 profile-router 的关键词匹配逻辑"""` |
| `tests/test_scenarios.py` | 148 | `# 这种模糊情况 profile-router 要求询问` |
| `tests/test_skeleton.py` | 98-107 | 多处 `profile-router` |

**严重程度**：🟡 中 — 代码注释和测试中的 `profile-router` 已改为 `persona-router`，这些是代码内残留引用。`egg-info/SOURCES.txt` 残留旧文件名（但 egg-info 是构建产物，非源文件）。

---

### 问题 6: 配置错误 — setup.py PACKAGED_SOURCES 包含不存在的 `manifests/`

**文件**：`setup.py`，第 25 行

```python
PACKAGED_SOURCES = [
    "core",
    "personas",
    "capabilities",
    "manifests",    # ⚠️ 此目录已不存在
    "adapters",
    "mcp.example.json",
]
```

**影响**：`pip install / pip build` 时 `_sync_resources()` 会尝试 `shutil.copytree(ROOT / "manifests", ...)`，虽代码有 `if not src_path.exists(): continue` 防御，但打包内容中缺少 manifests（persona.yaml 已在 personas/ 下）。不影响运行但语义不正确。

**严重程度**：🔴 高 — 应移除 `"manifests"` 行。

---

### 问题 7: 配置错误 — MANIFEST.in 引用旧目录名

**文件**：`MANIFEST.in`

```ini
graft profiles    # ⚠️ 应为 graft personas
graft manifests   # ⚠️ 目录已不存在
```

**影响**：`graft profiles` 在 `profiles/` 目录不存在时无效果；`graft manifests` 在 `manifests/` 已删除的情况下同样无效。sdist 打包会缺内容。

**严重程度**：🔴 高 — 影响 sdist 打包完整性。

---

### 问题 8: 配置错误 — MANIFEST.in 引用不存在的 README 文件

**文件**：`MANIFEST.in`

```ini
include README.md README_CN.md README_JA.md
```

**现状**：仓库中只有 `README.md` 和 `README.zh.md`，不存在 `README_CN.md` 和 `README_JA.md`（已在 v2 重构中重命名为 `README.zh.md` 和 `README.ja.md`，且 `README.ja.md` 也已删除）。

**严重程度**：🔴 高 — `README_CN.md` 和 `README_JA.md` 不存在，sdist 构建时 include 静默失败。

---

### 问题 9: scripts/validate_rules.py 引用旧 manifests 路径 — 必然崩溃

**文件**：`scripts/validate_rules.py`，第 17 行

```python
MANIFEST_DIR = REPO_ROOT / "manifests"
```

**影响**：此脚本运行时，`check_profile_consistency()` → `profiles = [p.stem for p in MANIFEST_DIR.glob("*.yaml")]` 在 `manifests/` 不存在时返回空列表，所有 Profile 都被跳过。

**严重程度**：🔴 高 — 验证脚本在当前仓库中无法正常工作。

---

### 问题 10: tests/test_dar.py 引用旧 manifests 路径

**文件**：`tests/test_dar.py`

| 行号 | 问题 |
|------|------|
| 26 | `MANIFEST_DIR = os.path.join(REPO_ROOT, "manifests")` |
| 134-141 | `test_manifests_enable_dar()` 依赖 `MANIFEST_DIR` |

**影响**：此测试文件在当前仓库中运行会因 `manifests/` 不存在而**必然失败**。

**严重程度**：🔴 高。

---

### 问题 11: tests/test_structure.py 引用 manifests

**文件**：`tests/test_structure.py`

| 行号 | 内容 |
|------|------|
| 3 | `验证 core、profiles、manifests 的完整性` |
| 48 | `def test_manifests_exist():` |
| 111 | `test_manifests_exist,` |

**严重程度**：🔴 高 — 测试会失败。

---

### 问题 12: 占位文件 — router.py 和 market.py 为空

| 文件 | 大小 | 状态 |
|------|------|------|
| `src/agentseed/router.py` | 0 字节 | 空文件 |
| `src/agentseed/market.py` | 0 字节 | 空文件 |

**说明**：`docs/V2_REFACTOR_REPORT.md` 第 20 行标注为"占位"。未找到对应的测试文件（`tests/test_router.py` 和 `tests/test_market.py` 均不存在）。

**严重程度**：🟡 中 — 空占位不影响运行（import 不报错），但意味着 "Persona Market" 和 "Router" 功能尚未实现。

---

### 问题 13: 版本号不一致

| 来源 | 版本号 |
|------|--------|
| `pyproject.toml` | **2.3.0** |
| `CHANGELOG.md` 最新 | **1.4.0** (2026-07-25) |

**说明**：CHANGELOG.md 只记录到 v1.4.0，但 pyproject.toml 声明 v2.3.0。v2.0 的大规模重构（manifests→personas, profiles→personas 等）未在 CHANGELOG 中体现。`docs/V2_REFACTOR_REPORT.md` 描述了变更但 CHANGELOG 未同步。

**严重程度**：🟡 中 — 对用户的误导，用户看 CHANGELOG 只会看到 1.4.0。

---

### 问题 14: 根目录生成产物治理 — AGENTS.md 已追踪到 git

| 生成文件 | 在 .gitignore? | 是否 git 追踪? |
|----------|---------------|---------------|
| `AGENTS.md` | ✅ 是 | ✅ 是（tracked） |
| `CLAUDE.md` | ✅ 是 | ❌ 否 |
| `GEMINI.md` | ✅ 是 | ❌ 否 |
| `best_practices.md` | ✅ 是 | ❌ 否 |
| `.cursor/rules/` | ✅ 是 | — |
| `.github/copilot-instructions.md` | ✅ 是 | — |
| `.trae/rules/` | ✅ 是 | — |
| `.windsurfrules` | ✅ 是 | — |
| `.clinerules/` | ✅ 是 | — |
| `.continue/rules/` | ✅ 是 | — |
| `.amazonq/rules/` | ✅ 是 | — |
| `.lingma/rules/` | ✅ 是 | — |
| `.comate/rules/` | ✅ 是 | — |

**说明**：`AGENTS.md` 虽然在 `.gitignore` 中，但被 git 追踪（历史原因）。这是 `core/governance.md` 第 8 节特意允许的——AGENTS.md 是规则唯一源。其他生成文件正确排除。

**被忽略的平台生成文件内容问题**：所有生成的平台文件（`.amazonq/rules/project.md`、`.clinerules/project.md`、`.continue/rules/project.md`、`.github/copilot-instructions.md`、`.trae/rules/project_rules.md`、`.lingma/rules/project.md`、`.comate/rules/project.d/*.md`、`.windsurfrules.d/*.md`）的"资源根绝对路径"都硬编码了：
```
C:\Users\Administrator\.qclaw\workspace-tfxjjhfnjialcuju\AI-RULE
```
和旧文案 `ai-rule`：
```
> 3. 若是 pip 安装的 ai-rule 包...
```

**严重程度**：🟡 中 — 生成文件含本机绝对路径不洁。但 `.gitignore` 已排除它们，不影响其他开发者。`sync_rules.py` 生成的这些文案（`"若是 pip 安装的 ai-rule 包"`）需更新源。

---

### 问题 15: scripts/inject_rules.py 引用旧 mcp/ 路径

**文件**：`scripts/inject_rules.py`

| 行号 | 内容 |
|------|------|
| 39-42 | `str(ROOT / "mcp" / "validate_codebase.py")` |
| 44-46 | `str(ROOT / "mcp" / "review_code.py")` |
| 49-51 | `str(ROOT / "mcp" / "git_precommit_check.py")` |
| 54-56 | `str(ROOT / "mcp" / "generate_tests.py")` |

**说明**：`mcp/` 目录在 v2 重构中已融入各 persona 和 capabilities，但 `inject_rules.py` 仍引用旧 `mcp/` 路径。

**严重程度**：🟡 中 — 如果 MCP 工具已迁移到新位置，此脚本无法找到工具。

---

### 问题 16: core/mcp-integration.md 引用 "Rule Hub"

**文件**：`core/mcp-integration.md`

| 行号 | 内容 |
|------|------|
| 3 | `Rule Hub 能力包 → MCP` |
| 8 | `Rule Hub 通过为每个能力包添加` |
| 9 | `调用 Rule Hub 定义的工具约束` |

**严重程度**：🟡 中。

---

### 问题 17: 生成文件的文案源引用 `ai-rule` 包名

**文件**：`src/agentseed/sync_rules.py`，第 837 行

```python
"> 3. 若是 pip 安装的 ai-rule 包，规则源已随包分发..."
```

**说明**：此文案被写入所有 13 个平台的生成文件中。应改为 `agentseed`。

**严重程度**：🟡 中 — 影响所有生成文件的一致性。

---

### 问题 18: 平台目录 `.github` 中的 FUNDING/ISSUE 引用旧名称

| 文件 | 行号 | 内容 |
|------|------|------|
| `.github/FUNDING.yml` | 1 | `# Funding for AI-RULE` |
| `.github/FUNDING.yml` | 6 | `custom: ["https://gitcode.com/badhope/AI-RULE"]` |
| `.github/ISSUE_TEMPLATE/config.yml` | 4 | `url: https://gitcode.com/badhope/AI-RULE/issues` |

**严重程度**：🟡 中——这些是 GitHub/GitCode 显示给用户的公开链接。

---

### 问题 19: CHANGELOG.md 未更新到 v2.x

**文件**：`CHANGELOG.md`

**说明**：CHANGELOG 只记录到 v1.4.0 (2026-07-25)，但当前 pyproject.toml 版本是 v2.3.0。v2.0 重构（manifests→personas, 目录扁平化, capabilities 目录化, DAR 迁移等）在 CHANGELOG 中无记录。

**严重程度**：🟡 中。

---

### 问题 20: CONTRIBUTING.md 内容过时

**文件**：`CONTRIBUTING.md`

**问题**：
- 第 21 行 `python scripts/sync_rules.py` — shim 虽仍可用，但推荐方式应为 `agentseed sync` CLI
- 第 35 行提到 `skills/` 和 `mcp/` 作为顶层目录 — 但在 v2 重构中这些已融入 personas/
- 未提及新 CLI（`agentseed forge`、`agentseed switch` 等）

**严重程度**：🟡 中。

---

## 汇总：优先级排序修复清单

### 🔴 高优先级（影响正确运行）

| # | 问题 | 修复建议 |
|---|------|---------|
| 1 | `scripts/validate_rules.py:17` — `MANIFEST_DIR = "manifests"` | 改为 `PERSONAS_DIR = REPO_ROOT / "personas"`，遍历 `personas/*/persona.yaml` |
| 2 | `tests/test_dar.py:26` — `MANIFEST_DIR = "manifests"` | 改为 `personas/` 或直接解析 persona.yaml |
| 3 | `tests/test_dar.py:134-141` — `test_manifests_enable_dar()` | 重写为遍历 `personas/*/persona.yaml` |
| 4 | `tests/test_structure.py:48` — `test_manifests_exist()` | 重命名为 `test_persona_manifests_exist()` 并改为 `personas/*/persona.yaml` |
| 5 | `setup.py:25` — PACKAGED_SOURCES 含 `"manifests"` | 移除 `"manifests"` |
| 6 | `MANIFEST.in` — `graft profiles` | 改为 `graft personas` |
| 7 | `MANIFEST.in` — `graft manifests` | 移除 |
| 8 | `MANIFEST.in` — `include README_CN.md README_JA.md` | 改为 `include README.zh.md`（README.ja.md 已删除） |
| 9 | `manifests/` git 追踪残留 | `git rm manifests/*.yaml` |

### 🟡 中优先级（品牌一致性）

| # | 问题 | 修复建议 |
|---|------|---------|
| 10 | `adapters/hooks/README.md` — 多处 `ai-rule` / `AI-RULE` / `Rule Hub` | 全文替换为 `agentseed` / `AgentSeed` |
| 11 | `core/constraints.yaml` — `.ai-rule/` 路径 | 改为 `.agentseed/` |
| 12 | `core/mcp-integration.md` — "Rule Hub" | 改为 "AgentSeed" |
| 13 | `core/agent-modes.md:4` — "manifests" 文本 | 改为 "persona.yaml 文件" |
| 14 | `src/agentseed/sync_rules.py:837` — "ai-rule 包" | 改为 "agentseed 包" |
| 15 | `src/agentseed/sync_rules.py:842` — "profile-router" 注释 | 改为 "persona-router" |
| 16 | `scripts/inject_rules.py` — 旧 `mcp/` 路径 | 映射到新位置或删除 |
| 17 | 所有 `INIT-PROMPT.md` — URL `gitcode.com/badhope/AI-RULE` | 确认 URL 有效性，更新为 AgentSeed URL |
| 18 | `scripts/rule_injection_guide.md` — `AI-RULE` 引用 | 全文替换 |
| 19 | `.github/FUNDING.yml` / `config.yml` — `AI-RULE` URL | 更新为 AgentSeed URL |
| 20 | `personas/agent-builder/skills/industry-source-map.md` — `AI-RULE` | 改为 `AgentSeed` |
| 21 | `docs/DIRECTORY_TREE.md` — `AI-RULE/` 目录名 | 改为 `AgentSeed/` |

### 🔵 低优先级（改进建议）

| # | 问题 | 修复建议 |
|---|------|---------|
| 22 | `CHANGELOG.md` — 缺少 v2.0+ 记录 | 补写 v2.0.0 ~ v2.3.0 变更日志 |
| 23 | `CONTRIBUTING.md` — 过时流程 | 添加 `agentseed forge` CLI 流程，更新 skills/mcp 路径说明 |
| 24 | `src/agentseed/router.py` / `market.py` — 空占位 | 实现或添加 `# TODO` 注释说明计划 |
| 25 | 测试注释中的 `profile-router` | 全文替换为 `persona-router` |
| 26 | `adapters/hooks/trae/sandbox-policy.json:26` — `ai-rule` | 改为 `agentseed` |
| 27 | `personas/agent-builder/skills/advanced-patterns-safety.md:338` — `ai_rule` | 改为 `agentseed` |
| 28 | `personas/agent-builder/skills/advanced-patterns.md:709` — `agentcreater` | 确认是否为新包名或需修改 |
| 29 | `scripts/rule_injection_guide.md` — 全文 `AI-RULE` | 改为 `AgentSeed` |

### ⚪ 无需处理

| 项目 | 原因 |
|------|------|
| 中文 GBK 乱码 | 所有 persona.yaml (6 个) 和 core/*.md (6 个) 均为 UTF-8，无乱码 |
| `docs/V2_REFACTOR_REPORT.md` 中的 AI-RULE/manifests 引用 | 历史文档，记录已完成的重构，无需修改 |
| `docs/AGENTSEED_ARCHITECTURE.md:406/423/441` | 历史对照表，记录已完成的重命名，无需修改 |
| `src/agentseed.egg-info/` | 构建产物目录，由 `pip install` 自动生成，无需手动维护 |
| 平台生成文件中的绝对路径 `C:\Users\...` | `.gitignore` 已排除，不影响其他开发者 |
| `CHANGELOG.md` 中的 "manifests"、"AgentCreater" | 历史日志，如实反映当时的命名 |

---

## 作弊条：一键修复命令（供参考，不执行）

```bash
# 1. 移除 git 追踪的 manifests 残留
git rm manifests/*.yaml

# 2. 修复 MANIFEST.in
sed -i 's/graft profiles/graft personas/' MANIFEST.in
sed -i '/graft manifests/d' MANIFEST.in
sed -i 's/README_CN.md README_JA.md/README.zh.md/' MANIFEST.in

# 3. 修复 setup.py — 移除 manifests
sed -i '/"manifests",/d' setup.py

# 4. 更新 sync_rules.py 中的文案
sed -i 's/ai-rule 包/agentseed 包/g' src/agentseed/sync_rules.py
sed -i 's/profile-router/persona-router/g' src/agentseed/sync_rules.py

# 5. 全文替换旧品牌名（审核后执行）
# adapters/hooks/README.md, core/constraints.yaml, core/mcp-integration.md,
# .github/FUNDING.yml, .github/ISSUE_TEMPLATE/config.yml,
# personas/*/INIT-PROMPT.md, scripts/rule_injection_guide.md, etc.
```
