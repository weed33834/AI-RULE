# MCP Integration

AgentSeed 能力包 → MCP (Model Context Protocol) 互操作层。

## 概述

Anthropic MCP 定义了 LLM 应用与外部工具/数据源之间的标准接口（类似于 USB-C）。
AgentSeed 通过为每个能力包添加 `.mcp.json` 描述符，使支持 MCP 的 Agent 客户端
能够程序化发现和调用 AgentSeed 定义的工具约束，而无需人工解析 Prompt 文本。

## 文件结构

```
capabilities/
  dar.mcp.json          # DAR 路由与评分工具
  engineering.mcp.json  # 代码校验与 Git 工作流
  research.mcp.json     # 深度搜索与方法审计
  testing.mcp.json      # 测试生成
  review.mcp.json       # 代码审查
```

## 生成 MCP Server 配置

```bash
# 全量生成
python scripts/generate_mcp_config.py --output mcp.json

# 按 Profile 裁剪
python scripts/generate_mcp_config.py --profile coding --output coding-mcp.json
```

输出为标准 MCP server 格式，可直接被 Claude Desktop、Cline、Cursor 等 MCP client 加载。

## 与 sync_rules.py 的关系

- `sync_rules.py`：装配规则 Prompt 文本（面向纯文本 Agent）
- `generate_mcp_config.py`：聚合工具描述符（面向 MCP Agent）
- 两者共享同一 `capabilities/` 源，保证一致性

## 扩展

添加新能力包时：
1. 创建 `capabilities/<name>.md`（规则文本）
2. 创建 `capabilities/<name>.mcp.json`（工具描述符）
3. 在对应 Profile 的 manifest 中启用
4. 在 `generate_mcp_config.py` 的 `PROFILE_CAPABILITIES` 映射中注册
