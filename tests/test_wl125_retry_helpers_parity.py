from __future__ import annotations

from thegent.cli.commands import impl


def test_wl125_backoff_delay_wrapper_delegates_to_retry_helper(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _fake(*, attempt: int, max_delay: float = 60.0) -> float:
        captured["attempt"] = attempt
        captured["max_delay"] = max_delay
        return 1.25

    monkeypatch.setattr("thegent.cli.commands.impl.retry_helpers.backoff_delay", _fake)

    result = impl._backoff_delay(3, max_delay=12.0)

    assert result == 1.25
    assert captured == {"attempt": 3, "max_delay": 12.0}
