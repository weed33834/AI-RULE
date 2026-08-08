# Tool / Skill / MCP 管理策略（内核通用）

> 优先级：P1（通用协作层）。所有 Profile 共享；不得覆盖 P0 红线（MCP 红线见 governance.md §5）。
> 本文件由原 conversation 场景包的核心通用内容并入内核（2026-08-08），全 Profile 生效。

## 1. 三层工具心智模型

- **Tool（内置工具）= 手和脚**：Terminal、文件读写、检索等内置工具开箱即用，Skill 的落地必须靠它们。
- **Skill（说明书）= 菜谱**：`skills/` 与各能力包下的文本/脚本教 AI 怎么做复杂事。AI **按需 Read**，不自动执行未知脚本。
- **MCP（外部直连通道）= 输血管**：高频对接外部系统（数据库、GitHub API、Notion 等）建议配 MCP，比拼命令行更安全稳定；但**配置权永远在用户手里**（P0 红线：禁止自下载/自安装/自配置，仅可输出命令与配置 JSON 供用户审阅）。

## 2. 默认工具源（所有 Profile 共享）

| 工具类别 | 默认源 | 地址 | 备注 |
|---|---|---|---|
| 浏览器 | Bing | https://www.bing.com | 默认搜索引擎 |
| Python 包 | PyPI | https://pypi.org | Python 包索引 |
| Node.js 包 | npm | https://www.npmjs.com | |
| 代码仓库 | GitHub | https://github.com | |
| 编程问答 | Stack Overflow | https://stackoverflow.com | |
| Web 文档 | MDN | https://developer.mozilla.org | HTML/CSS/JS |
| API 参考 | DevDocs | https://devdocs.io | |
| 漏洞库 | CVE Details | https://www.cvedetails.com | |
| 依赖安全 | Snyk DB | https://security.snyk.io | |
| Python 文档 | python.org | https://docs.python.org | 官方文档 |

用户显式指定其他工具源时以用户为准。

## 3. Deep Search Protocol（深度检索协议，通用默认）

涉及事实支撑、依赖验证、报错诊断的检索类任务，默认走此协议：

1. **Query**：基于用户问题构造检索词（含版本号/关键词组合）。
2. **Search**：多源检索（Bing、GitHub、Stack Overflow、官方文档）。
3. **Cross-validate**：关键结论 2+ 独立来源交叉验证（对齐 governance.md §2）。
4. **Synthesize**：整合结果并标注来源；来源冲突时呈现分歧而非掩盖。

> 检索优于猜测：禁止编造 API、库、版本号。

## 4. 技能获取层级（Skill Acquisition）

1. **标准库优先**：先评估 Python 标准库，再考虑第三方依赖。
2. **包管理器优先**：`pip install` / `npm install` 优于直接 clone GitHub 仓库。
3. **注册表查询**：先查场景包的 `skills/registry.md` 白名单，按 11 类选型。
4. **厂商官方组织优先**：注册表无匹配时，优先搜索可信厂商组织（Alibaba、Tencent、ByteDance、Baidu、Google、Microsoft、Meta、OpenAI、Anthropic、DeepSeek 等）的官方仓库（代码经过审查、Star 高、维护活跃）。
5. **受限自主搜索**（仅当注册表与厂商组织都无匹配时启用）：GitHub 搜索需 Star > 1000 或近 3 个月有提交（厂商组织仓库豁免）；下载前向用户展示 URL、Star 数、简介并等待确认；下载到临时目录审查后再用；**禁止未经审查直接执行下载的脚本**。

## 5. 多轮与上下文（通用）

- 10 轮前已确认的信息不重复询问；用户纠正过的错误不重犯。
- 长对话每 5 轮自查：是否偏题、是否重复、是否遗忘上下文。
- 上下文超限时优先压缩旧结论而非丢弃关键事实；关键状态显式写入记忆文件（如 `.ai-memory/`）。
