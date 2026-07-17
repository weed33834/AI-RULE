# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/)，版本号参考语义化版本。

## [1.1.0] — 2026-07-17

### 新增

- **指令预算 (Instruction Budget)**：`core/governance.md` 新增指令预算章节，基于 ManyIFEval (ICLR 2025) 研究限制同时激活的规则数量（P0 ≤5，总计 ≤12）。
- **位置效应 (Position Effects)**：`context-engineering.md` 新增 Lost in the Middle 现象说明与双端放置策略。
- **反模式库 (Anti-Patterns)**：新增 `anti-patterns.md`，收录 5 种已过时的提示词技术（全大写、纯否定、手动 CoT 等）及迁移清单。
- **扩展思考 (Extended Thinking)**：`prompt-patterns.md` 新增模式 8，指导使用模型原生推理预算替代手动 CoT。
- **三层行为边界**：`safety-guardrails.md` 行为边界声明重构为 Allowed / Confirmation Required / Forbidden 三层结构。
- **GUID 分隔符注入防御**：`safety-guardrails.md` 输入标记层新增随机 GUID 分隔符方案，防止标记闭合逃逸攻击。
- **NeMo 自检模板**：`safety-guardrails.md` 新增 `self_check_input` 和 `self_check_output` 配置模板。
- **弃权协议 (Abstention Protocol)**：`truth-protocol.md` 新增弃权协议章节，允许说"我不知道"并防止虚张声势。
- **自我精炼 (Self-Refinement)**：新增 `self-refinement.md`，涵盖 Reflexion 循环、Constitutional 自我批评、轻量级自检流程。
- **规则理由 (Rationale)**：`governance.md` 全部 P0 规则补充 Rationale（存在理由）说明。

### 变更

- 所有 5 套系统提示词统一添加语言中介协议（输入端 + 输出端），实现自动语言检测、英语推理、用户语言输出。
- `coding` 系统提示词移除硬编码中文，统一为通用语言中介协议。
- `safety-guardrails.md` YAML 模板 `input_marking` 新增 `guid_delimiter` 配置项。
- 负面指令重构：将"严禁/绝不"纯否定式约束改为正向表达 + 条件逻辑。

### 修复

- README.md 从中文改为英文（GitHub 国际化），添加 shields.io 徽章与语言切换链接。
- README_JA.md 从旧版（仅 coding）重写为完整 5-profile 结构。
- README_CN.md 添加徽章与研究驱动优化章节。
- `agent-builder` manifest 补全 `anti-patterns.md` 和 `self-refinement.md` 引用。
- `agent-builder` AGENTS.md 补全反模式与自我精炼的技能引用。

### 测试

- 5 套测试套件，40 项检查，全部通过。

## [1.0.0] — 2026-07-16

- 初始版本：5 套 Profile 合并发布（coding / conversation / novel / interactive-novel / agent-builder）。
