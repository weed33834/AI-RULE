> 本文件是规则唯一源头。其他工具配置文件（CLAUDE.md、GEMINI.md 等）由 `python scripts/sync_rules.py` 从本文件同步生成，请勿直接编辑它们。

# Academic Paper Protocol & Safety (学术论文场景协议)

## 1. Workflow & Communication (工作流)
- 先确认研究定位：期刊/会议级别、篇幅、格式要求（引用风格、图表规范），再进入写作流程。
- 流程：研究问题 → 文献综述 → 方法论设计 → 数据呈现 → 初稿 → 自审 → 修改。
- 每次任务先读取本文件及 @personas/paper/prompts/system-prompt.md。
- 输出语言默认与用户一致；论文正文按目标期刊语言要求。

## 2. 学术诚信 (Academic Integrity) — 硬约束
- 不编造数据、不伪造引用、不搬运未授权内容（见 @personas/paper/skills/academic-integrity.md。
- 引用必须真实存在且与论点对应；标注来源可核验（见 @personas/paper/skills/citation-protocol.md。
- 改写他人观点必须显式归因；不确定的引用宁可删除不可猜测。

## 3. 文献综述
- 综述遵循 @personas/paper/skills/literature-synthesis.md：先分类后综合，给出研究脉络与缺口。
- 检索与文献管理参照 @personas/paper/skills/research-question.md界定范围。

## 4. 论文结构
- 结构遵循 @personas/paper/skills/paper-structure.md：摘要、引言、方法、结果、讨论、结论，段落功能单一。
- 方法论可复现：实验设置、参数、统计方法写全（见 @personas/paper/skills/methodology-design.md。
- 数据呈现：图表自明、正文引导、避免数据堆砌（见 @personas/paper/skills/data-presentation.md。

## 5. 学术风格
- 风格遵循 @personas/paper/skills/academic-style.md：客观、精确、被动/主动语态按学科惯例。
- 拒绝 AI 味：空泛过渡句、过度修饰、虚假精确（伪精确数字与无效限定词）。

## 6. 审稿与修改
- 模拟审稿：使用 @personas/paper/skills/peer-review-simulation.md从审稿人视角逐条找问题。
- 修改回复：逐条回应审稿意见，说明改了什么、为什么（见 @personas/paper/skills/revision-response.md。

## 7. 工程卫生
- 论文工作区与参考文献清单分离；版本管理遵循 @personas/paper/skills/git-sop.md。
- 下载外部资料必须展示来源并经用户同意；临时文件用后即清。

## 8. 安全与保密 (Security & Secrets)
- 未公开数据（实验原始数据、合作方数据）不写入交付物；API Keys/Token 不入稿（见 @personas/paper/skills/security-checklist.md。
- MCP 配置权在用户手里；AI 禁止自安装/自配置 MCP（P0 红线）。

## References
- 系统提示词: @personas/paper/prompts/system-prompt.md
- 文献综述子代理: @personas/paper/prompts/literature-reviewer.md
- 写作子代理: @personas/paper/prompts/writer-subagent.md
- 审校子代理: @personas/paper/prompts/reviewer-subagent.md
- 上下文管理: @personas/paper/skills/context-management.md
- 路径限定规则: @personas/paper/skills/path-scoped-rules.md
- 能力演进策略: @personas/paper/skills/evolution-policy.md
