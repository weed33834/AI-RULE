"""AgentSeed MCP Server — stdio / HTTP JSON-RPC 2.0 protocol.

Exposes governance / persona management as MCP tools for any MCP-compatible client.

Usage:
    agentseed serve          # stdio mode (default, for MCP clients)
    agentseed serve --port N # HTTP mode (JSON-RPC over POST /mcp, stdlib only)
"""

__version__ = "1.0.0"

import json
import sys
import os
from pathlib import Path
from typing import Any

# ── resolve resources root ───────────────────────────────────────
_PACK_DIR_NAMES = ("scenarios", "personas")  # scenarios 优先（未来规范目录），personas 兼容


def _has_pack_dir(p: Path) -> bool:
    """目录是否为 AgentSeed 资源根（含场景包目录 scenarios/ 或 personas/）。"""
    return any((p / name).is_dir() for name in _PACK_DIR_NAMES)


def _pack_dir(root: Path) -> Path:
    """返回场景包目录：scenarios/ 优先，personas/ 兼容回退。"""
    for name in _PACK_DIR_NAMES:
        cand = root / name
        if cand.is_dir():
            return cand
    return root / "personas"


def _resolve_resources_root() -> Path:
    """Resolve the rule-hub resources root.

    Priority (mirrors sync_rules._find_rule_hub_root):
      1. AGENTSEED_REPO env var — explicit user override, hot-swappable
      2. packaged layout: <pkg>/_resources   (pip wheel install)
      3. dev/source layout: <repo>/src/agentseed -> parent.parent = repo root
      4. legacy fallback: parent.parent.parent (kept for backwards compat)

    The old single-path logic (`parent.parent.parent`) pointed at the wrong
    directory in wheel installs, silently disabling persona/constraint loading.
    """
    env = os.environ.get("AGENTSEED_REPO", "")
    if env:
        p = Path(env).expanduser().resolve()
        if _has_pack_dir(p):
            return p

    pkg = Path(__file__).resolve().parent / "_resources"
    if _has_pack_dir(pkg):
        return pkg

    dev = Path(__file__).resolve().parent.parent
    if _has_pack_dir(dev):
        return dev

    legacy = Path(__file__).resolve().parent.parent.parent
    return legacy


