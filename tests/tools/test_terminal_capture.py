"""Tests for thegent.tools.terminal_capture.

Covers:
- CaptureResult dataclass construction and defaults
- Each backend helper (_capture_via_tmux, _capture_via_zmx, _capture_via_proc,
  _capture_via_termitty) in isolation via mocking
- TerminalCapture.capture_last_n_lines fallback chain
- TerminalCapture.capture_by_pid fallback chain
- Trimming to n lines
- Graceful handling when every backend fails

# @trace FR-SES-001, FR-SES-002, FR-SES-003
"""

from __future__ import annotations

import platform
import sys
from dataclasses import fields
from typing import Any
from unittest.mock import MagicMock, patch

import pytest  # noqa: F401 -- imported for pytest.main at module bottom and fixtures

# thegent.tools.terminal_capture module was removed.
_terminal_capture = pytest.importorskip(
    "thegent.tools.terminal_capture",
    reason="thegent.tools.terminal_capture module removed; terminal capture tests skipped",
)
from thegent.tools.terminal_capture import (  # noqa: E402  (importorskip may skip before this)
    CaptureResult,
    TerminalCapture,
    _capture_via_proc,
    _capture_via_termitty,
    _capture_via_tmux,
    _capture_via_zmx,
    _is_tmux_available,
    _trim_to_n,
)

# ---------------------------------------------------------------------------
# CaptureResult dataclass tests
# ---------------------------------------------------------------------------


class TestCaptureResult:
    """FR-SES-001: CaptureResult must be a well-formed typed dataclass."""

    def test_default_backend_is_none(self) -> None:
        result = CaptureResult()
        assert result.backend == "none"

    def test_default_lines_is_empty_list(self) -> None:
        result = CaptureResult()
        assert result.lines == []

    def test_default_pane_id_is_none(self) -> None:
        result = CaptureResult()
        assert result.pane_id is None

    def test_custom_construction(self) -> None:
        result = CaptureResult(lines=["a", "b"], backend="tmux", pane_id="%1")
        assert result.lines == ["a", "b"]
        assert result.backend == "tmux"
        assert result.pane_id == "%1"

    def test_has_three_fields(self) -> None:
        assert len(fields(CaptureResult)) == 3

    def test_lines_are_independent_across_instances(self) -> None:
        r1 = CaptureResult()
        r2 = CaptureResult()
        r1.lines.append("x")
        assert r2.lines == [], "lines list must not be shared between instances"


# ---------------------------------------------------------------------------
# _trim_to_n helper
# ---------------------------------------------------------------------------


class TestTrimToN:
    def test_shorter_than_n_returns_all(self) -> None:
        assert _trim_to_n(["a", "b"], 5) == ["a", "b"]

    def test_longer_than_n_returns_last_n(self) -> None:
        assert _trim_to_n(list("abcde"), 3) == ["c", "d", "e"]

    def test_exactly_n_returns_all(self) -> None:
        assert _trim_to_n(["x", "y", "z"], 3) == ["x", "y", "z"]

    def test_empty_list(self) -> None:
        assert _trim_to_n([], 10) == []


# ---------------------------------------------------------------------------
# _is_tmux_available
# ---------------------------------------------------------------------------


class TestIsTmuxAvailable:
    def test_returns_true_when_tmux_on_path(self) -> None:
        with patch("thegent.tools.terminal_capture.shutil.which", return_value="/usr/bin/tmux"):
            assert _is_tmux_available() is True

    def test_returns_false_when_tmux_absent(self) -> None:
        with patch("thegent.tools.terminal_capture.shutil.which", return_value=None):
            assert _is_tmux_available() is False


# ---------------------------------------------------------------------------
# _capture_via_tmux
# ---------------------------------------------------------------------------


