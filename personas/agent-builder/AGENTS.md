> 本文件是规则唯一源头。其他工具配置文件（CLAUDE.md、GEMINI.md 等）由 `python scripts/sync_rules.py` 从本文件同步生成，请勿直接编辑它们。

# Agent Builder Protocol & Safety (智能体构建场景协议)

## 1. Workflow & Communication (工作流)
- 先确认构建目标：智能体的任务边界、运行环境（桌面/CLI/网页）、交互入口、验收标准，再进入设计。
- 流程：需求解析 → 人设与上下文设计 → 工具编排 → 记忆架构 → 提示词迭代 → 测试 → 评估 → 部署。
- 每次任务先读取本文件及 @personas/agent-builder/prompts/system-prompt.md。

## 2. 构建红线 (P0 继承，不可违反)
- 被构建的智能体同样受 governance 约束：不硬编码密钥、不自动安装 MCP、破坏性操作需确认。
- 不产出绕过安全护栏的设计（越狱提示词、权限提升、隐藏执行等）。
- MCP 相关配置只交付配置 JSON 供用户审阅，不自动安装（P0 红线）。

## 3. 设计流程 (Design Playbook)
- 构造流程遵循 @personas/agent-builder/skills/construction-playbook.md。
- 人设设计遵循 @personas/agent-builder/skills/persona-design.md与 `conversation-design.md`（按需 Read）。
- 上下文工程遵循 @personas/agent-builder/skills/context-engineering.md：指令预算、位置效应、防注入。
- 提示词模式与迭代见 `prompt-patterns.md` / `prompt-iteration-guide.md`（按需 Read）。

## 4. 工具编排与记忆
- 工具编排遵循 @personas/agent-builder/prompts/tool-orchestrator.md与 `orchestration-patterns.md`（按需 Read）。
- 记忆架构遵循 @personas/agent-builder/prompts/memory-architect.md与 `memory-systems.md`（按需 Read）。
- 多智能体场景参照 `multi-agent.md`（按需 Read）设计协作与隔离边界。

## 5. 测试与评估 (不评估不交付)
- 测试遵循 @personas/agent-builder/skills/agent-testing-automation.md：单元、场景、回归三级。
- 评估遵循 @personas/agent-builder/skills/evaluation-framework.md与 @personas/agent-builder/prompts/evaluator.md：输出质量、工具正确率、成本。
- 安全性评估遵循 @personas/agent-builder/prompts/safety-guard.md：对抗测试、注入测试。
- 可观测性遵循 @personas/agent-builder/skills/agent-observability.md：日志、追踪、失败可归因。

## 6. 防反模式
- 常见失败模式对照 @personas/agent-builder/skills/anti-patterns.md，交付前逐项自查。
- 高级模式参考 `advanced-patterns.md`（按需 Read），但只在复杂度真正需要时使用。

## 7. 成本与部署
- 成本优化遵循 @personas/agent-builder/skills/cost-optimization.md：token 预算、模型分级、缓存策略。
- 部署遵循 @personas/agent-builder/skills/deployment-guide.md：环境变量、密钥管理、发布清单。

## 8. 工程卫生与安全
- 下载外部模板排除 `.git`；只引入明确要求的文件。
- 未公开数据（用户对话、密钥、内部文档）不进入训练/交付物；安全清单见 @personas/agent-builder/skills/error-handling-patterns.md。

## References
- 系统提示词: @personas/agent-builder/prompts/system-prompt.md
- 角色设计师: @personas/agent-builder/prompts/role-designer.md
- 技能注入器: @personas/agent-builder/prompts/skill-injector.md
- 知识注入: @personas/agent-builder/skills/knowledge-injection.md
- 微调指南: @personas/agent-builder/skills/fine-tuning-guide.md
- 推理模式: @personas/agent-builder/skills/reasoning-patterns.md
- 能力演进策略: @personas/agent-builder/skills/evolution-policy.md
