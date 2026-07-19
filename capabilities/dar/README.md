# Domain Authority Registry (DAR)

> DAR（域权威注册表）为每个领域预置权威源名录、打分规则、检索通道和领域知识。
> 规范定义见 `core/dar-spec.md`。

## 为什么需要 DAR

传统搜索"全网乱搜→取前几条"存在三大问题：
1. 来源不可控——SEO 垃圾可能排在首位。
2. 权威性无法量化——没有统一标准。
3. 领域知识缺失——不同领域对时效性、共识性要求不同。

DAR 通过预置权威源名录、打分公式、路由规则和领域知识，让搜索行为更有指向性。

## 模块结构

每个领域的 DAR 配置包含 6 个模块：

| 模块 | 作用 |
|------|------|
| `source_registry` | T1-T4 四档权威源名录 |
| `scoring_protocol` | 打分权重配置（α/β/γ/δ） |
| `routing_rules` | 查询路由规则（trigger → priority_sources） |
| `domain_knowledge` | 领域专属术语、规范、陷阱 |
| `conflict_policy` | 冲突处理策略 |
| `prefix_templates` | 自适应前缀模板（standard + extended） |

## 领域配置

| Profile | 配置文件 | 重点 |
|---------|----------|------|
| paper | `dar-paper.yaml` | 顶刊名录 + 引用验证 + 撤稿检查 |
| coding | `dar-coding.yaml` | 开发工具/资源平台/漏洞库 |
| conversation | `dar-conversation.yaml` | 事实核查/统计数据/新闻源 |
| novel | `dar-novel.yaml` | 词典/词源/人名/写作规范 |
| interactive-novel | `dar-interactive-novel.yaml` | 引擎文档/游戏设计/叙事理论 |
| agent-builder | `dar-agent-builder.yaml` | AI 模型库/框架文档/benchmark |

## 加载方式

DAR 作为 `capabilities` 能力包加载。Profile 在 manifest 中声明：

```yaml
enables_capabilities:
  - dar
```

加载后，DAR 配置会自动嵌入该 Profile 的深度搜索流程（`deep-search.md`）和真实性协议（`truth-protocol.md`）。

## 自适应前缀 (v4)

每个 DAR 配置包含两个前缀变体，基于模型规模自动选择：

| 变体 | 格式 | 适用 | 前缀长度 |
|------|------|------|----------|
| `standard` | 压缩式 + 可执行指引 + 3 硬约束 | 大模型 (≥70B / 商业 API) | 150-220 chars |
| `extended` | 完整路由 + 打分公式 + 术语表 | 小模型 (<70B) | 200-400 chars |

选择依据：v1/v2/v3 三轮 A/B 测试（270+ 次 API 调用）发现大模型从短前缀推断意图（+0.8），小模型需要详尽指导（+6.1）。详见 `core/dar-spec.md` §11。

## 动态调整

DAR 支持运行时权重热调整——安全查询提升可信度权重，创意写作提升共识权重，紧急新闻提升时效权重。详见 `core/dar-spec.md` §8。

## 用户覆盖

用户可覆盖所有 DAR 规则（指定来源、调整权重、禁用某源），用户决策权最高。
