from __future__ import annotations

from thegent.cli.commands import cli


def test_queue_list_wrapper_delegates_to_extracted_module(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _fake(*, watch: bool = False) -> None:
        captured["watch"] = watch

    monkeypatch.setattr("thegent.cli.commands.queue_commands.queue_list_cmd", _fake)
    cli.queue_list_cmd(watch=True)

    assert captured["watch"] is True
