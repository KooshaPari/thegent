"""Unit tests for filtering benign macOS malloc stderr noise."""

from __future__ import annotations

from thegent.agents.codex_proxy import _is_ignorable_stderr_line
from thegent.agents.cursor_api_runner import _sanitize_stderr


def test_codex_proxy_ignores_malloc_noise_line() -> None:
    line = "codex(24650) MallocStackLogging: can't turn off malloc stack logging because it was not enabled."
    assert _is_ignorable_stderr_line(line) is True


def test_cursor_api_runner_sanitizes_only_malloc_noise() -> None:
    stderr = (
        "first error\n"
        "MallocStackLogging: can't turn off malloc stack logging because it was not enabled.\n"
        "second error\n"
    )
    assert _sanitize_stderr(stderr) == "first error\nsecond error\n"
