---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 98adaa6f98486df4666888a6691e7607_bd4a8916883611f18766525400f8a581
    ReservedCode1: JDV0aEODEo5oZkLFzsMAifFWSTGX3TYjRMnO9pxNCfB1pUje0HkduXjuZT4cPXQt64WtZorB0VobMjXvbLDCvFH54lH38NT7e/FM6+nQCYlXrnm2zCVnmtpPgmV5pm4w050n/jJbeIyN6z1M7wsn6TzR+vZVrnCs2lg38BusxRMyv/4tqiqpiZV5W9o=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 98adaa6f98486df4666888a6691e7607_bd4a8916883611f18766525400f8a581
    ReservedCode2: JDV0aEODEo5oZkLFzsMAifFWSTGX3TYjRMnO9pxNCfB1pUje0HkduXjuZT4cPXQt64WtZorB0VobMjXvbLDCvFH54lH38NT7e/FM6+nQCYlXrnm2zCVnmtpPgmV5pm4w050n/jJbeIyN6z1M7wsn6TzR+vZVrnCs2lg38BusxRMyv/4tqiqpiZV5W9o=
---

# Workflow Five Roles — 编码五子角色工作流

> **触发条件**：接收任何开发需求（写代码 / 重构 / 修 Bug / 新增功能）。
> **加载时机**：Agent 在开始编码工作前必须加载本 Skill，按五子角色逐阶段执行。
> **优先级**：P1（与 core/governance.md §2 真实性、§3 澄清优先、§4 变更范围联动）。

---

## 角色总览

```text
Architect → Engineer → Critic → Verifier → Final
  (设计)    (实现)    (审查)    (验证)    (交付)
```

每个角色有独立的输入/输出契约和退出条件。同一轮对话中按顺序流转，前一角色输出为后一角色输入。

---

## Role 1: Architect（架构师）

### 职责
解析需求 → 设计方案 → 输出文件清单

### 输入
- 用户需求描述（自然语言或 Issue 描述）
- 项目当前技术栈和目录结构

### 执行步骤

1. **需求解析**：将用户需求拆解为功能点列表（Feature Breakdown）
2. **技术选型**：
   - 检查是否可用标准库或已有依赖（引用 `profiles/coding/docs/skills/registry.md`）
   - 如需新依赖，触发 `skills/skill-acquisition.md` 选库流程
3. **文件清单**：列出需要创建、修改、删除的所有文件，标注操作类型：

| 文件路径 | 操作 | 理由 |
|----------|------|------|
| `src/models/user.py` | 新建 | 新增 User ORM 模型 |
| `src/routes/auth.py` | 修改 | 添加登录端点 |
| `tests/test_auth.py` | 新建 | 登录端点测试 |

4. **边界决策**：明确哪些**不**归本次变更范围（防止 scope creep）

### 退出条件
- 文件清单完整且每项有理由
- 技术选型有明确的引用来源
- 无模糊项（如"可能需要"、"到时候再看"）

### 引用
- `core/governance.md §4` 变更范围：只改指定文件
- `core/governance.md §2` 真实性：选型必须有依据
- `core/governance.md §3` 澄清优先：关键参数缺失时先确认

---

## Role 2: Engineer（工程师）

### 职责
严格按 Architect 的文件清单和方案实现代码

### 输入
- Architect 输出的文件清单 + 方案
- 项目现有代码

### 执行步骤

1. **按文件清单顺序编码**：
   - 先建数据模型（model / schema）
   - 再写业务逻辑（service / router）
   - 最后写测试骨架（tests）
2. **遵守项目约定**：
   - 代码风格（ruff / eslint / prettier）
   - 类型标注（mypy / TypeScript）
   - 注释与文档字符串
3. **每完成一个文件，在清单中标记 `[done]`**
4. **不偏离方案**：如实现中发现设计方案有问题，暂停并回到 Architect 修正

### 退出条件
- 文件清单中所有文件已创建/修改
- 无语法错误（lint 通过）
- 无 P0 安全违规（硬编码密钥等）

### 引用
- `core/governance.md §1` 安全与保密：不硬编码密钥
- `core/governance.md §4` 变更范围：不私自改动未列入清单的文件

---

## Role 3: Critic（审查者）

### 职责
逐行审查 Engineer 的产出，至少找出 1 个问题

### 输入
- Engineer 产出的代码（全部文件）

### 执行步骤

1. **逐文件审查**，按以下维度打分：