class TestCaptureViaTmux:
    def test_returns_none_when_tmux_unavailable(self) -> None:
        with patch("thegent.tools.terminal_capture.shutil.which", return_value=None):
            assert _capture_via_tmux("%0", 50) is None

    def test_returns_result_on_success(self) -> None:
        fake = MagicMock()
        fake.returncode = 0
        fake.stdout = "line1\nline2\nline3\n"
        fake.stderr = ""
        with (
            patch("thegent.tools.terminal_capture.shutil.which", return_value="/usr/bin/tmux"),
            patch("thegent.tools.terminal_capture.subprocess.run", return_value=fake),
        ):
            result = _capture_via_tmux("%0", 50)
        assert result is not None
        assert result.backend == "tmux"
        assert result.pane_id == "%0"
        assert "line1" in result.lines

    def test_returns_none_on_nonzero_exit(self) -> None:
        fake = MagicMock()
        fake.returncode = 1
        fake.stdout = ""
        fake.stderr = "no server running"
        with (
            patch("thegent.tools.terminal_capture.shutil.which", return_value="/usr/bin/tmux"),
            patch("thegent.tools.terminal_capture.subprocess.run", return_value=fake),
        ):
            result = _capture_via_tmux("%0", 50)
        assert result is None

    def test_trims_to_n_lines(self) -> None:
        lines = "\n".join(f"L{i}" for i in range(100))
        fake = MagicMock()
        fake.returncode = 0
        fake.stdout = lines
        fake.stderr = ""
        with (
            patch("thegent.tools.terminal_capture.shutil.which", return_value="/usr/bin/tmux"),
            patch("thegent.tools.terminal_capture.subprocess.run", return_value=fake),
        ):
            result = _capture_via_tmux("%0", 10)
        assert result is not None
        assert len(result.lines) == 10

    def test_returns_none_on_os_error(self) -> None:
        with (
            patch("thegent.tools.terminal_capture.shutil.which", return_value="/usr/bin/tmux"),
            patch("thegent.tools.terminal_capture.subprocess.run", side_effect=OSError("no tmux")),
        ):
            result = _capture_via_tmux("%0", 50)
        assert result is None


# ---------------------------------------------------------------------------
# _capture_via_zmx
# ---------------------------------------------------------------------------


class TestCaptureViaZmx:
    def test_returns_none_when_import_fails(self) -> None:
        with patch.dict(sys.modules, {"thegent.session.zmx_backend": None}):
            result = _capture_via_zmx("mysession", 50)
        assert result is None

    def test_returns_none_when_zmx_not_available(self) -> None:
        mock_backend = MagicMock()
        mock_backend.available = False
        mock_cls = MagicMock(return_value=mock_backend)
        mock_module = MagicMock()
        mock_module.ZmxBackend = mock_cls
        with patch.dict(sys.modules, {"thegent.session.zmx_backend": mock_module}):
            result = _capture_via_zmx("mysession", 50)
        assert result is None

    def test_returns_result_on_success(self) -> None:
        mock_backend = MagicMock()
        mock_backend.available = True
        mock_backend.capture.return_value = "alpha\nbeta\ngamma\n"
        mock_cls = MagicMock(return_value=mock_backend)
        mock_module = MagicMock()
        mock_module.ZmxBackend = mock_cls
        with patch.dict(sys.modules, {"thegent.session.zmx_backend": mock_module}):
            result = _capture_via_zmx("mysession", 50)
        assert result is not None
        assert result.backend == "zmx"
        assert result.pane_id == "mysession"
        assert "alpha" in result.lines

    def test_returns_none_when_capture_empty(self) -> None:
        mock_backend = MagicMock()
        mock_backend.available = True
        mock_backend.capture.return_value = ""
        mock_cls = MagicMock(return_value=mock_backend)
        mock_module = MagicMock()
        mock_module.ZmxBackend = mock_cls
        with patch.dict(sys.modules, {"thegent.session.zmx_backend": mock_module}):
            result = _capture_via_zmx("mysession", 50)
        assert result is None


# ---------------------------------------------------------------------------
# _capture_via_proc
# ---------------------------------------------------------------------------


class TestCaptureViaProc:
    def test_returns_none_on_non_linux(self) -> None:
        with patch("thegent.tools.terminal_capture.platform.system", return_value="Darwin"):
            result = _capture_via_proc(12345, 50)
        assert result is None

    def test_returns_result_on_linux_readable_fd(self) -> None:
        content = b"line1\nline2\nline3\n"
        mock_open = MagicMock()
        mock_fh = MagicMock()
        mock_fh.__enter__ = MagicMock(return_value=mock_fh)
        mock_fh.__exit__ = MagicMock(return_value=False)
        mock_fh.read.return_value = content
        mock_open.return_value = mock_fh
        with (
            patch("thegent.tools.terminal_capture.platform.system", return_value="Linux"),
            patch("builtins.open", mock_open),
        ):
            result = _capture_via_proc(42, 50)
        assert result is not None
        assert result.backend == "proc"
        assert result.pane_id == "42"
        assert "line1" in result.lines

    def test_returns_none_on_permission_error(self) -> None:
        with (
            patch("thegent.tools.terminal_capture.platform.system", return_value="Linux"),
            patch("builtins.open", side_effect=OSError("Permission denied")),
        ):
            result = _capture_via_proc(99, 50)
        assert result is None