def _force_utf8_streams() -> None:
    """Force UTF-8 on stdout/stderr so JSON-RPC survives Windows GBK locales.

    MCP stdio transport is UTF-8 by spec; without this, Chinese persona names
    are emitted as GBK bytes on zh-CN Windows and corrupt the stream for MCP
    clients. Safe no-op when the stream is not reconfigurable (e.g. consoles).
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


# ── constraints.yaml loader ───────────────────────────────────────

def _load_constraints() -> dict:
    """Load core/constraints.yaml from resources root."""
    root = _resolve_resources_root()
    yaml_path = root / "core" / "constraints.yaml"
    if not yaml_path.exists():
        return {"constraints": []}
    # Simple YAML subset parser (enough for our constraints.yaml)
    with open(yaml_path, "r", encoding="utf-8") as f:
        content = f.read()
    return _parse_simple_yaml(content)


def _parse_simple_yaml(content: str) -> dict:
    """Parse a minimal subset of YAML — only what constraints.yaml needs."""
    import re

    result: dict = {"constraints": []}
    constraints: list = []
    current: dict = {}
    in_match = False
    match_lines: list = []

    for line in content.splitlines():
        # Skip comments and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Detect top-level keys
        if stripped.startswith("version:") or stripped.startswith("source:"):
            continue

        # Start of a new constraint
        if stripped.startswith("- id:"):
            if current:
                constraints.append(current)
            current = {"id": stripped.split(":", 1)[1].strip()}
            in_match = False
            match_lines = []
            continue

        # Inside a constraint
        if current:
            if stripped.startswith("description:"):
                current["description"] = stripped.split(":", 1)[1].strip().strip('"')
            elif stripped.startswith("severity:"):
                current["severity"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("action:"):
                current["action"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("match:"):
                in_match = True
                match_lines = []
                continue
            elif in_match:
                if stripped.startswith("command_regex:"):
                    val = stripped.split(":", 1)[1].strip().lstrip(">").strip()
                    match_lines.append(val)
                elif stripped.startswith("content_regex:"):
                    val = stripped.split(":", 1)[1].strip().lstrip(">").strip()
                    match_lines.append(val)
                elif stripped.startswith("file_path_patterns:"):
                    val = stripped.split(":", 1)[1].strip()
                    match_lines.append(val)
            if not stripped.startswith(" ") and not stripped.startswith("- "):
                # Exiting constraint
                pass

    if current:
        constraints.append(current)

    result["constraints"] = constraints
    # Count P0 constraints
    p0_count = sum(1 for c in constraints if c.get("severity") == "P0")
    result["meta"] = {"total_p0": p0_count}
    return result


# ── persona helpers ────────────────────────────────────────────────

def _list_personas() -> list:
    """List scenario packs from the packs directory (scenarios/ or personas/)."""
    root = _resolve_resources_root()
    personas_dir = _pack_dir(root)
    if not personas_dir.exists():
        return []

    results = []
    for entry in sorted(personas_dir.iterdir()):
        if not entry.is_dir() or entry.name.startswith("_"):
            continue
        yaml_path = entry / "persona.yaml"
        if not yaml_path.exists():
            continue
        info = _read_persona_info(yaml_path)
        results.append({"id": entry.name, "name": info.get("name", entry.name),
                        "description": info.get("description", "")})
    return results


def _read_persona_info(yaml_path: Path) -> dict:
    """Extract basic info from a persona.yaml."""
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return {}
    info = {}
    in_profile = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "profile:":
            in_profile = True
            continue
        if in_profile:
            if stripped.startswith("id:"):
                info["id"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("name:"):
                info["name"] = stripped.split(":", 1)[1].strip()
            elif not stripped.startswith(" "):
                break
    return info


def _load_persona_config(persona_id: str) -> dict:
    """Load full persona.yaml for a given scenario pack."""
    root = _resolve_resources_root()
    yaml_path = _pack_dir(root) / persona_id / "persona.yaml"
    if not yaml_path.exists():
        return {}
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return {}

    info: dict = {}
    current_section = None
    includes_core = []
    includes_profile = []
    includes_skills = []
    enables = []
    forbids = []
    anchors = []
    keywords = []

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("profile:"):
            current_section = "profile"
            continue
        elif stripped.startswith("includes:"):
            current_section = "includes"
            continue
        elif stripped.startswith("enables_capabilities:"):
            current_section = "enables"
            continue
        elif stripped.startswith("forbids_capabilities:"):
            current_section = "forbids"
            continue
        elif stripped.startswith("activation_anchors:"):
            current_section = "anchors"
            continue
        elif stripped.startswith("intent_keywords:"):
            current_section = "keywords"
            continue
        elif stripped.startswith("mutually_exclusive_with:"):
            current_section = "mutex"
            continue

        if current_section == "profile":
            if stripped.startswith("id:"):
                info["id"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("name:"):
                info["name"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("source_repo:"):
                info["source_repo"] = stripped.split(":", 1)[1].strip()
        elif current_section == "includes":
            if stripped.startswith("- "):
                path = stripped[2:].strip()
                if path.startswith("core/"):
                    includes_core.append(path)
                elif path.startswith("personas/"):
                    includes_profile.append(path)
                elif path.startswith("personas/") and "/skills/" in path:
                    includes_skills.append(path)
                else:
                    includes_skills.append(path)
        elif current_section == "enables":
            if stripped.startswith("- "):
                enables.append(stripped[2:].strip())
        elif current_section == "forbids":
            if stripped.startswith("- "):
                forbids.append(stripped[2:].strip())
        elif current_section == "anchors":
            if stripped.startswith("- "):
                anchors.append(stripped[2:].strip())
        elif current_section == "keywords":
            if stripped.startswith("- "):
                keywords.append(stripped[2:].strip())
        elif current_section == "mutex":
            if stripped.startswith("- "):
                mutex = info.setdefault("mutually_exclusive_with", [])
                mutex.append(stripped[2:].strip())

    info["includes"] = {"core": includes_core, "profile": includes_profile, "skills": includes_skills}
    info["capabilities"] = {"enables": enables, "forbids": forbids}
    info["anchors"] = anchors
    info["keywords"] = keywords

    # Platform files that would be affected
    info["platform_files"] = [
        "AGENTS.md", "CLAUDE.md", "GEMINI.md",
        ".cursor/rules/project_rules.mdc",
        ".github/copilot-instructions.md",
        ".trae/rules/project_rules.md",
        ".windsurfrules",
    ]
    return info


# ── gap detection ──────────────────────────────────────────────────

def _compute_gap_score(context: str) -> dict:
    """Analyze context string for capability gaps based on self-evolution.md logic."""
    context_lower = context.lower()

    # Check for missing tool / knowledge indicators
    missing_tool = 0.0
    missing_knowledge = 0.0
    urgency = 0.5  # default implicit
    alternatives_exhausted = 0.0
    risk = 1.0  # default low risk

    tool_keywords = ["need tool", "缺少工具", "no tool", "can't do", "做不到", "找不到工具"]
    knowledge_keywords = ["don't know", "不知道", "not familiar", "不熟悉", "outside domain", "超出范围"]

    if any(kw in context_lower for kw in tool_keywords):
        missing_tool = 0.8
    if any(kw in context_lower for kw in knowledge_keywords):
        missing_knowledge = 0.8

    # Explicit urgency
    urgency_keywords = ["must", "urgent", "critical", "必须", "紧急", "关键", "important"]
    if any(kw in context_lower for kw in urgency_keywords):
        urgency = 1.0

    # Alternatives exhausted
    alt_keywords = ["tried everything", "已经试过", "exhausted", "no alternatives"]
    if any(kw in context_lower for kw in alt_keywords):
        alternatives_exhausted = 1.0

    # Risk check
    risk_keywords = ["delete", "format", "drop", "删除", "格式化", "destroy"]
    if any(kw in context_lower for kw in risk_keywords):
        risk = 0.3  # higher risk → lower score

    gap_score = (
        0.35 * missing_tool
        + 0.25 * missing_knowledge
        + 0.20 * urgency
        + 0.10 * alternatives_exhausted
        + 0.10 * risk
    )

    gaps = []
    suggestions = []

    if missing_tool > 0:
        gaps.append("missing_tool")
        suggestions.append("搜索或安装匹配的工具/技能")
    if missing_knowledge > 0:
        gaps.append("missing_knowledge")
        suggestions.append("使用 web_search 获取领域知识或加载对应 Persona Pack")
    if gap_score < 0.30:
        suggestions.append("缺口很小，使用现有能力尽力回答")
    elif gap_score < 0.55:
        suggestions.append("输出建议命令供用户手动执行")
    elif gap_score < 0.75:
        suggestions.append("执行低风险自动获取（搜索/下载公开资源）")
    else:
        suggestions.append("全自动获取并热加载（P0 除外）")

    return {"gaps": gaps, "suggestions": suggestions, "gap_score": round(gap_score, 3)}


# ── MCP tool handlers ──────────────────────────────────────────────

def _collect_strings(value: Any, acc: list) -> None:
    """Recursively collect all string leaves from tool args for command scanning."""
    if isinstance(value, str):
        acc.append(value)
    elif isinstance(value, dict):
        for v in value.values():
            _collect_strings(v, acc)
    elif isinstance(value, (list, tuple)):
        for v in value:
            _collect_strings(v, acc)


def _handle_governance_check(args: dict) -> dict:
    """Check if a tool call violates P0 security red lines.

    Tool-name agnostic: command-bearing arguments (command/cmd/code/script/...)
    are scanned regardless of the reported tool name, so clients that report
    non-standard tool names (e.g. shell_executor) get the same protection as
    bash/terminal/git. Secrets are matched against the full serialized call.
    """
    tool_name = args.get("tool_name", "")
    tool_args = args.get("tool_args", {}) or {}

    constraints = _load_constraints()
    p0_constraints = [c for c in constraints.get("constraints", [])
                      if c.get("severity") == "P0"]

    if not p0_constraints:
        return {"allowed": True, "reason": "No P0 constraints loaded", "risk_level": "none"}

    # Collect every string leaf of the args, then scan the union as command text.
    strings: list = []
    _collect_strings(tool_args, strings)
    cmd_text = "\n".join(strings)
    tool_call_str = json.dumps({"tool": tool_name, "args": tool_args}, ensure_ascii=False)

    for c in p0_constraints:
        cid = c.get("id", "")

        # DESTRUCTIVE_OP check — any tool whose args carry a destructive command
        if cid == "DESTRUCTIVE_OP_REQUIRES_CONFIRM":
            destructive_patterns = ["rm -rf", "rm -r ", "git push --force", "git push -f",
                                    "git reset --hard", "git clean -fd", "DROP TABLE",
                                    "DROP DATABASE", "TRUNCATE TABLE"]
            if any(p in cmd_text for p in destructive_patterns):
                return {"allowed": False,
                        "reason": f"[P0 {cid}] 破坏性操作已拦截，需用户确认",
                        "risk_level": "P0"}

        # SECRETS check — any tool whose args carry hardcoded secret material
        if cid == "SECRETS_NO_HARDCODE":
            import re
            secret_patterns = [
                r'sk-[A-Za-z0-9]{20,}',
                r'ghp_[A-Za-z0-9]{36,}',
                r'AKIA[0-9A-Z]{16}',
                r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
            ]
            if any(re.search(pattern, tool_call_str) for pattern in secret_patterns):
                return {"allowed": False,
                        "reason": f"[P0 {cid}] 检测到疑似硬编码密钥",
                        "risk_level": "P0"}

        # MCP_NO_AUTO_INSTALL check — any command that installs MCP servers
        if cid == "MCP_NO_AUTO_INSTALL":
            install_keywords = ["install", "npm", "pip", "npx", "uvx", "pipx"]
            if "mcp" in cmd_text.lower() and any(k in cmd_text.lower() for k in install_keywords):
                return {"allowed": False,
                        "reason": f"[P0 {cid}] AI 禁止自行安装 MCP",
                        "risk_level": "P0"}

    return {"allowed": True, "reason": "All P0 checks passed", "risk_level": "none"}


def _handle_persona_list(args: dict) -> list:
    """List all available persona packs."""
    return _list_personas()


def _handle_persona_activate(args: dict) -> dict:
    """Activate a persona and return config summary."""
    persona_id = args.get("persona_id", "")
    if not persona_id:
        return {"success": False, "persona": {}, "platform_files": [],
                "error": "persona_id is required"}

    config = _load_persona_config(persona_id)
    if not config:
        return {"success": False, "persona": {}, "platform_files": [],
                "error": f"Persona '{persona_id}' not found"}

    return {
        "success": True,
        "persona": {
            "id": config.get("id", persona_id),
            "name": config.get("name", ""),
            "capabilities": config.get("capabilities", {}),
            "anchors": config.get("anchors", []),
            "keywords": config.get("keywords", []),
        },
        "platform_files": config.get("platform_files", []),
    }


def _handle_gap_detect(args: dict) -> dict:
    """Detect capability gaps in the given context."""
    context = args.get("context", "")
    return _compute_gap_score(context)


# ── JSON-RPC 2.0 server ────────────────────────────────────────────

_TOOL_HANDLERS = {
    "governance_check": _handle_governance_check,
    "persona_list": _handle_persona_list,
    "persona_activate": _handle_persona_activate,
    "gap_detect": _handle_gap_detect,
    # scenario_* 为 persona_* 的规范别名（对外术语"场景规则包"）；旧名保留兼容
    "scenario_list": _handle_persona_list,
    "scenario_activate": _handle_persona_activate,
}

_TOOL_SCHEMAS = {
    "governance_check": {
        "description": "Check if a tool call violates P0 security red lines (destructive ops, hardcoded secrets, "
                       "auto-installing MCP servers). Tool-name agnostic: command strings are extracted from any "
                       "tool's arguments, so clients reporting non-standard tool names get the same protection.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tool_name": {"type": "string", "description": "Name of the tool to check"},
                "tool_args": {"type": "object", "description": "Arguments passed to the tool"},
            },
            "required": ["tool_name", "tool_args"],
        },
    },
    "persona_list": {
        "description": "List available scenario packs (场景规则包) from personas/ directory",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    "persona_activate": {
        "description": "Activate a scenario pack (场景规则包) and return its configuration summary",
        "inputSchema": {
            "type": "object",
            "properties": {
                "persona_id": {"type": "string", "description": "Scenario pack identifier"},
            },
            "required": ["persona_id"],
        },
    },
    "gap_detect": {
        "description": "Analyze context for capability gaps based on core/self-evolution.md gap score formula",
        "inputSchema": {
            "type": "object",
            "properties": {
                "context": {"type": "string", "description": "Context string to analyze for gaps"},
            },
            "required": ["context"],
        },
    },
    # 规范别名（对外术语"场景规则包"）；persona_* 保留为兼容旧客户端
    "scenario_list": {
        "description": "List available scenario packs (场景规则包). Alias of persona_list.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    "scenario_activate": {
        "description": "Activate a scenario pack (场景规则包) and return its configuration summary. "
                       "Alias of persona_activate.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "persona_id": {"type": "string", "description": "Scenario pack identifier"},
            },
            "required": ["persona_id"],
        },
    },
}

_SERVER_INFO = {
    "name": "agentseed-mcp-server",
    "version": "1.0.0",
}


def _send_json(data: dict) -> None:
    """Write JSON-RPC response to stdout."""
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _handle_request(request: dict) -> dict | None:
    """Handle a single JSON-RPC request. Returns response dict or None for notifications."""
    req_id = request.get("id")
    method = request.get("method", "")
    params = request.get("params", {})

    # initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": _SERVER_INFO,
                "capabilities": {"tools": {}},
            },
        }

    # notifications (no response)
    if method == "notifications/initialized":
        return None

    # tools/list
    if method == "tools/list":
        tools = []
        for name, schema in _TOOL_SCHEMAS.items():
            tools.append({"name": name, **schema})
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}

    # ping (MCP 2024-11-05 heartbeat)
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    # tools/call
    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        handler = _TOOL_HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Tool not found: {tool_name}"}],
                    "isError": True,
                },
            }
        try:
            result = handler(tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]},
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": str(e)}],
                    "isError": True,
                },
            }

    # method not found
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def _log(msg: str) -> None:
    """Log diagnostic messages to stderr (MCP convention: stdout is data, stderr is logs)."""
    print(f"[AgentSeed MCP] {msg}", file=sys.stderr, flush=True)


def run_stdio() -> None:
    """Run MCP server over stdio (JSON-RPC 2.0 line-delimited)."""
    _force_utf8_streams()
    _log(f"Server v{_SERVER_INFO['version']} starting in stdio mode")
    _log("Waiting for initialize request...")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as e:
            _log(f"Invalid JSON received: {e}")
            continue
        method = request.get("method", "")
        req_id = request.get("id", "")
        if method:
            _log(f"← {method} (id={req_id})")
        response = _handle_request(request)
        if response is not None:
            if "error" in response:
                _log(f"→ error: {response['error'].get('message', '')}")
            else:
                _log(f"→ success (id={req_id})")
            _send_json(response)


def run_http(port: int = 8080) -> None:
    """Run MCP server over HTTP (JSON-RPC 2.0, stdlib only, no third-party deps).

    Minimal transport for remote / agent-to-agent usage:
      POST /mcp      — JSON-RPC request, JSON response (Content-Type: application/json)
      GET  /healthz  — {"ok": true, "name": ..., "version": ...}

    Notes:
      - Streamable-HTTP / SSE transports are not implemented; for MCP client
        integration prefer stdio mode (`agentseed serve`).
      - Binds to 127.0.0.1 only — do not expose to untrusted networks.
    """
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    _force_utf8_streams()

    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # route request logs to stderr via _log
            _log(fmt % args)

        def _send_json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path.rstrip("/") in ("/healthz", "/health"):
                self._send_json(200, {"ok": True, **_SERVER_INFO})
                return
            self._send_json(404, {"error": "not found", "hint": "POST /mcp or GET /healthz"})

        def do_POST(self) -> None:
            if self.path.rstrip("/") != "/mcp":
                self._send_json(404, {"error": "not found", "hint": "POST /mcp or GET /healthz"})
                return
            try:
                length = int(self.headers.get("Content-Length", 0) or 0)
                raw = self.rfile.read(length) if length else b""
                request = json.loads(raw.decode("utf-8"))
            except Exception as e:
                self._send_json(400, {"jsonrpc": "2.0", "id": None,
                                      "error": {"code": -32700, "message": f"Parse error: {e}"}})
                return
            response = _handle_request(request)
            if response is None:  # notification — acknowledge with an empty result
                response = {"jsonrpc": "2.0", "id": None, "result": None}
            _log(f"http {request.get('method', '?')} id={request.get('id')}")
            self._send_json(200, response)

    _log(f"Server v{_SERVER_INFO['version']} starting in HTTP mode on port {port}")
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    _log(f"Listening on http://127.0.0.1:{port}/mcp (GET /healthz) — Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        _log("HTTP server stopped")
        server.server_close()


# ── Public API ──────────────────────────────────────────────────────

def governance_check(tool_name: str, tool_args: dict) -> dict:
    """Public API: check if a tool call violates governance rules."""
    return _handle_governance_check({"tool_name": tool_name, "tool_args": tool_args})

def persona_list() -> list:
    """Public API: list all available persona packs."""
    return _handle_persona_list({})

def persona_activate(persona_id: str) -> dict:
    """Public API: activate a persona pack."""
    return _handle_persona_activate({"persona_id": persona_id})

def gap_detect(context: str) -> dict:
    """Public API: detect capability gaps in context."""
    return _handle_gap_detect({"context": context})


if __name__ == "__main__":
    run_stdio()
