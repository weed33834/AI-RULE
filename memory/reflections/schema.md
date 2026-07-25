# Reflexion Memory Schema（反思记忆格式）

> 反思记忆是情景记忆的子类型，存储 Agent 在自主执行过程中的自我纠偏记录。
> 由 `scripts/inject_memory.py` 在每次会话启动时检索并注入上下文。
> 文件格式：JSONL（每行一条记录），存放在 `memory/reflections/` 目录。

## 1. 记录格式

```json
{
  "id": "ref_20260725_001",
  "session_id": "conv_19f945ed6af_4265a002c218",
  "timestamp": "2026-07-25T14:30:00+08:00",
  "agent_mode": "autonomous",
  "profile": "coding",
  "trigger": {
    "type": "error_correction | self_critique | user_feedback | pattern_discovery",
    "description": "修复同一个 Bug 连续失败 2 次后，发现根因是正则表达式未转义特殊字符"
  },
  "before": {
    "approach": "使用 r\"@([\\w/.-]+\\.md)\" 匹配 @@ 双 at 语法",
    "failure": "仅匹配单 @，漏掉 @@ 前缀的内联引用，导致 build_ruleset 跳过 14 个文件"
  },
  "after": {
    "approach": "改用 r\"@@?([\\w/.-]+\\.md)\" 同时匹配 @ 和 @@",
    "result": "全部内联引用正确加载，验证通过"
  },
  "lesson": {
    "pattern": "正则表达式边界条件覆盖",
    "rule": "编写正则时，先列出所有合法输入格式，再构造模式，避免遗漏变体",
    "severity": "P1",
    "applies_to": ["regex", "parsing", "file_loading"]
  },
  "metadata": {
    "iteration_count": 2,
    "resolved": true,
    "tags": ["regex", "sync_rules", "double-at-syntax"]
  }
}
```

## 2. 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识，格式 `ref_YYYYMMDD_NNN` |
| `session_id` | string | 是 | 产生该反思的会话 ID |
| `timestamp` | string | 是 | ISO 8601 格式，带时区 |
| `agent_mode` | string | 是 | 产生反思时的 Agent 模式 |
| `profile` | string | 是 | 产生反思时的 Profile |
| `trigger.type` | enum | 是 | 触发类型：`error_correction` / `self_critique` / `user_feedback` / `pattern_discovery` |
| `trigger.description` | string | 是 | 触发情况的自然语言描述 |
| `before.approach` | string | 是 | 修正前的方法 |
| `before.failure` | string | 是 | 失败表现 |
| `after.approach` | string | 是 | 修正后的方法 |
| `after.result` | string | 是 | 修正后的结果 |
| `lesson.pattern` | string | 是 | 失败模式的简短名称 |
| `lesson.rule` | string | 是 | 从中提炼的可复用规则/教训 |
| `lesson.severity` | enum | 是 | `P0` / `P1` / `P2` |
| `lesson.applies_to` | string[] | 是 | 适用领域标签 |
| `metadata.iteration_count` | int | 是 | 修正前尝试次数 |
| `metadata.resolved` | bool | 是 | 是否已解决 |
| `metadata.tags` | string[] | 否 | 检索标签 |

## 3. 检索注入规则

- 注入时机：每次新会话启动，由 `scripts/inject_memory.py` 检索相关反思记录。
- 检索条件：当前 Profile + 当前 Agent 模式 + 标签匹配。
- 注入格式：以系统提示词附录形式注入，每条反思不超过 200 token。
- 注入数量上限：最多 5 条，按 `timestamp` 倒序取最新。
- 注入位置：在 Profile 规则之后、用户输入之前。

## 4. 写入时机

- 当 Agent 在 Autonomous / Project 模式下遇到 P0/P1 级别错误并成功修正后，自动生成反思记录。
- 用户明确要求"记住这个教训"时，生成反思记录。
- 写入路径：`memory/reflections/<profile>_<yyyy-mm>.jsonl`。