# ---------------------------------------------------------------------------
# _capture_via_termitty
# ---------------------------------------------------------------------------


class TestCaptureViaTermitty:
    def test_returns_none_when_termitty_not_installed(self) -> None:
        with patch.dict(sys.modules, {"termitty": None}):
            result = _capture_via_termitty(b"hello\n", 50)
        assert result is None

    def test_returns_result_when_termitty_available(self) -> None:
        result = _capture_via_termitty(b"hello\nworld\n", 50)
        assert result is not None
        assert result.backend == "termitty"
        assert result.pane_id is None
        assert any("hello" in line for line in result.lines)

    def test_strips_trailing_blank_lines(self) -> None:
        result = _capture_via_termitty(b"text\n", 50)
        assert result is not None
        if result.lines:
            assert result.lines[-1].strip() != ""

    def test_trims_to_n_lines(self) -> None:
        big_input = b"\n".join(f"line{i}".encode() for i in range(200)) + b"\n"
        result = _capture_via_termitty(big_input, 10)
        assert result is not None
        assert len(result.lines) <= 10

    def test_ansi_escape_codes_processed(self) -> None:
        ansi_input = b"\x1b[32mgreen\x1b[0m text\n"
        result = _capture_via_termitty(ansi_input, 50)
        assert result is not None
        assert result.backend == "termitty"


# ---------------------------------------------------------------------------
# TerminalCapture.capture_last_n_lines
# ---------------------------------------------------------------------------


class TestTerminalCaptureLastNLines:
    def test_returns_none_backend_when_all_fail(self) -> None:
        tc = TerminalCapture()
        with (
            patch("thegent.tools.terminal_capture.shutil.which", return_value=None),
            patch.object(tc, "_read_current_tty_bytes", return_value=b""),
        ):
            result = tc.capture_last_n_lines(n=50)
        assert result.backend == "none"
        assert result.lines == []

    def test_uses_tmux_when_pane_id_given_and_available(self) -> None:
        fake = MagicMock()
        fake.returncode = 0
        fake.stdout = "a\nb\nc\n"
        fake.stderr = ""
        with (
            patch("thegent.tools.terminal_capture.shutil.which", return_value="/usr/bin/tmux"),
            patch("thegent.tools.terminal_capture.subprocess.run", return_value=fake),
        ):
            result = TerminalCapture().capture_last_n_lines(n=50, pane_id="%0")
        assert result.backend == "tmux"

    def test_falls_through_to_termitty_when_pane_unavailable(self) -> None:
        tc = TerminalCapture()
        with (
            patch("thegent.tools.terminal_capture.shutil.which", return_value=None),
            patch.object(tc, "_read_current_tty_bytes", return_value=b"tty line\n"),
        ):
            result = tc.capture_last_n_lines(n=50)
        assert result.backend in {"termitty", "none"}

    def test_no_pane_id_skips_tmux_and_zmx(self) -> None:
        call_log: list[str] = []

        def fake_tmux(pane_id: str, n: int) -> Any:
            call_log.append("tmux")
            return None

        def fake_zmx(session: str, n: int) -> Any:
            call_log.append("zmx")
            return None

        tc = TerminalCapture()
        with (
            patch("thegent.tools.terminal_capture._capture_via_tmux", side_effect=fake_tmux),
            patch("thegent.tools.terminal_capture._capture_via_zmx", side_effect=fake_zmx),
            patch.object(tc, "_read_current_tty_bytes", return_value=b""),
        ):
            tc.capture_last_n_lines(n=50, pane_id=None)
        assert "tmux" not in call_log
        assert "zmx" not in call_log

    def test_default_n_is_50(self) -> None:
        tc = TerminalCapture()
        captured_n: list[int] = []

        def fake_tmux(pane_id: str, n: int) -> CaptureResult:
            captured_n.append(n)
            return CaptureResult(lines=[], backend="tmux", pane_id=pane_id)

        with (
            patch("thegent.tools.terminal_capture.shutil.which", return_value="/usr/bin/tmux"),
            patch("thegent.tools.terminal_capture._capture_via_tmux", side_effect=fake_tmux),
        ):
            tc.capture_last_n_lines(pane_id="%0")
        assert captured_n == [50]


# ---------------------------------------------------------------------------
# TerminalCapture.capture_by_pid
# ---------------------------------------------------------------------------


