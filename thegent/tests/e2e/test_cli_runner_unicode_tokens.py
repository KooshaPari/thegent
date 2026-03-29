from __future__ import annotations

import typer

from tests.e2e.cli_runner_compat import (
    _alias_rewrite_argv,
    _build_command_surface_drift_skip_message,
    _result_mentions_no_such_command,
)


def test_build_skip_message_preserves_unicode_tokens() -> None:
    argv = ["recover", "rollback", "cafe-123"]
    message = _build_command_surface_drift_skip_message(None, argv)

    assert message.endswith("recover rollback cafe-123")


def test_result_mentions_no_such_command_with_unicode_noise() -> None:
    class Result:
        stdout = "noise-prefix No such command: logs"
        stderr = ""

    assert _result_mentions_no_such_command(Result())


def test_alias_rewrite_returns_none_for_empty_argv() -> None:
    app = typer.Typer()
    assert _alias_rewrite_argv(app, []) is None


def test_alias_rewrite_does_not_rewrite_unicode_argumentful_alias() -> None:
    app = typer.Typer()
    run_app = typer.Typer()

    @run_app.command("logs")
    def run_logs() -> None:
        return None

    app.add_typer(run_app, name="run")

    assert _alias_rewrite_argv(app, ["logs", "cafe-123"]) is None