| 维度 | 检查内容 |
|------|----------|
| 安全 | 有无硬编码密钥、SQL 注入、XSS、未校验输入 |
| 正确性 | 逻辑是否正确、边界条件是否处理 |
| 性能 | 有无 N+1 查询、不必要的循环、未释放资源 |
| 可读性 | 命名是否清晰、函数是否过长（>30 行警告） |
| 契约 | 是否遵守了 Architect 的方案 |

2. **统计问题**：至少输出 1 个有效问题（如无可优化，输出"代码虽无硬伤，但以下风格可改进"）
3. **分类输出**：

```
🔴 Critical（阻塞交付）:
- <问题描述> @ <文件:行号>

🟡 Warning（建议修改）:
- <问题描述> @ <文件:行号>

🟢 Nit（锦上添花）:
- <问题描述> @ <文件:行号>
```

### 退出条件
- 至少产出 1 个审查发现
- 所有 Critical 问题必须回传给 Engineer 修复
- Warning 和 Nit 由下个角色 Verifier 决定是否修复

### 引用
- `core/governance.md §1` 安全与保密
- `core/governance.md §2` 真实性：审查必须基于真实代码，不能猜测

---

## Role 4: Verifier（验证者）

### 职责
验证修复后的代码是否满足需求

### 输入
- Critic 的问题清单 + Engineer 的修复
- Architect 的原始需求

### 执行步骤

1. **逐条验证 Critic 问题**：
   - 是否已修复 → 标记 [resolved]
   - 是否未修复 → 标记 [unresolved]，回传给 Engineer
2. **功能验证**：
   - 运行测试（`pytest` / `jest`）
   - 手动验证关键路径（如API端点能否正常返回）
3. **需求闭环**：逐条对照 Architect 的功能点列表，确认每个功能点已实现
4. **输出验证报告**：

```
✅ 已修复: 3/3 Critical | 2/3 Warning | 1/2 Nit
❌ 未修复: 1 Warning（原因: <说明>）
🧪 测试: 12 passed, 0 failed
📋 功能: 5/5 已实现
```

### 退出条件
- 所有 Critical 已修复
- 测试全部通过
- 功能点 100% 覆盖

### 引用
- `core/governance.md §6` 失败熔断：修复同一 Bug 失败 2 次则停止
- `core/governance.md §2` 真实性：验证基于真实执行结果

---

## Role 5: Final（交付者）

### 职责
最终交付或回退

### 输入
- Verifier 的验证报告

### 执行步骤

1. **交付决策**：
   - 所有 Critical resolved + 测试通过 → **交付**
   - 存在 unresolved Critical 且已尝试 2 次 → **回退**（core/governance.md §6）
2. **交付动作**：
   - 调用 `skills/git-sop.md` 执行 Git 提交
   - 输出交付摘要

3. **交付摘要模板**：

```
## 交付摘要

**分支**: feature/add-user-auth
**文件变更**: 3 new, 1 modified, 0 deleted
**审查**: Passed (0 Critical, 2 Nit deferred)
**测试**: 12/12 passed

### 变更文件
- `src/models/user.py` [new]
- `src/routes/auth.py` [modified]
- `src/schemas/auth.py` [new]
- `tests/test_auth.py` [new]
```

4. **回退动作**：
   - 输出故障报告（错误信息、尝试方案、疑似根因）
   - 等待人工介入

### 退出条件
- 已提交或已回退
- 最终状态明确（delivered / reverted）

### 引用
- `skills/git-sop.md` 提交规范
- `core/governance.md §6` 失败熔断
- `core/governance.md §7` 工程卫生

---

## 状态机

```text
Architect ──→ Engineer ──→ Critic ──→ Verifier ──┬──→ Final (交付)
                              ↑                   │
                              │   发现问题         ├──→ Final (回退)
                              └───────────────────┘
                              (回传修复)
```

各角色间可跳转条件：
- Engineer → Architect：实现中发现方案缺陷
- Verifier → Engineer：验证未通过
- Critic → Engineer：存在 Critical 问题

不允许跳转：
- Final 之后不再回到任何角色（一轮交付完成）
- 跳过 Critic 进入 Verifier（禁止）

---

## Budget 估算

| 角色 | RT Budget | 预计 Token | 说明 |
|------|-----------|-----------|------|
| Architect | STANDARD | ~500-800 | 需求解析 + 方案设计 |
| Engineer | STANDARD | ~1500-3000 | 实际编码 |
| Critic | DEEP | ~600-1000 | 需要深入理解代码 |
| Verifier | STANDARD | ~400-600 | 执行测试 + 验证 |
| Final | QUICK | ~200-400 | 交付摘要 |
*（内容由AI生成，仅供参考）*
