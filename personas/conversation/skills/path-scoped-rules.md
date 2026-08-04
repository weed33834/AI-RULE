# 路径级规则 (Path-Scoped Rules)

> 本文档定义按文件类型自动激活的规则集。
> 是 AGENTS.md §19 路径级规则的完整实现。

## §1 规则激活机制

当编辑或创建文件时，根据文件扩展名/路径自动加载对应规则：

| 文件类型 | 路径模式 | 激活规则 |
|----------|----------|----------|
| Python 代码 | `**/*.py` | §2 Python 规则 |
| JavaScript/TypeScript | `**/*.{js,ts,jsx,tsx}` | §3 JS/TS 规则 |
| Markdown 文档 | `**/*.md` | §4 文档规则 |
| JSON/YAML 配置 | `**/*.{json,yaml,yml}` | §5 配置规则 |
| Shell 脚本 | `**/*.sh` | §6 Shell 规则 |
| 其他 | `*` | §7 通用规则 |

## §2 Python 规则

- 函数命名: snake_case
- 类命名: PascalCase
- 常量: UPPER_SNAKE_CASE
- 类型标注: 使用现代类型提示 (Python 3.9+)
- 文档字符串: 只在公共 API 添加，解释"为什么"不解释"什么"
- import 顺序: 标准库 → 第三方 → 本地

## §3 JS/TS 规则

- 变量/函数: camelCase
- 类/接口: PascalCase
- 常量: UPPER_SNAKE_CASE
- TypeScript: 优先使用 interface 而非 type
- import: 使用 ES Module 语法

## §4 文档规则

- 使用 Markdown 格式。
- 标题层级: # → ## → ###，不跳级。
- 代码块标注语言。
- 表格用于对比，列表用于步骤/并列。
- 链接使用相对路径（站内）或完整 URL（站外）。
- 中英文之间加空格。

## §5 配置规则

- JSON: 2 空格缩进，无尾逗号。
- YAML: 2 空格缩进，键名用 kebab-case。
- 不在配置文件中硬编码密钥。
- 敏感配置用环境变量引用。

## §6 Shell 规则

- 使用 `set -euo pipefail` 开头。
- 变量用双引号包裹: `"$VAR"`。
- 路径用引号: `"path/to/file"`。
- 不用 `rm -rf /` 或类似危险命令。

## §7 通用规则

- 文件编码: UTF-8。
- 换行符: LF (Unix)。
- 文件末尾: 保留一个空行。
- 行尾: 无多余空格。

## §8 与其他文档的关系

- **`tool-skill-mcp.md`**: 工具使用策略与路径级规则配合——编辑文件时先按路径激活规则，再按工具策略操作。
- **`conversation-quality.md`**: §4 文档规则与对话质量标准中的格式规范互补——前者针对文件，后者针对对话输出。
- **`security-checklist.md`**: 配置文件规则（§5）中的密钥安全与安全检查清单互补。
- **`evolution-policy.md`**: 路径级规则本身可随技能生命周期演进。
