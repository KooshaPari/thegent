"""Tests for `thegent domain map` advisor command."""

from __future__ import annotations

import orjson as json

from typer.testing import CliRunner

from thegent.cli.apps.main import app

runner = CliRunner()


def test_domain_map_help() -> None:
    result = runner.invoke(app, ["domain", "map", "--help"])
    assert result.exit_code == 0


def test_domain_map_advisor_json_payload() -> None:
    result = runner.invoke(
        app,
        [
            "domain",
            "map",
            "app.example.com",
            "--target",
            "http://localhost:3847",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["mode"] == "advisor"
    assert payload["domain"] == "app.example.com"
    assert payload["target"] == "http://localhost:3847"
    assert payload["tunnel_name"] == "thegent"
    assert payload["steps"]


def test_domain_map_invalid_domain_fails() -> None:
    result = runner.invoke(app, ["domain", "map", "localhost", "--target", "http://localhost:3847"])
    assert result.exit_code == 2
    assert "domain must include at least one dot" in result.output


def test_domain_map_apply_mode_not_implemented() -> None:
    result = runner.invoke(
        app,
        ["domain", "map", "example.com", "--target", "http://localhost:3847", "--mode", "apply"],
    )
    assert result.exit_code == 2
    assert "Apply mode is intentionally not enabled yet" in result.output


def test_domain_map_legacy_shim_command() -> None:
    result = runner.invoke(
        app,
        ["domain-map", "app.example.com", "--target", "http://localhost:3847", "--format", "json"],
    )
    assert result.exit_code == 0
