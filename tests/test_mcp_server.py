"""
MCP Server 修复与增强测试。

覆盖 v2.4.2 的改动：
1. 资源根解析（packaged/dev/AGENTSEED_REPO 三级回退）
2. governance_check 工具名无关的 P0 匹配（任意工具名拦截破坏性操作/密钥/MCP 自装）
3. persona_list 不依赖 AGENTSEED_REPO 即可返回内置人设
4. HTTP 传输（POST /mcp + GET /healthz）
5. CLI --json 结构化输出

运行: python -m pytest tests/test_mcp_server.py -v
"""
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _no_agentseed_env():
    """测试资源解析时不受用户环境 AGENTSEED_REPO 影响。"""
    saved = os.environ.pop("AGENTSEED_REPO", None)
    yield
    if saved is not None:
        os.environ["AGENTSEED_REPO"] = saved


# ─── 1. 资源根解析 ────────────────────────────────────────────────

def test_resources_root_resolves_to_valid_hub():
    """默认解析结果必须含 personas/ 与 core/constraints.yaml（否则 governance 全放行）。"""
    from agentseed import mcp_server as ms
    root = ms._resolve_resources_root()
    assert (root / "personas").is_dir(), f"资源根缺少 personas/: {root}"
    assert (root / "core" / "constraints.yaml").exists(), f"资源根缺少 constraints.yaml: {root}"


def test_resources_root_env_override(monkeypatch, tmp_path):
    """AGENTSEED_REPO 应优先于 packaged/dev 布局。"""
    from agentseed import mcp_server as ms
    fake = tmp_path / "hub"
    (fake / "personas").mkdir(parents=True)
    monkeypatch.setenv("AGENTSEED_REPO", str(fake))
    assert ms._resolve_resources_root() == fake.resolve()


# ─── 2. governance_check 工具名无关匹配 ──────────────────────────

def test_governance_blocks_rm_rf_any_tool_name():
    """破坏性命令无论上报什么工具名都应拦截（修复前仅 bash/terminal/git）。"""
    from agentseed import mcp_server as ms
    for name in ("shell_executor", "Bash", "run_command", "command_executor", "powershell"):
        r = ms._handle_governance_check({"tool_name": name,
                                         "tool_args": {"command": "rm -rf /etc/nginx"}})
        assert r["allowed"] is False, f"{name}: {r}"
        assert r["risk_level"] == "P0"


def test_governance_allows_safe_command():
    from agentseed import mcp_server as ms
    r = ms._handle_governance_check({"tool_name": "Bash", "tool_args": {"command": "ls -la"}})
    assert r["allowed"] is True


def test_governance_blocks_secrets_in_write_tool():
    from agentseed import mcp_server as ms
    r = ms._handle_governance_check({"tool_name": "write_file",
                                     "tool_args": {"path": "conf.py",
                                                   "content": 'api_key = "sk-abcdefghijklmnopqrstuvwxyz123456"'}})
    assert r["allowed"] is False and r["risk_level"] == "P0"


def test_governance_blocks_mcp_auto_install():
    from agentseed import mcp_server as ms
    # shell 形式
    r1 = ms._handle_governance_check({"tool_name": "exec",
                                      "tool_args": {"command": "pip install mcp-server-foo"}})
    assert r1["allowed"] is False
    # 参数分离形式（如 Python 代码里的字符串字面量）
    r2 = ms._handle_governance_check({"tool_name": "exec",
                                      "tool_args": {"code": "subprocess.run(['pip','install','mcp-server-foo'])"}})
    assert r2["allowed"] is False


# ─── 3. persona / tools 基础可用性 ────────────────────────────────

def test_persona_list_not_empty_without_env():
    """修复前 wheel 安装下 persona_list 返回 []；修复后必须返回 6 个内置人设。"""
    from agentseed import mcp_server as ms
    personas = ms._handle_persona_list({})
    ids = [p["id"] for p in personas]
    assert "coding" in ids and "agent-builder" in ids
    assert len(ids) >= 5


def test_tools_list_via_json_rpc():
    from agentseed import mcp_server as ms
    resp = ms._handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = [t["name"] for t in resp["result"]["tools"]]
    assert names == ["governance_check", "persona_list", "persona_activate", "gap_detect",
                     "scenario_list", "scenario_activate"]


def test_scenario_aliases_work():
    """scenario_* 别名与 persona_* 行为一致（对外术语"场景规则包"）。"""
    from agentseed import mcp_server as ms
    r1 = ms._handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                             "params": {"name": "scenario_list", "arguments": {}}})
    packs = json.loads(r1["result"]["content"][0]["text"])
    assert "coding" in [p["id"] for p in packs]
    r2 = ms._handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                             "params": {"name": "scenario_activate",
                                        "arguments": {"persona_id": "coding"}}})
    data = json.loads(r2["result"]["content"][0]["text"])
    assert data["success"] is True


# ─── 4. HTTP 传输 ─────────────────────────────────────────────────

def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def http_server():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "agentseed.cli", "serve", "--port", str(port)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    base = f"http://127.0.0.1:{port}"
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(base + "/healthz", timeout=1) as resp:
                if resp.status == 200:
                    break
        except Exception:
            time.sleep(0.2)
    else:
        proc.terminate()
        pytest.fail("HTTP server did not become ready")
    yield base
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def test_http_healthz(http_server):
    with urllib.request.urlopen(http_server + "/healthz", timeout=5) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    assert body["ok"] is True
    assert body["name"] == "agentseed-mcp-server"


def test_http_json_rpc_tools_list(http_server):
    req = urllib.request.Request(
        http_server + "/mcp",
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list",
                         "params": {}}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    names = [t["name"] for t in body["result"]["tools"]]
    assert "governance_check" in names


# ─── 5. CLI --json ────────────────────────────────────────────────

def _run_cli(*argv) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "agentseed.cli", *argv],
        capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_cli_list_json():
    data = _run_cli("list", "--json")
    assert "profiles" in data and "tools" in data
    assert any(t["id"] == "agents-md" for t in data["tools"])
    assert any(t["id"] == "qwenwork" for t in data["tools"]), "qwenwork 应注册为内置平台"


def test_cli_platform_list_json():
    data = _run_cli("platform", "list", "--json")
    ids = [p["id"] for p in data["platforms"]]
    assert "qwenwork" in ids
    assert data["count"] == len(ids)


def test_cli_persona_list_json():
    data = _run_cli("persona", "list", "--json")
    assert "coding" in [p["id"] for p in data["personas"]]
