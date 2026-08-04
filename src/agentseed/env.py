"""
环境适配层 — 跨平台抽象（Windows / Linux / macOS / WSL / MSYS）。

所有平台相关的代码都集中到这里：
- 编码 (UTF-8 / GBK / CP936)
- 路径 (~/.cache / %APPDATA% / XDG_CACHE_HOME)
- 命令 (powershell / bash / zsh / cmd)
- 行尾 (CRLF / LF)
- 行长度限制 (Win 8191 / *nix 4096)
- 文本流包装 (reconfigure stdout/stderr 为 UTF-8)

设计原则：
- 不假设任何特定平台，用 platform.system() / sys.platform 检测
- 在检测时设置 PYTHONIOENCODING=utf-8 / PYTHONUTF8=1
- 提供 safe_print() / safe_input() 跨平台输出/输入中文
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


# ───────────────────────────────────────────────────────────────────────
# 平台检测
# ───────────────────────────────────────────────────────────────────────

IS_WINDOWS = sys.platform.startswith("win") or sys.platform == "cygwin"
IS_LINUX = sys.platform.startswith("linux")
IS_MACOS = sys.platform == "darwin"
IS_WSL = IS_LINUX and "microsoft" in platform.release().lower()
IS_MSYS = IS_WINDOWS and "MSYS" in os.environ.get("MSYSTEM", "")
IS_GIT_BASH = IS_WINDOWS and shutil.which("bash") is not None and os.environ.get("TERM") == "xterm-256color"


def os_name() -> str:
    """返回可读的平台名（用于诊断输出）。"""
    if IS_WSL:
        return "wsl"
    if IS_MSYS:
        return "msys"
    if IS_GIT_BASH:
        return "git-bash"
    if IS_WINDOWS:
        return "windows"
    if IS_MACOS:
        return "macos"
    if IS_LINUX:
        return "linux"
    return sys.platform


def shell_name() -> str:
    """检测当前 shell。"""
    if IS_WINDOWS:
        if os.environ.get("PSModulePath"):
            return "powershell"
        if os.environ.get("BASH"):
            return "bash"
        return "cmd"
    if os.environ.get("ZSH_VERSION"):
        return "zsh"
    if os.environ.get("BASH_VERSION"):
        return "bash"
    return os.environ.get("SHELL", "sh").split("/")[-1] or "sh"


# ───────────────────────────────────────────────────────────────────────
# 路径
# ───────────────────────────────────────────────────────────────────────

def user_cache_dir() -> Path:
    """跨平台用户缓存目录（XDG 规范 + Windows %LOCALAPPDATA%）。

    Linux/macOS:  $XDG_CACHE_HOME/agentseed  或  ~/.cache/agentseed
    Windows:      %LOCALAPPDATA%/agentseed  或  ~/AppData/Local/agentseed
    """
    if IS_WINDOWS:
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if not base:
            base = str(Path.home() / "AppData" / "Local")
        return Path(base) / "agentseed"
    # Linux/macOS — XDG 规范
    base = os.environ.get("XDG_CACHE_HOME")
    if base:
        return Path(base) / "agentseed"
    return Path.home() / ".cache" / "agentseed"


def user_config_dir() -> Path:
    """跨平台用户配置目录。

    Linux:   $XDG_CONFIG_HOME/agentseed  或  ~/.config/agentseed
    macOS:   ~/Library/Application Support/agentseed
    Windows: %APPDATA%/agentseed
    """
    if IS_WINDOWS:
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "agentseed"
    if IS_MACOS:
        return Path.home() / "Library" / "Application Support" / "agentseed"
    base = os.environ.get("XDG_CONFIG_HOME")
    if base:
        return Path(base) / "agentseed"
    return Path.home() / ".config" / "agentseed"


def user_personas_dir() -> Path:
    """用户级 personas 目录（market install 用户画像用）。"""
    return user_config_dir() / "personas"


# ───────────────────────────────────────────────────────────────────────
# 编码
# ───────────────────────────────────────────────────────────────────────

def configure_utf8() -> None:
    """将 stdout/stderr 重设为 UTF-8（解决 Windows GBK 乱码）。

    在模块导入时自动调用一次。也可在用户脚本开头调用。
    """
    if not IS_WINDOWS:
        return  # Linux/macOS 默认 UTF-8
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        try:
            # reconfigure 只在 Python 3.7+ 且流未被替换时可用
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def preferred_encoding() -> str:
    """返回当前平台推荐的文本编码。"""
    if IS_WINDOWS:
        # 优先 UTF-8（已 reconfigure）；fallback 到控制台编码（CP936/GBK）
        try:
            return sys.stdout.encoding or "utf-8"
        except Exception:
            return "utf-8"
    return "utf-8"


def decode_bytes(data: bytes) -> str:
    """智能解码 bytes → str（Windows 兼容 GBK/UTF-8）。"""
    for enc in ("utf-8", "gbk", "cp936", "latin-1"):
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="replace")


def encode_text(text: str) -> bytes:
    """编码 str → bytes（用 UTF-8）。"""
    return text.encode("utf-8")


# ───────────────────────────────────────────────────────────────────────
# 安全打印（跨平台中文输出）
# ───────────────────────────────────────────────────────────────────────

def safe_print(*args, sep: str = " ", end: str = "\n", file=None, flush: bool = False) -> None:
    """安全的 print：自动处理 Windows GBK 编码失败（用 errors='replace'）。"""
    if file is None:
        file = sys.stdout
    text = sep.join(str(a) for a in args) + end
    try:
        file.write(text)
        if flush:
            file.flush()
    except UnicodeEncodeError:
        # 最后兜底：替换无法编码的字符
        enc = preferred_encoding()
        encoded = text.encode(enc, errors="replace").decode(enc, errors="replace")
        file.write(encoded)
        if flush:
            file.flush()


def safe_input(prompt: str = "") -> str:
    """安全的 input：避免 Windows 控制台编码错误。"""
    if prompt:
        safe_print(prompt, end="")
    try:
        return input()
    except UnicodeDecodeError:
        # 用 stdin 直接读 bytes 再解码
        try:
            raw = sys.stdin.buffer.readline()
            return decode_bytes(raw).rstrip("\r\n")
        except Exception:
            return ""


# ───────────────────────────────────────────────────────────────────────
# 行尾 / 文本规范化
# ───────────────────────────────────────────────────────────────────────

def line_separator() -> str:
    """返回当前平台的行尾。"""
    return "\r\n" if IS_WINDOWS else "\n"


def normalize_line_endings(text: str, to: Optional[str] = None) -> str:
    """统一行尾。to=None 时用当前平台的行尾。"""
    if to is None:
        to = line_separator()
    # 先把所有 CRLF/LF/CR 统一为 LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if to == "\n":
        return text
    return text.replace("\n", to)


def max_path_length() -> int:
    """当前平台的路径最大长度。"""
    if IS_WINDOWS:
        return 260  # MAX_PATH; 长路径支持需 \?\ 前缀
    return 4096  # Linux/macOS PATH_MAX


# ───────────────────────────────────────────────────────────────────────
# 命令执行（跨平台 subprocess）
# ───────────────────────────────────────────────────────────────────────

def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
    timeout: Optional[float] = None,
    check: bool = False,
    capture: bool = True,
) -> Tuple[int, str, str]:
    """跨平台执行命令（不用 shell=True 防注入）。

    Returns: (exit_code, stdout, stderr)
    """
    # 合并环境：优先用户传入，但保留系统 PATH/HOME 等关键变量
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    # Windows: 确保 PYTHONIOENCODING= utf-8
    if IS_WINDOWS:
        merged_env.setdefault("PYTHONIOENCODING", "utf-8")
        merged_env.setdefault("PYTHONUTF8", "1")

    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=merged_env,
        capture_output=capture,
        text=False,  # bytes mode → 跨平台编码
        timeout=timeout,
        check=False,
        shell=False,  # 防止 shell 注入
    )
    stdout = decode_bytes(proc.stdout) if proc.stdout else ""
    stderr = decode_bytes(proc.stderr) if proc.stderr else ""

    if check and proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd, stdout, stderr)

    return proc.returncode, stdout, stderr


def which(cmd: str) -> Optional[str]:
    """跨平台 which 命令。"""
    return shutil.which(cmd)


# ───────────────────────────────────────────────────────────────────────
# 平台特定工具
# ───────────────────────────────────────────────────────────────────────

def line_ending_safe_write(path: Path, content: str) -> None:
    """写入文件，自动处理行尾。"""
    content = normalize_line_endings(content)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")


# 自动配置一次
configure_utf8()
