# AgentSeed v2 产品化重构完成报告

**时间**: 2026-08-04 00:44  
**状态**: ✅ 全部完成，69 passed / 1 skipped

## 完成的 12 项改动

### 目录结构重组
1. ❌ manifests/ → ✅ 合并进 personas/ 的 persona.yaml
2. ❌ personas/<id>/docs/prompts/ → ✅ personas/<id>/prompts/（扁平化）
3. ❌ personas/<id>/docs/skills/ → ✅ personas/<id>/skills/（扁平化）
4. ❌ personas/<id>/docs/templates/ → ✅ personas/<id>/templates/（agent-builder 专属）
5. ❌ capabilities/*.md 单文件 → ✅ capabilities/<cap>/{cap.yaml,prompt.md,mcp.json} 目录化
6. ❌ capabilities/dar/ → ✅ capabilities/research/dar/（合并进 research）
7. ❌ 顶层 skills/ → ✅ 已融入各 persona/skills/
8. ❌ 顶层 mcp/ → ✅ 已融入各 persona 或 capabilities
9. ❌ 顶层 README.ja.md → ✅ 已删除
10. ✅ 新增 `core/persona-router.md`（从 profile-router 改名）
11. ✅ 新增 `src/agentseed/router.py` + `market.py`（占位）
12. ✅ 根目录生成产物保持 gitignore 治理

### 代码级改动
- `src/agentseed/sync_rules.py`: MANIFEST_DIR → PERSONAS_DIR，所有 `(x/"manifests")` → `(x/"personas")` 资源检测
- `parse_manifest()`: `manifests/{id}.yaml` → `personas/{id}/persona.yaml`
- `list_profiles()`: glob *.yaml → 遍历 persona 目录 + persona.yaml 存在性
- 所有 capability 路径: `capabilities/{cap}.md` → `capabilities/{cap}/prompt.md`
- DAR 路径: `capabilities/dar/` → `capabilities/research/dar/`
- `core.py`、`__init__.py`、`scripts/sync_rules.py` shim 全部同步 `PERSONAS_DIR` 导出
- 6 个 `persona.yaml` 文件路径引用全部更新（docs/ → flat）
- 7 个测试文件路径引用全部更新

### 测试修复
- `test_packaged.py`: 假资源目录 manifests→personas
- `test_audit.py`: manifests/*.yaml→personas/*/persona.yaml，AGENTS.md 缺失时 skip
- `test_structure.py`: docs/ → prompts/ or skills/，manifest→persona.yaml，缩进修复
- `test_skeleton.py`: capabilities/research/prompt.md 替代目录级 read_text
- `test_persona_router.py`（从 test_profile_router 改名）

### 最终仓库结构
```
AI-RULE/
├── core/                 # 13 文件 P0 宪法层
├── personas/             # 6 个 Persona Pack
│   ├── _template/default/
│   ├── coding/           # prompts/ skills/
│   ├── conversation/
│   ├── novel/
│   ├── interactive-novel/
│   ├── paper/
│   └── agent-builder/    # + templates/
├── capabilities/         # 17 个能力包目录
│   ├── research/dar/     # DAR 注册表
│   ├── testing/
│   ├── review/
│   ├── engineering/
│   ├── creative/
│   ├── game-engine/
│   ├── worldbuilding/
│   ├── npc-simulation/
│   ├── state-machine/
│   ├── adaptive-difficulty/
│   ├── agent-governance/
│   ├── novel-chapter-deliverable-mode/
│   └── orchestration/
├── adapters/             # 13 平台适配层
├── src/agentseed/        # Python 包
│   ├── sync_rules.py     # 核心生成器
│   ├── cli.py            # CLI 入口
│   ├── evolution.py      # 自进化引擎
│   ├── forge.py          # 装配引擎
│   ├── router.py         # Persona 路由（新）
│   └── market.py         # 市场分发（新）
├── scripts/
├── tests/                # 69 passed, 1 skipped
└── docs/
```

## 验证结果
- ✅ pytest: **69 passed, 1 skipped**, 19.11s
- ✅ `agentseed list`: 6 Profile + 13 Tool 全部可用
- ✅ 资源根检测: cwd 模式正常
- ❌ git remote 仍是旧地址（用户需自行改名或新建仓库推送）
