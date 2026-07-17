# 路径级条件规则 (Path-Scoped Rules)

> 不同文件类型自动激活不同规则集，减少上下文窗口占用。

## §1 路径-规则映射表

| 文件路径模式 | 激活的规则集 | 检查项 |
|-------------|-------------|--------|
| `docs/manuscript/*.md` 或 `*.txt` | 创作规则 | 去 AI 文学味（§2）、Show don't tell、角色对话个性化、内容分级合规 |
| `.ai-memory/characters/*.md` | 角色一致性 | 角色卡模板完整、性格/动机/能力/弧光齐全、与前文一致 |
| `.ai-memory/worldbuilding.md` | 世界观自洽 | 规则无矛盾、科技/力量体系与设定一致、地理/历史/文化匹配 |
| `.ai-memory/plot-threads.md` | 伏笔追踪 | 伏笔台账格式规范、状态准确、超期预警 |
| `.ai-memory/creative-blueprint.md` | 创作蓝图 | 种子信息完整、大纲结构合理 |
| `docs/skills/*.md` | 技能文档 | 标准结构完整、版本号、评估记录 |
| `scripts/*.py` | 代码安全 | pip-audit 通过、无硬编码密钥、路径穿越防护 |
| `AGENTS.md` | 规则源头 | 版本号、引用完整性、@ 引用路径有效 |

## §2 条件加载示例

### Claude Code 条件加载
```json
{
  "condition": {
    "filePattern": "docs/manuscript/**/*.md",
    "rules": [
      "docs/skills/world-building.md",
      "docs/skills/character-crafting.md",
      "docs/skills/plot-architecture.md",
      "docs/skills/dialogue-crafting.md",
      "docs/skills/scene-crafting.md"
    ]
  },
  "condition": {
    "filePattern": ".ai-memory/characters/*.md",
    "rules": [
      "docs/skills/character-crafting.md"
    ]
  }
}
```

### 规则激活逻辑
- 当 AI 操作 `docs/manuscript/` 下的文件时，自动加载全部创作技能文档。
- 当 AI 操作 `.ai-memory/characters/` 下的文件时，只加载角色塑造技能。
- 当 AI 操作 `scripts/` 下的文件时，只加载安全检查清单。
- 这样做减少了上下文窗口占用——不需要同时加载所有规则。

## §3 稿件文件特殊规则

当处理 `docs/manuscript/` 或 `.txt` 稿件文件时，以下规则**强制激活**：

1. **去 AI 文学味（AGENTS.md §2）**：检查模板化叙事、陈词滥调、机器感文风。
2. **Show, Don't Tell**：标记直接告知情感的位置。
3. **角色对话个性化**：检查不同角色说话方式是否有差异。
4. **内容分级合规（AGENTS.md §5.2）**：检查是否越级。
5. **内部一致性**：角色行为、世界观规则、时间线。
6. **伏笔追踪**：检查新增和回收的伏笔。

## §4 .ai-memory 特殊规则

当处理 `.ai-memory/` 下的文件时：
- **只读优先**：先读取已有内容，再追加或更新，不覆盖。
- **格式规范**：遵循各文件类型的模板格式。
- **增量更新**：只更新变化的部分，不重写整个文件。
