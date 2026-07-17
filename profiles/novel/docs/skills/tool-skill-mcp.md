# Tool / Skill / MCP 关系与落地结构

> 工具是 AI 的手脚，技能是 AI 的经验，MCP 是工具的标准化封装。

## Tool（工具）

工具是 AI 执行具体操作的能力。小说创作场景下的工具分类：

| 工具类别 | 示例 | 副作用级别 |
|----------|------|-----------|
| 文件读写 | 读取/写入稿件文件 | 写操作需确认 |
| 素材检索 | Wikipedia API / OpenAlex API / 搜索引擎 | 只读 |
| 语言分析 | textstat（可读性）/ nltk（词频分析） | 只读 |
| 名字生成 | Faker（角色名/地名生成） | 只读 |
| 格式转换 | Markdown → EPUB / PDF | 只读 |
| 版本管理 | git 操作 | 写操作需确认 |

## Skill（技能）

技能是 AI 在实战中沉淀的可复用创作经验，存储在 `docs/skills/` 下。与工具的区别：工具是"能做什么"，技能是"怎么做更好"。

技能文档标准结构：
```markdown
# [技能名称]
## 适用场景
## 前置条件
## 模板/流程
## 质量检查清单
## 版本号: x.y.z
## 评估记录: [最近一次评估分数和反馈]
```

## MCP（Model Context Protocol）

MCP 是工具的标准化封装协议，允许 AI 跨平台连接外部系统。

### 创作场景 MCP 工具设计
| MCP 工具 | 功能 | 副作用级别 |
|----------|------|-----------|
| `consistency_check` | 检查角色/情节/世界观一致性 | 只读 |
| `character_generate` | 根据参数生成角色卡 | 只读 |
| `plot_deduce` | 推演情节发展可能性 | 只读 |
| `foreshadow_track` | 追踪伏笔状态 | 只读 |
| `style_analyze` | 分析文本风格特征 | 只读 |

### MCP 红线（P0）
- MCP server 默认只读，写操作需显式授权。
- AI 绝对禁止自下载/自安装/自启动/自配置 MCP。
- MCP 配置 JSON 由 AI 输出供用户审阅后手动粘贴。
- 配置位置：Trae `.trae/mcp.json` / Claude Desktop `claude_desktop_config.json` / Cursor `.cursor/mcp.json`。

## Hooks（工具执行拦截器）

| Hook 类型 | 触发时机 | 创作场景应用 |
|-----------|----------|-------------|
| PreToolUse | 文件写入前 | 检查目标路径在稿件目录内；检查内容分级合规 |
| PostToolUse | 章节写入后 | 自动更新角色状态、伏笔台账、触发一致性检查 |

## 真实性要求 / Truthfulness Requirements
- 工具描述必须如实标注功能和限制，不夸大能力。
- MCP 工具的 inputSchema 必须准确反映参数约束。
- 副作用级别标注必须真实——标注为"只读"的工具绝不能有写操作。
