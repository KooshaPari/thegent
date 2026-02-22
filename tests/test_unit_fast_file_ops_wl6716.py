from __future__ import annotations

import errno
from pathlib import Path

import pytest

from thegent.infra import fast_file_ops


def test_sendfile_failure_falls_back_and_emits_telemetry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    src = tmp_path / "src.bin"
    dst = tmp_path / "dst.bin"
    payload = b"abc123"
    src.write_bytes(payload)

    monkeypatch.setattr(fast_file_ops.sys, "platform", "linux")
    monkeypatch.setattr(fast_file_ops, "SEND_FILE_THRESHOLD_BYTES", 1)

    def _raise_sendfile(*_args: object, **_kwargs: object) -> int:
        raise OSError(errno.EPERM, "blocked")

    monkeypatch.setattr(fast_file_ops.os, "sendfile", _raise_sendfile)

    fast_file_ops.reset_sendfile_fallback_counts()
    caplog.set_level("WARNING", logger="thegent.infra.fast_file_ops")

    fast_file_ops.FastFileOps.copy(src, dst, preserve_metadata=False)

    assert dst.read_bytes() == payload
    assert fast_file_ops.get_sendfile_fallback_counts().get("permission") == 1
    assert any("sendfile fallback engaged" in rec.message for rec in caplog.records)
