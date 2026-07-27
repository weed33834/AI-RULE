# Rule Hub Policy — Rego
#
# 这是 core/constraints.yaml 的 OPA/Rego 升级版，支持更复杂的上下文判断。
# 与 constraints.yaml 同源同义（YAML 给简单 hook 用，Rego 给装了 OPA 的用户用）。
#
# 优势：
#   - 支持上下文判断（如"非工作时间禁 git push"）
#   - 支持跨调用状态（如"agent 已失败 2 次就熔断"）
#   - 可单元测试（policy_test.rego）
#   - 可审计（每次决策有完整 reasoning）
#
# 用法（需先装 OPA: https://www.openpolicyagent.org/docs/#1-download-opa）：
#   opa eval -d core/policy.rego -i input.json 'data.ai_rule.allow'
#
# Python API（需装 opa-python 或调 opa binary）：
#   from ai_rule.policy_engine import decide_with_opa
#   result = decide_with_opa(tool_name="Bash", tool_input={"command": "git push"})

package ai_rule

# ─── 默认决策 ───────────────────────────────────────

default allow = true
default deny = false
default require_approval = false
default warn = ""
default reason = ""
default matched_constraint = ""

# ─── 输入 schema ───────────────────────────────────
# input = {
#   "tool_name": "Bash",
#   "tool_input": {"command": "git push", "file_path": "...", "content": "..."},
#   "context": {
#     "timestamp": "2026-07-26T22:00:00Z",
#     "session_failures": 0,
#     "files_modified_this_session": ["app.py", "test_app.py"]
#   }
# }

# ─── P0 红线（deny 即直接拦截）──────────────────────

# 1. 硬编码密钥
deny_secrets {
  some content
  content := input.tool_input.content
  regex.match("sk-[A-Za-z0-9]{20,}", content)
  not is_placeholder(content)
}
deny_secrets {
  some content
  content := input.tool_input.content
  regex.match("ghp_[A-Za-z0-9]{36,}", content)
}
deny_secrets {
  some content
  content := input.tool_input.content
  regex.match("AKIA[0-9A-Z]{16}", content)
}
deny_secrets {
  some content
  content := input.tool_input.content
  regex.match("-----BEGIN [A-Z ]*PRIVATE KEY-----", content)
}

# 白名单：${ENV_VAR} / os.getenv() / <YOUR_API_KEY>
is_placeholder(content) {
  regex.match(".*\\$\\{[A-Z_]+\\}.*", content)
}
is_placeholder(content) {
  regex.match(".*os\\.getenv\\(.*", content)
}
is_placeholder(content) {
  regex.match(".*<YOUR_API_KEY>.*", content)
}

# 2. 提交 .env
deny_env_commit {
  some cmd
  cmd := input.tool_input.command
  regex.match("git\\s+(add|commit|push).*(\\.env|\\.env\\.local)", cmd)
}

# 3. MCP 自安装
deny_mcp_install {
  some cmd
  cmd := input.tool_input.command
  regex.match("(npm\\s+install|npx|pip\\s+install|uvx).*(mcp|modelcontextprotocol)", cmd)
}

# 4. 编辑生成文件
deny_edit_generated {
  some path
  path := input.tool_input.file_path
  is_generated_file(path)
  file_has_marker(path)
}

is_generated_file(path) {
  path == "AGENTS.md"
}
is_generated_file(path) {
  path == "CLAUDE.md"
}
is_generated_file(path) {
  startswith(path, ".cursor/rules/")
}
is_generated_file(path) {
  startswith(path, ".trae/rules/")
}
# （其他生成文件略，对齐 constraints.yaml 的 file_path_patterns）

file_has_marker(path) {
  # 实际实现需读文件头检查"禁止手工编辑"标记
  # Rego 本身不读文件，需要外层 Python 包装传入 marker_exists 标志
  input.tool_input._header_has_marker == true
}

# ─── P0 红线：deny 总规则 ───────────────────────────

deny {
  deny_secrets
  reason := "SECRETS_NO_HARDCODE: 检测到硬编码密钥"
  matched_constraint := "SECRETS_NO_HARDCODE"
}

deny {
  deny_env_commit
  reason := "ENV_FILE_NO_COMMIT: 禁止提交 .env 文件"
  matched_constraint := "ENV_FILE_NO_COMMIT"
}

deny {
  deny_mcp_install
  reason := "MCP_NO_AUTO_INSTALL: AI 禁止自行安装 MCP"
  matched_constraint := "MCP_NO_AUTO_INSTALL"
}

deny {
  deny_edit_generated
  reason := "NO_EDIT_GENERATED_FILES: 该文件由 ai-rule 自动生成，禁止手改"
  matched_constraint := "NO_EDIT_GENERATED_FILES"
}

# ─── P0 require_approval（需用户确认）────────────────

# 破坏性操作
require_approval_destructive {
  some cmd
  cmd := input.tool_input.command
  regex.match("(rm\\s+-rf?\\s+(/|~|\\*|\\$|\\.\\.)|git\\s+push\\s+.*(--force|-f)\\b|git\\s+reset\\s+--hard|DROP\\s+(TABLE|DATABASE|SCHEMA))", cmd)
}

# git push 默认需确认
require_approval_push {
  some cmd
  cmd := input.tool_input.command
  regex.match("git\\s+push\\b", cmd)
  not regex.match("git\\s+push\\s+(--dry-run|-n\\b)", cmd)
}

# 上下文感知：非工作时间禁 git push（OPA 独有能力，YAML 做不到）
require_approval_after_hours {
  some cmd
  cmd := input.tool_input.command
  regex.match("git\\s+push\\b", cmd)
  is_after_hours
}

is_after_hours {
  # 假设 input.context.timestamp 是 ISO8601
  # 22:00-08:00 视为非工作时间
  hour := to_number(substr(input.context.timestamp, 11, 2))
  hour >= 22
}
is_after_hours {
  hour := to_number(substr(input.context.timestamp, 11, 2))
  hour < 8
}

require_approval {
  require_approval_destructive
  reason := "DESTRUCTIVE_OP_REQUIRES_CONFIRM: 破坏性操作需用户确认"
  matched_constraint := "DESTRUCTIVE_OP_REQUIRES_CONFIRM"
}

require_approval {
  require_approval_push
  reason := "GIT_NO_AUTO_PUSH: git push 需用户确认"
  matched_constraint := "GIT_NO_AUTO_PUSH"
}

require_approval {
  require_approval_after_hours
  reason := "AFTER_HOURS_PUSH_BLOCKED: 非工作时间（22:00-08:00）禁止 git push"
  matched_constraint := "AFTER_HOURS_PUSH_BLOCKED"
}

# ─── P0 失败熔断（stateful，OPA 独有）───────────────

deny_circuit_breaker {
  input.context.session_failures >= 2
  reason := sprintf("FAILURE_CIRCUIT_BREAKER: 会话已失败 %d 次，触发熔断", [input.context.session_failures])
  matched_constraint := "FAILURE_CIRCUIT_BREAKER"
}

deny {
  deny_circuit_breaker
}

# ─── 最终决策 ────────────────────────────────────────

# deny 优先级最高
deny_final {
  deny
}

# 否则若 require_approval，返回需确认
require_approval_final {
  not deny
  require_approval
}

# 否则放行
allow_final {
  not deny
  not require_approval
}

# 输出
allow := allow_final
