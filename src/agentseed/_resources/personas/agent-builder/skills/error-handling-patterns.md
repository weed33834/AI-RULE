# 错误处理模式 (Error Handling Patterns)

> 本文档定义智能体错误处理的系统化模式：4 层防御、8 种恢复策略、降级方案设计。
> 智能体在真实环境中会遇到各种异常——工具调用失败、API 超时、上下文溢出、用户输入异常。
> 与 `safety-guardrails.md` 互补——安全护栏防止危险行为，错误处理保障异常时的优雅降级。

## §1 设计原则

- **快速失败**（Fail Fast）：能立即发现的错误立即报出，不拖延到下游。
- **高声失败**（Fail Loud）：不确定是否成功时，明确说出来，不假装成功。
- **优雅降级**（Graceful Degradation）：无法完成完整任务时，提供部分可用的结果。
- **可恢复**（Recoverable）：错误发生后，系统应能恢复到可用状态，而非崩溃。
- **可观测**（Observable）：所有错误都记录足够的上下文，便于诊断。

## §2 四层防御体系

```
┌─────────────────────────────────────────┐
│ L1: 输入校验层 — 拦截非法输入             │
├─────────────────────────────────────────┤
│ L2: 执行防护层 — 工具调用/API 请求的异常处理 │
├─────────────────────────────────────────┤
│ L3: 状态恢复层 — 异常后的状态回滚与恢复     │
├─────────────────────────────────────────┤
│ L4: 用户体验层 — 向用户优雅地传达错误       │
└─────────────────────────────────────────┘
```

### 2.1 L1: 输入校验层

在智能体开始处理前，拦截非法输入：

| 校验类型 | 检查内容 | 处理方式 |
|----------|----------|----------|
| 格式校验 | JSON 结构、字段类型、必填字段 | 返回明确的格式错误提示 |
| 语义校验 | 逻辑一致性、值域合理性 | 返回语义错误说明 |
| 安全校验 | 注入检测、越权检测 | 拒绝并记录安全日志 |
| 资源校验 | 输入大小、 token 数限制 | 返回资源限制提示 |

```python
# L1 示例：输入校验
def validate_input(user_input: dict) -> ValidationResult:
    if not user_input.get("query"):
        return ValidationResult(ok=False, error="query 字段不能为空")
    if len(user_input["query"]) > 10000:
        return ValidationResult(ok=False, error="query 超过最大长度 10000")
    if contains_injection(user_input["query"]):
        return ValidationResult(ok=False, error="输入包含不安全内容")
    return ValidationResult(ok=True)
```

### 2.2 L2: 执行防护层

工具调用和 API 请求的异常处理：

| 异常类型 | 处理策略 | 重试？ |
|----------|----------|--------|
| 网络超时 | 指数退避重试 3 次 | ✅ |
| API 限流(429) | 等待 Retry-After 后重试 | ✅ |
| 认证失败(401/403) | 不重试，报告认证问题 | ❌ |
| 资源不存在(404) | 不重试，报告资源缺失 | ❌ |
| 服务端错误(5xx) | 重试 2 次后降级 | ✅(有限) |
| 响应格式异常 | 不重试，记录原始响应 | ❌ |
| 工具执行异常 | 根据异常类型决定 | 视情况 |

```python
# L2 示例：工具调用防护
async def safe_tool_call(tool, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await tool(**params)
            return ToolResult(ok=True, data=result)
        except TimeoutError:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避
                continue
            return ToolResult(ok=False, error="工具调用超时，已重试 3 次")
        except RateLimitError:
            wait = get_retry_after(error) or 60
            await asyncio.sleep(wait)
            continue
        except AuthError:
            return ToolResult(ok=False, error="认证失败，请检查 API Key")
        except Exception as e:
            return ToolResult(ok=False, error=f"未知错误: {e}")
```

### 2.3 L3: 状态恢复层

异常发生后的状态管理：

