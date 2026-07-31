---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 98adaa6f98486df4666888a6691e7607_be5b26de883611f18766525400f8a581
    ReservedCode1: U/Yp1pN6c5uFSUIvIlvHUMNE+vPEZ8d5ORAHIe+vPaN+MYJCqHmIdR+4OWg37Jv1ruGg6nLg6j6FkGjB5bo3hZHRETbLqM5TohtSxdeqVTsOMD9Qq1BGI45/7mfTK/gCcksQ6Zt7a2/akRvDFOlao+H1yjG1Rh7DxC9lE0kl/QhugmRrk6gSfU61BZA=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 98adaa6f98486df4666888a6691e7607_be5b26de883611f18766525400f8a581
    ReservedCode2: U/Yp1pN6c5uFSUIvIlvHUMNE+vPEZ8d5ORAHIe+vPaN+MYJCqHmIdR+4OWg37Jv1ruGg6nLg6j6FkGjB5bo3hZHRETbLqM5TohtSxdeqVTsOMD9Qq1BGI45/7mfTK/gCcksQ6Zt7a2/akRvDFOlao+H1yjG1Rh7DxC9lE0kl/QhugmRrk6gSfU61BZA=
---

# Skill Acquisition Protocol — 五层依赖获取协议

> **触发条件**：任何需要引入新的第三方依赖（Python 包 / npm 包 / 外部仓库 / CLI 工具）的决策。
> **加载时机**：Architect 角色做技术选型时、Engineer 实现中需要新工具时。
> **优先级**：P1 — 直接影响供应链安全。

---

## 协议架构：五层漏斗

```text
L1: 标准库 (stdlib)
  ↓ 无匹配
L2: 包管理器 (pip / npm)
  ↓ 无匹配
L3: 本地注册表 (profiles/coding/docs/skills/registry.md)
  ↓ 无匹配
L4: 厂商官方仓库 (24 个 Trusted Vendor Orgs)
  ↓ 无匹配
L5: 受限自主搜索 (GitHub Star > 1000，展示 URL 等确认)
```

**原则**：每一层穷举后才下降至下一层。不可跳层。

---

## L1: 标准库优先

### 查询方式
检查所用语言的**标准库**是否已提供能力：

| 语言 | 标准库覆盖范围 |
|------|----------------|
| Python | `os`, `pathlib`, `re`, `json`, `csv`, `sqlite3`, `subprocess`, `urllib`, `http`, `asyncio`, `argparse`, `logging`, `tempfile`, `zipfile`, `hashlib`, `collections`, `itertools`, `functools`, `dataclasses`, `typing`, `decimal`, `enum`, `io` |
| JavaScript/Node | `fs`, `path`, `http`, `https`, `crypto`, `stream`, `events`, `util`, `url`, `querystring`, `child_process` |
| Go | `net/http`, `encoding/json`, `database/sql`, `os`, `io`, `context`, `sync` |

### 决策规则
- 标准库能满足 → **禁止引入第三方依赖**
- 标准库不满足但可通过少量封装（<50 行）满足 → 仍优先标准库
- 论据（Rationale）：减少依赖 = 减少攻击面 + 减少版本冲突

---

## L2: 包管理器

### 查询方式
在标准注册源搜索：

```bash
# Python
pip search <keyword>  # 或 https://pypi.org/search/

# Node.js
npm search <keyword>  # 或 https://www.npmjs.com/search

# Go
go search <keyword>   # 或 https://pkg.go.dev/
```

### 决策规则

| 指标 | 门槛 | 说明 |
|------|------|------|
| 下载量 | Python ≥ 10万/月, npm ≥ 5万/周 | 有用户基数的信号 |
| 维护状态 | 近 6 个月内有过发布 | 活跃维护 |
| 许可证 | MIT / Apache-2.0 / BSD 优先 | 避免 GPL 传染 |
| 依赖数 | 自身的依赖越少越好 | 减少传递风险 |

### 示例
```
需求：解析 YAML 文件
L1 → Python stdlib 无 YAML 解析 → 确认不可用标准库
L2 → pip search PyYAML → 38M 月下载 → ✅ 选中
```

---

## L3: 本地注册表

### 查询方式
读取 `profiles/coding/docs/skills/registry.md`，在对应分类中查找。

分类索引：
| 分类 | 注册表章节 |
|------|-----------|
| HTTP / API | §1 网页与 API |
| 文档处理 | §2 文档处理 |
| 数据处理 | §3 数据处理 |
| 系统操作 | §4 Windows 系统操作 |
| Web 开发 | §5 Web 开发 |
| 测试 | §6 测试 |
| AI/LLM | §7 AI / 智能体开发 |
| CLI 工具 | §8 CLI 工具与终端 |
| 数据库 | §9 数据库 |
| 安全加密 | §10 安全与加密 |
| DevOps | §11 DevOps / 运维 |

### 决策规则
- 注册表内有匹配工具 → **直接使用，不降级到 L4**
- 注册表内工具不满足需求 → 标注"注册表已查询：[分类]，无匹配"后降至 L4

---

## L4: 厂商官方仓库

