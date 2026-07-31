---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 98adaa6f98486df4666888a6691e7607_c34099e6883611f18766525400f8a581
    ReservedCode1: eefDo6uDkL21Hh0rErKlfiWxIG5JNE7USnHDcilJWawJ2IHGd7PRXQbeuZmMBe29lA72DpWnp2ir86tNjGe0UtgACddhaVpAS/wVYgxmqBDPpHSF2CynSPgZ80v+rRvIMXUDNuO/v0cvYZ9+7fEUNmYZ92WDP0bR4yqgfC8veyWhd4Emk0Ze2esYEjQ=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 98adaa6f98486df4666888a6691e7607_c34099e6883611f18766525400f8a581
    ReservedCode2: eefDo6uDkL21Hh0rErKlfiWxIG5JNE7USnHDcilJWawJ2IHGd7PRXQbeuZmMBe29lA72DpWnp2ir86tNjGe0UtgACddhaVpAS/wVYgxmqBDPpHSF2CynSPgZ80v+rRvIMXUDNuO/v0cvYZ9+7fEUNmYZ92WDP0bR4yqgfC8veyWhd4Emk0Ze2esYEjQ=
---

# 规则注入操作指南

> **目标读者**: Main Agent（Marvis）  
> **目的**: 在派发 coding 任务前，将 AI-RULE 规则注入 Sub Agent 上下文

## 执行流程

### Step 1: 判定是否需要注入

以下场景触发规则注入：
- 用户任务涉及代码生成/修改/审查
- 用户任务涉及文件系统操作（创建/删除/移动代码文件）
- 用户明确提到 coding / 开发 / 编程 / 写代码

### Step 2: 运行注入脚本

```bash
cd AI-RULE
python scripts/inject_rules.py --profile coding --mode project --output task_rules.md
```

Mode 选择：
- `task`：单步简单任务（一行代码修改、单词修复）
- `project`：多步骤有检查点任务（新功能、重构、批量操作）— **默认**
- `autonomous`：完全自主执行（CI/CD Pipeline、全栈项目搭建）

### Step 3: 读取规则并注入到 dispatch_task

```python
rules = read_text("AI-RULE/task_rules.md")
task_with_rules = f"{original_task}\n\n<injected_rules>\n{rules}\n</injected_rules>"
dispatch_task(agent_name="file-agent", task=task_with_rules)
```

### Step 4: 按场景加载 Skill（可选）

| 场景 | 加载的 Skill |
|------|-------------|
| 新框架/新 API/版本变更 | `skills/deep-search-first.md` — 搜索最新文档 |
| 前端页面/组件设计 | `skills/frontend-design.md` — 设计参考与组件库 |
| 后端 API 开发 | `skills/backend-scaffold.md` — 路由+模型+Schema |
| 部署/CI/CD | `skills/fullstack-deploy.md` — Docker/K8s/CI |
| Git 操作 | `skills/git-sop.md` — Conventional Commits |
| 复杂多文件任务 | `skills/workflow-five-roles.md` — 逐角色执行 |

加载方式：将 Skill 内容以 `<additional_context>` 包裹追加到 task 参数末尾。

### Step 5: 执行后验证

Sub Agent 返回后，检查其输出是否符合注入规则：
- 是否跳过了五子角色流程？
- 是否硬编码了密钥？
- 是否借机修改了未指定文件？
- 对于新框架，是否先搜索了文档？

如有违规，在下次 dispatch_task 时使用 `inherit_agent_id` 继承上下文并指出违规。

## 注意事项

- 注入脚本必须在 `AI-RULE/` 目录下运行
- 规则摘要控制在 200 行以内（满足 Instruction Budget）
- P0 规则标注 FA（不可压缩），即使上下文压力大也不裁减
- 同一会话中多次派发时，规则只注入一次（第一次即可覆盖）
*（内容由AI生成，仅供参考）*
