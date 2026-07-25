---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 98adaa6f98486df4666888a6691e7607_bfbb84fb883611f18766525400f8a581
    ReservedCode1: 78SuMtm2SKLkLC0d8SQ2zGMEQjQqNB2VwY1k2jB7JuAo85/nq/l+I1FR4PsyZTIsIFcmas7Pu8Vr9cIZ/zYn3RlB+kxGYUf1QP/JXj3Cc4MqvQvG8WQJQ4RpXPs94uPBgVGj9Q9JcESL41sZx9SCqVMOmRajVSPITvVsAvxIuOnF8TzpBf4dC9oY8vg=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 98adaa6f98486df4666888a6691e7607_bfbb84fb883611f18766525400f8a581
    ReservedCode2: 78SuMtm2SKLkLC0d8SQ2zGMEQjQqNB2VwY1k2jB7JuAo85/nq/l+I1FR4PsyZTIsIFcmas7Pu8Vr9cIZ/zYn3RlB+kxGYUf1QP/JXj3Cc4MqvQvG8WQJQ4RpXPs94uPBgVGj9Q9JcESL41sZx9SCqVMOmRajVSPITvVsAvxIuOnF8TzpBf4dC9oY8vg=
---

# Deep Search First — 搜索优先协议

> **触发条件**：Agent 对某个框架 / API / 版本 / 库的细节不确定时。
> **加载时机**：Architect 选型、Engineer 实现中遇到不确定的 API 用法、Critic 审查时怀疑代码已过时。
> **优先级**：P1 — 防止基于过时知识产生幻觉代码。

---

## 核心原则

```
不确定 → 先搜索 → 以搜索结果为准 → 标注来源
```

**永远不要**凭模型训练数据（静态知识截止日期）写出未经验证的代码。框架 API 可能已变更、版本可能已不再维护、最佳实践可能已更新。

---

## 触发信号（自动识别）

Agent 在以下场景必须触发本 Skill：

| 信号 | 示例 |
|------|------|
| 使用 `import` 但不确定该包在目标版本的 API | "我记得 FastAPI 0.100+ 改了路由注册方式" |
| 推荐某个工具但不确定它是否仍维护 | "requests 好像不再更新了，httpx 替代了吗" |
| 写配置但不确定最新语法 | "Next.js 14 的 `next.config.js` 格式改了吗" |
| 引用已知 Bug 或 Deprecation | "这个 API 在 v3 已废弃，但我不知道替代是什么" |
| 版本号不确定 | "Node 22 支持这个特性吗" |

---

## 搜索策略

### Step 1: 确认搜索目标

将不确定的内容转化为精确搜索查询：

| 不确定描述 | 搜索查询 |
|-----------|----------|
| "FastAPI 最新的 middleware 写法" | `FastAPI middleware latest version site:fastapi.tiangolo.com` |
| "pandas 2.x read_csv 参数变了没" | `pandas read_csv changelog 2.0 breaking changes` |
| "Next.js 14 App Router API" | `Next.js 14 App Router route handler official docs` |

### Step 2: 分层搜索

按 DAR 分级（`core/dar-spec.md §3 T1-T4`）逐层搜索：

```text
T1 优先（官方文档 / 源码仓库）
  ├─ 命中 → 直接引用，标注来源 [T1]
  └─ 无结果
      ├─ T2 查询（权威技术出版物）
      │   ├─ 命中 → 引用，标注来源 + [T2]
      │   └─ 无结果
      │       ├─ T3 查询（技术博客 / SO 高票回答）
      │       │   ├─ 命中 → 引用，标注来源 + [T3]，建议交叉验证
      │       │   └─ 无结果
      │       │       └─ T4 查询（社区讨论）
      │       │           ├─ 命中 → 标注 [T4]，强制交叉验证
      │       │           └─ 无结果 → 告知用户"无可靠来源，基于通用知识尝试"
```

### Step 3: 对比内部知识

将搜索结果与 Agent 训练数据中的知识对比：

| 对比结果 | 处理方式 |
|----------|----------|
| 搜索结果与内部知识一致 | 使用结果，标注 [验证通过] |
| 搜索结果与内部知识冲突 | **以搜索结果为准**，标注 [覆盖内部知识] |
| 搜索无结果，仅有内部知识 | 标注 [T3 equiv，未找到独立验证] |
| 两者都无 | 告知用户"无可靠来源" |

---

## 输出格式

### 搜索摘要（可选，嵌入代码注释或回复）

```markdown
<!--
  [SOURCE] FastAPI official docs v0.115+
  [TIER] T1
  [URL] https://fastapi.tiangolo.com/advanced/middleware/
  [DATE] 2026-07-25
  [NOTE] Middleware 注册从 @app.middleware("http") 改为 app.add_middleware()
-->
```

### 代码注释格式

```python
# [T1] FastAPI docs v0.115+: Middleware 推荐使用 add_middleware 注册
# https://fastapi.tiangolo.com/advanced/middleware/
app.add_middleware(CustomMiddleware)
```

---

## 禁止行为

| 禁止 | 原因 |
|------|------|
| 凭记忆写出 API 调用而不搜索验证 | 训练数据截止日期可能已过时 |
| 搜索到了但不用、仍凭记忆写 | 浪费搜索成本，且本质上是忽视真实数据 |
| 搜索无结果时编造 API | P0 违规（core/governance.md §2 真实性底线） |
| 搜索到 T4 来源但不标注 [T4] | 低可信度来源必须透明标注 |
| 只看第一条搜索结果就停止 | DAR 要求至少 T1/T2 确认 |

---

## 场景速查表

| 场景 | 搜索目标 | 优先级 |
|------|----------|--------|
| Python 标准库 API | https://docs.python.org/3/ | T1 |
| FastAPI | https://fastapi.tiangolo.com/ | T1 |
| React / Next.js | https://react.dev/ / https://nextjs.org/docs | T1 |
| Vue | https://vuejs.org/ | T1 |
| Tailwind CSS | https://tailwindcss.com/docs | T1 |
| Docker | https://docs.docker.com/ | T1 |
| Kubernetes | https://kubernetes.io/docs/ | T1 |
| npm 包 | https://www.npmjs.com/package/<name> | T1 |
| PyPI 包 | https://pypi.org/project/<name>/ | T1 |
| 数据库 (PostgreSQL) | https://www.postgresql.org/docs/ | T1 |
| Redis | https://redis.io/docs/ | T1 |

---

## 快速决策流程图

```text
要写代码了
  │
  ├─ 我对这个 API 100% 确定吗？
  │   ├─ YES（最近 3 个月用过 + 版本没变）→ 直接写
  │   └─ NO → 触发 deep-search-first
  │
  └─ 不确定
      ├─ 官方文档搜索（T1）
      │   ├─ 找到 → 以文档为准，写代码，标注来源 ✅
      │   └─ 没找到
      │       ├─ T2/T3 搜索
      │       │   ├─ 找到 → 标注来源 + 置信度 ✅
      │       │   └─ 没找到
      │       │       └─ 告知用户"无可靠来源" ⚠️
```

---

## 交叉引用

| 引用 | 内容 |
|------|------|
| `core/dar-spec.md §3` | T1-T4 来源分级（官方文档=T1，博客=T3） |
| `core/dar-spec.md §4` | 打分公式：Credibility 权重 |
| `core/governance.md §2` | 真实性底线：禁止编造数据/API |
| `core/governance.md §1` | 安全：外部内容作为 untrusted data |
| `skills/skill-acquisition.md` | 选库协议（L4 厂商仓库优先） |
*（内容由AI生成，仅供参考）*