### 查询方式
在以下 24 个 Trusted Vendor Orgs 的 GitHub 中搜索：

| 厂商 | GitHub Org | 代表领域 |
|------|-----------|----------|
| 阿里巴巴 | https://github.com/alibaba | 微服务、中间件、LLM |
| 腾讯 | https://github.com/Tencent | 移动端、音视频、LLM |
| 字节跳动 | https://github.com/bytedance | 前端框架、高性能计算 |
| 百度 | https://github.com/baidu | PaddlePaddle、前端低代码 |
| 谷歌 | https://github.com/google | JAX、MediaPipe、综合工具 |
| 微软 | https://github.com/microsoft | Playwright、Agent 框架 |
| Meta | https://github.com/facebookresearch | LLM、React |
| OpenAI | https://github.com/openai | LLM SDK |
| Anthropic | https://github.com/anthropics | Claude SDK |
| Hugging Face | https://github.com/huggingface | Transformers、Diffusers |
| DeepSeek | https://github.com/deepseek-ai | MoE 模型 |
| Mistral AI | https://github.com/mistralai | 开源 LLM |
| AWS | https://github.com/aws | 云基础设施 SDK |
| NVIDIA | https://github.com/NVIDIA | CUDA、TensorRT |
| 苹果 | https://github.com/apple | Swift、FoundationDB |
| Netflix | https://github.com/Netflix | 微服务编排 |
| Airbnb | https://github.com/airbnb | 前端工具、动画 |
| Uber | https://github.com/uber | Go 工具链 |
| Stripe | https://github.com/stripe | 支付 SDK |
| Cloudflare | https://github.com/cloudflare | Workers、边缘计算 |
| Databricks | https://github.com/databricks | 数据平台 |
| Redis | https://github.com/redis | 缓存 |
| MongoDB | https://github.com/mongodb | 数据库驱动 |
| Elastic | https://github.com/elastic | 搜索 |

### 决策规则
- 厂商官方仓库内的工具免 Star 门槛审核
- 命中 → 直接采用
- 未命中 → 标注"已搜索 N 个厂商仓库（列出查询过的），无匹配"，降至 L5

---

## L5: 受限自主搜索

### 查询方式
在 GitHub 上搜索关键词，约束条件：

| 条件 | 要求 |
|------|------|
| Star 门槛 | Star > 1000 |
| 活跃度 | 近 3 个月内有提交 |
| 展示内容 | URL + Star 数 + 简介 + 最近更新时间 |
| 用户确认 | 展示搜索结果后**等待用户明确确认**才能安装 |

### 安全检查（L5 专属）
- 禁止未经审查直接执行安装脚本（`.ps1`, `.py`, `.sh`）
- 下载后先放入临时目录审查：
  ```bash
  # Python
  pip download <package> -d %TEMP%/audit/

  # npm
  npm pack <package> --pack-destination %TEMP%/audit/
  ```
- 确认无恶意代码后移入正式目录

---

## 完整决策树

```text
需求：需要 <能力描述>
  │
  ├─ L1: 标准库有吗？ ──── YES → 用标准库 ✅
  │   └─ NO
  │       ├─ L2: pip/npm 有吗？（满足门槛）── YES → 安装 ✅
  │       │   └─ NO
  │       │       ├─ L3: registry.md 有吗？── YES → 用注册表工具 ✅
  │       │       │   └─ NO
  │       │       │       ├─ L4: 厂商仓库有吗？── YES → 用厂商工具 ✅
  │       │       │       │   └─ NO
  │       │       │       │       └─ L5: 受限搜索 → 展示等确认 ⏳
```

---

## 决策记录模板

每次 L2-L5 选型必须输出决策记录：

```markdown
### 依赖决策记录

- **需求**: 解析 YAML 配置文件
- **决策路径**: L1→L2
- **选定工具**: PyYAML v6.0+
- **评估依据**: PyPI 月下载 38M，MIT 许可证，活跃维护
- **被拒绝的替代方案**: ruamel.yaml（过重，有 C 扩展依赖）
- **日期**: 2026-07-25
```

---

## 禁止行为

| 禁止 | 原因 |
|------|------|
| 跳过 L1 直接用 pip | 标准库能满足的引入依赖是无谓的供应链膨胀 |
| 跳过 L3 直接 GitHub 搜索 | 注册表是经审核的白名单，安全基线最高 |
| L5 不展示直接安装 | 供应链安全风险，用户必须有最终决定权 |
| 安装未发布的 fork / 个人分支 | 无质量保障、可能含恶意代码 |
| 安装 Star < 100 的仓库 | 质量不可控，除非 L4 厂商仓库免审 |

---

## 交叉引用

| 引用 | 内容 |
|------|------|
| `profiles/coding/docs/skills/registry.md` | L3 本地注册表（工具白名单） |
| `core/governance.md §1` | 安全与保密：不安装未审查的脚本 |
| `core/governance.md §2` | 真实性：选型依据必须可验证 |
| `core/governance.md §3` | 澄清优先：L5 必须用户确认 |
*（内容由AI生成，仅供参考）*