| 场景 | 恢复策略 |
|------|----------|
| 部分工具调用成功，部分失败 | 保留成功结果，报告失败部分，让用户决定是否继续 |
| 多步骤任务中途失败 | 保存已完成步骤的 checkpoint，支持从断点恢复 |
| 上下文溢出 | 触发摘要压缩，保留关键信息，丢弃低优先级内容 |
| 记忆冲突 | 以最新信息为准，标记旧信息为"已过时" |
| 状态不一致 | 触发一致性检查，向用户报告矛盾点 |

### 2.4 L4: 用户体验层

向用户传达错误时的规范：

| 原则 | 正确做法 | 错误做法 |
|------|----------|----------|
| 诚实 | "抱歉，我无法完成这个任务，原因是..." | 假装成功或编造结果 |
| 具体 | "API 返回 404，用户 ID 12345 不存在" | "出错了" |
| 可操作 | "请检查用户 ID 是否正确，或联系管理员" | 只报错不给建议 |
| 简洁 | 技术细节折叠/次要展示 | 把完整 stack trace 直接给用户 |
| 不甩锅 | "我没能找到相关信息" | "系统有问题" / "这不是我的错" |

## §3 八种恢复策略

| # | 策略 | 适用场景 | 示例 |
|---|------|----------|------|
| 1 | 重试 | 瞬时故障（网络抖动） | 指数退避重试 API 调用 |
| 2 | 降级 | 核心功能可用但非核心功能不可用 | 无法生成图片时只返回文字描述 |
| 3 | 备选方案 | 主方案失败但有替代路径 | 主 API 不可用时切换到备选 API |
| 4 | 部分返回 | 多项任务中部分成功 | 10 项查询中 8 项成功，返回 8 项并标注 |
| 5 | 缓存 | 数据源不可用但有历史数据 | API 不可用时返回上次缓存的结果（标注时效） |
| 6 | 用户介入 | 自动恢复不可能 | 向用户展示问题并提供选项 |
| 7 | 安全失败 | 无法恢复但不能崩溃 | 返回默认安全值 + 错误日志 |
| 8 | 熔断 | 连续失败表明系统问题 | 连续 5 次失败后停止尝试，等待恢复 |

## §4 降级方案设计

### 4.1 降级层次模型

```
完整功能 (所有工具可用)
  ↓ 降级
核心功能 (关键工具可用，辅助工具不可用)
  ↓ 降级
基本功能 (只有基础能力可用)
  ↓ 降级
只读模式 (只能查看不能操作)
  ↓ 降级
安全停机 (返回错误信息 + 联系方式)
```

### 4.2 降级触发条件

| 触发条件 | 降级到 | 用户感知 |
|----------|--------|----------|
| 非关键工具不可用 | 核心功能 | "部分功能暂时不可用" |
| 关键工具不可用 | 基本功能 | "核心功能受限" |
| 上下文窗口接近上限 | 压缩模式 | 响应变短，历史被摘要 |
| API 全部不可用 | 只读/安全停机 | "服务暂时不可用" |
| 连续错误超过阈值 | 熔断 | "系统正在恢复中" |

## §5 错误日志规范

```json
{
  "timestamp": "2025-01-15T10:30:45Z",
  "level": "ERROR",
  "error_type": "tool_call_timeout",
  "tool_name": "search_web",
  "params": {"query": "***"},
  "attempt": 3,
  "duration_ms": 30000,
  "recovery_action": "degraded_to_cache",
  "user_message": "搜索服务暂时不可用，显示上次缓存结果",
  "context": {
    "session_id": "sess_abc123",
    "turn": 5,
    "previous_tool": "parse_intent"
  }
}
```

## §6 与其他文档的关系

- **`safety-guardrails.md`**: 安全护栏是错误处理的 P0 层——危险操作必须被拦截，不走错误恢复流程。
- **`evaluation-framework.md`**: 错误恢复能力是评估维度之一。
- **`context-engineering.md`**: 上下文溢出是常见错误，其处理策略参考该文档的压缩机制。
- **`deployment-guide.md`**: 部署时需要配置错误监控和告警。
- **`agent-observability.md`**: 错误日志是可观测性的核心数据源。
