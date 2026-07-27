# Rule Hub Hook 适配器

把 `core/constraints.yaml` 里的 P0 红线翻译成各 AI 编程工具的 PreToolUse hook，
让规则从"软引导"升级为"硬拦截"——AI 想违规也做不到。

## 支持的平台

| 平台 | 适配器 | 拦截能力 | 配置文件 |
|---|---|---|---|
| **Claude Code** | `claude-code/` | ✅ 完整（PreToolUse / PostToolUse / Stop） | `~/.claude/settings.json` 或 `.claude/settings.json` |
| **Cursor** | `cursor/` | ✅ 完整（preToolUse） | `.cursor/hooks.json` |
| **Gemini CLI** | `gemini/` | ✅ 完整（PreToolUse） | `.gemini/hooks.json` 或 `~/.gemini/settings.json` |
| **Cline** | `cline/` | ✅ 完整（preToolUse） | `.cline/hooks.json` 或 `~/.cline/settings.json` |
| **Codex CLI** | `codex/` | ✅ 完整（PreToolUse） | `.codex/hooks.json` 或 `~/.codex/config.json` |
| **Trae IDE** | `trae/` | ⚠️ 部分（仅平台内置沙箱，无自定义 hook） | `.trae/sandbox-policy.json` |

## 架构

```
adapters/hooks/
├── shared/
│   └── check.py              ← 通用拦截逻辑（读 constraints.yaml，决策 deny/approval/warn）
├── claude-code/
│   ├── pre_tool_use.py       ← Claude Code 适配器（stdin JSON → stdout JSON）
│   └── settings.json.template
├── cursor/
│   ├── pre_tool_use.py       ← Cursor 适配器
│   └── hooks.json.template
├── gemini/
│   ├── pre_tool_use.py       ← Gemini CLI 适配器
│   └── hooks.json.template
├── cline/
│   ├── pre_tool_use.py       ← Cline 适配器
│   └── hooks.json.template
├── codex/
│   ├── pre_tool_use.py       ← Codex CLI 适配器
│   └── hooks.json.template
└── trae/
    └── sandbox-policy.json   ← Trae 沙箱策略（平台层固定，非脚本）
```

## 部署步骤

### 1. 安装 Rule Hub

```bash
pip install ai-rule
# 或
git clone https://gitcode.com/badhope/AI-RULE.git
export AI_RULE_REPO=/path/to/AI-RULE
```

### 2. 复制适配器到你的项目

```bash
# 假设你在 ~/my-project/ 里开发
cp -r $AI_RULE_REPO/adapters/hooks/ ~/my-project/.ai-rule-hooks/
```

### 3. 启用对应平台的 hook

**Claude Code**：复制 `claude-code/settings.json.template` 内容到 `~/.claude/settings.json`（全局）或 `.claude/settings.json`（项目级）

**Cursor**：复制 `cursor/hooks.json.template` 到 `.cursor/hooks.json`

**其他平台**同理，看各适配器目录下的 `.template` 文件。

### 4. 验证 hook 工作

```bash
# 测试 MCP 安装拦截
echo '{"tool_name": "Bash", "tool_input": {"command": "npm install @modelcontextprotocol/server-filesystem"}}' | python .ai-rule-hooks/claude-code/pre_tool_use.py

# 应输出：{"deny": true, "reason": "[P0 MCP_NO_AUTO_INSTALL] ..."}
```

## 拦截的 P0 红线（与 governance.md 一一对应）

| Constraint ID | governance § | 拦截行为 | 示例 |
|---|---|---|---|
| SECRETS_NO_HARDCODE | §1 | deny | `sk-xxxx...` / `ghp_xxxx...` 写入文件 |
| ENV_FILE_NO_COMMIT | §1 | deny | `git add .env` |
| DESTRUCTIVE_OP_REQUIRES_CONFIRM | §3 | require_approval | `rm -rf /` / `git push --force` |
| GIT_NO_AUTO_PUSH | §3, AGENTS §7 | require_approval | `git push origin main` |
| MCP_NO_AUTO_INSTALL | §5, AGENTS §5 | deny | `npm install @modelcontextprotocol/*` |
| NO_EDIT_GENERATED_FILES | §8 | deny | 直接编辑 AGENTS.md / CLAUDE.md 等 |
| SCOPE_LIMITED_CHANGES | §4 | require_approval | 修改用户未指定的文件 |
| NO_LARGE_FILE_REWRITE | §4 | require_approval | 全量重写 >100 行文件 |
| FAILURE_CIRCUIT_BREAKER | §6 | runtime（hook 暂未实现，需 stateful） | 连续失败 2 次熔断 |
| PROMPT_INJECTION_GUARD | §1 | runtime（hook 暂未实现） | 输入含"ignore previous instructions" |

## 调试

每个适配器脚本可直接运行自检：

```bash
python adapters/hooks/shared/check.py
```

会跑 7 个典型测试场景，输出每个的拦截结果。

## 边界说明

- **stateful 约束（FAILURE_CIRCUIT_BREAKER）**：当前版本未实现，需要 hook 维护跨工具调用状态。下一版本计划用本地状态文件（`.ai-rule/session-state.json`）支持。
- **runtime 约束（PROMPT_INJECTION_GUARD）**：当前版本未实现，需要平台支持 UserPromptSubmit hook。Claude Code 支持，下一版本接入。
- **Trae 沙箱**：只能配置平台固定策略，不能跑自定义脚本。所以 Trae 适配器是 `.json` 不是 `.py`。
- **白名单**：可在 `.ai-rule/session-allowed.txt` 里写文件路径（每行一个），这些文件不会被 SCOPE_LIMITED_CHANGES 拦截。
