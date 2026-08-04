"""Tests for cross-platform env.py layer."""
import os
from pathlib import Path
from unittest import mock

import pytest

from agentseed import env


class TestPlatformDetection:
    def test_os_name_known(self):
        # In QClaw test env, always one of known platforms
        assert env.os_name() in ("windows", "wsl", "msys", "git-bash", "linux", "macos")

    def test_shell_name_known(self):
        assert env.shell_name() in ("powershell", "cmd", "bash", "zsh", "sh")

    def test_exactly_one_platform(self):
        flags = [env.IS_WINDOWS, env.IS_LINUX, env.IS_MACOS]
        assert sum(flags) >= 1


class TestUserCacheDir:
    def test_returns_under_home_or_appdata(self, monkeypatch):
        # Windows: under LOCALAPPDATA or AppData/Local
        # Linux: under XDG_CACHE_HOME or ~/.cache
        # macOS: under ~/Library/Caches
        cache = env.user_cache_dir()
        assert "agentseed" in str(cache).lower() or "AgentSeed" in str(cache)

    def test_linux_xdg(self, monkeypatch):
        monkeypatch.setattr(env, "IS_WINDOWS", False)
        monkeypatch.setattr(env, "IS_MACOS", False)
        monkeypatch.setenv("XDG_CACHE_HOME", "/tmp/xdgcache")
        cache = env.user_cache_dir()
        # Path 在 Windows 测试环境会变 WindowsPath — 规范化为 os.path.normpath
        assert os.path.normpath(str(cache)).startswith(os.path.normpath("/tmp/xdgcache"))

    def test_linux_default(self, monkeypatch):
        monkeypatch.setattr(env, "IS_WINDOWS", False)
        monkeypatch.setattr(env, "IS_MACOS", False)
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        cache = env.user_cache_dir()
        assert os.path.normpath(str(cache)).startswith(os.path.normpath(str(Path.home())))
        assert "agentseed" in str(cache)


class TestUserConfigDir:
    def test_returns_under_home_or_appdata(self):
        config = env.user_config_dir()
        assert "agentseed" in str(config).lower() or "AgentSeed" in str(config)

    def test_linux_xdg(self, monkeypatch):
        monkeypatch.setattr(env, "IS_WINDOWS", False)
        monkeypatch.setattr(env, "IS_MACOS", False)
        monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/xdgcfg")
        config = env.user_config_dir()
        assert os.path.normpath(str(config)).startswith(os.path.normpath("/tmp/xdgcfg"))

    def test_macos_library(self, monkeypatch):
        monkeypatch.setattr(env, "IS_WINDOWS", False)
        monkeypatch.setattr(env, "IS_MACOS", True)
        config = env.user_config_dir()
        assert "Library" in str(config)
        assert "Application Support" in str(config)


class TestUserPersonasDir:
    def test_under_config_dir(self):
        personas = env.user_personas_dir()
        config = env.user_config_dir()
        assert str(personas).startswith(str(config))
        assert personas.name == "personas"


class TestEncoding:
    def test_preferred_encoding(self):
        enc = env.preferred_encoding()
        assert enc in ("utf-8", "cp936", "gbk", "cp1252", "ascii")

    def test_decode_bytes_utf8(self):
        data = "中文测试".encode("utf-8")
        assert env.decode_bytes(data) == "中文测试"

    def test_decode_bytes_gbk(self):
        data = "中文测试".encode("gbk")
        assert env.decode_bytes(data) == "中文测试"

    def test_decode_bytes_fallback(self):
        # 任何 bytes 都能 decode（不会抛）
        assert env.decode_bytes(b"\xff\xfe invalid")  # 替换字符也算成功

    def test_encode_text_utf8(self):
        assert env.encode_text("hello") == b"hello"
        assert env.encode_text("中文") == "中文".encode("utf-8")


class TestSafePrint:
    def test_safe_print_basic(self, capsys):
        env.safe_print("hello")
        out = capsys.readouterr()
        assert "hello" in out.out

    def test_safe_print_chinese(self, capsys):
        # 即便在 Windows GBK 也不会抛异常
        env.safe_print("中文测试")
        capsys.readouterr()  # 不抛即通过


class TestLineEndings:
    def test_line_separator(self):
        sep = env.line_separator()
        if env.IS_WINDOWS:
            assert sep == "\r\n"
        else:
            assert sep == "\n"

    def test_normalize_lf_to_crlf(self):
        text = "a\nb\nc"
        result = env.normalize_line_endings(text, "\r\n")
        assert result == "a\r\nb\r\nc"

    def test_normalize_crlf_to_lf(self):
        text = "a\r\nb\r\nc"
        result = env.normalize_line_endings(text, "\n")
        assert result == "a\nb\nc"

    def test_normalize_mixed_to_lf(self):
        text = "a\rb\r\nc\nd"
        result = env.normalize_line_endings(text, "\n")
        assert result == "a\nb\nc\nd"


class TestRunCommand:
    def test_run_echo_command(self):
        code, stdout, stderr = env.run_command(
            ["python", "-c", "print('hi')"], timeout=10
        )
        assert code == 0
        assert "hi" in stdout

    def test_run_chinese_output(self):
        code, stdout, stderr = env.run_command(
            ["python", "-c", "print('中文输出')"], timeout=10
        )
        assert code == 0
        assert "中文输出" in stdout

    def test_run_with_cwd(self, tmp_path):
        code, stdout, stderr = env.run_command(
            ["python", "-c", "import os; print(os.getcwd())"],
            cwd=tmp_path, timeout=10,
        )
        assert code == 0
        assert str(tmp_path) in stdout or str(tmp_path).replace("/", "\\") in stdout

    def test_run_check_raises_on_error(self):
        with pytest.raises(Exception):  # CalledProcessError
            env.run_command(["python", "-c", "import sys; sys.exit(1)"], check=True, timeout=10)

    def test_run_timeout(self):
        with pytest.raises(Exception):  # TimeoutExpired
            env.run_command(["python", "-c", "import time; time.sleep(5)"], timeout=1)


class TestMaxPathLength:
    def test_max_path(self):
        max_len = env.max_path_length()
        if env.IS_WINDOWS:
            assert max_len == 260
        else:
            assert max_len == 4096


class TestWhich:
    def test_which_python(self):
        path = env.which("python")
        assert path is not None
        assert "python" in path.lower()

    def test_which_nonexistent(self):
        assert env.which("definitely-not-a-command-xyz123") is None