class TestTerminalCaptureByPid:
    def test_returns_none_backend_when_all_fail(self) -> None:
        tc = TerminalCapture()
        with (
            patch("thegent.tools.terminal_capture.platform.system", return_value="Darwin"),
            patch.object(tc, "_read_proc_bytes", return_value=b""),
        ):
            result = tc.capture_by_pid(pid=99999, n=50)
        assert result.backend == "none"
        assert result.pane_id == "99999"

    def test_uses_proc_on_linux(self) -> None:
        content = b"output line\n"
        mock_fh = MagicMock()
        mock_fh.__enter__ = MagicMock(return_value=mock_fh)
        mock_fh.__exit__ = MagicMock(return_value=False)
        mock_fh.read.return_value = content
        with (
            patch("thegent.tools.terminal_capture.platform.system", return_value="Linux"),
            patch("builtins.open", MagicMock(return_value=mock_fh)),
        ):
            result = TerminalCapture().capture_by_pid(pid=1, n=50)
        assert result.backend == "proc"
        assert result.pane_id == "1"

    def test_pane_id_set_to_str_pid(self) -> None:
        tc = TerminalCapture()
        with (
            patch("thegent.tools.terminal_capture.platform.system", return_value="Darwin"),
            patch.object(tc, "_read_proc_bytes", return_value=b""),
        ):
            result = tc.capture_by_pid(pid=12345)
        assert result.pane_id == "12345"

    def test_falls_through_to_termitty_when_proc_unavailable(self) -> None:
        tc = TerminalCapture()
        with (
            patch("thegent.tools.terminal_capture.platform.system", return_value="Darwin"),
            patch.object(tc, "_read_proc_bytes", return_value=b"termitty line\n"),
        ):
            result = tc.capture_by_pid(pid=1, n=50)
        assert result.backend in {"termitty", "none"}
        if result.backend == "termitty":
            assert result.pane_id == "1"


# ---------------------------------------------------------------------------
# _read_current_tty_bytes / _read_proc_bytes helpers
# ---------------------------------------------------------------------------


class TestInternalHelpers:
    def test_read_current_tty_bytes_returns_bytes_on_success(self) -> None:
        mock_fh = MagicMock()
        mock_fh.__enter__ = MagicMock(return_value=mock_fh)
        mock_fh.__exit__ = MagicMock(return_value=False)
        mock_fh.read.return_value = b"tty data"
        with (
            patch("thegent.tools.terminal_capture.os.ttyname", return_value="/dev/pts/0"),
            patch("builtins.open", MagicMock(return_value=mock_fh)),
        ):
            result = TerminalCapture._read_current_tty_bytes()
        assert result == b"tty data"

    def test_read_current_tty_bytes_returns_empty_on_error(self) -> None:
        with patch("thegent.tools.terminal_capture.os.ttyname", side_effect=OSError("not a tty")):
            result = TerminalCapture._read_current_tty_bytes()
        assert result == b""

    def test_read_proc_bytes_returns_empty_on_non_linux(self) -> None:
        with patch("thegent.tools.terminal_capture.platform.system", return_value="Windows"):
            assert TerminalCapture._read_proc_bytes(1) == b""

    def test_read_proc_bytes_returns_bytes_on_linux(self) -> None:
        mock_fh = MagicMock()
        mock_fh.__enter__ = MagicMock(return_value=mock_fh)
        mock_fh.__exit__ = MagicMock(return_value=False)
        mock_fh.read.return_value = b"proc data"
        with (
            patch("thegent.tools.terminal_capture.platform.system", return_value="Linux"),
            patch("builtins.open", MagicMock(return_value=mock_fh)),
        ):
            result = TerminalCapture._read_proc_bytes(42)
        assert result == b"proc data"

    def test_read_proc_bytes_returns_empty_on_os_error(self) -> None:
        with (
            patch("thegent.tools.terminal_capture.platform.system", return_value="Linux"),
            patch("builtins.open", side_effect=OSError("no fd")),
        ):
            result = TerminalCapture._read_proc_bytes(99)
        assert result == b""


# ---------------------------------------------------------------------------
# Export surface tests
# ---------------------------------------------------------------------------


class TestExports:
    def test_can_import_from_tools_package(self) -> None:
        import thegent.tools as pkg

        assert pkg.CaptureResult is CaptureResult
        assert pkg.TerminalCapture is TerminalCapture

    def test_capture_result_in_all(self) -> None:
        import thegent.tools as pkg

        assert "CaptureResult" in pkg.__all__
        assert "TerminalCapture" in pkg.__all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
