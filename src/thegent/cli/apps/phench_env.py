"""Phench environment-management commands."""

from __future__ import annotations

import typer
from rich.console import Console

import orjson as json

console = Console()


def register_env_commands(
    env_app: typer.Typer,
    run_env_doctor_for_target_fn,
    set_env_profile_fn,
    get_env_profile_fn,
) -> None:
    """Register environment-related commands on the phench env sub-app."""

    @env_app.command("doctor", help="Run fail-fast environment doctor for a materialized target.")
    def env_doctor_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
    ) -> None:
        report = run_env_doctor_for_target_fn(name, family=family)
        console.print_json(json.dumps(report).decode())
        if report["doctor_status"] != "pass":
            raise typer.Exit(2)

    @env_app.command("profile-set", help="Set or replace a named env profile for target run commands.")
    def env_profile_set_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        profile: str = typer.Option(..., "--profile", help="Profile name."),
        vars: list[str] = typer.Option([], "--var", help="KEY=VALUE pairs; may be repeated."),
    ) -> None:
        values: dict[str, str] = {}
        for pair in vars:
            if "=" not in pair:
                raise typer.BadParameter("Each --var must be KEY=VALUE")
            key, value = pair.split("=", 1)
            if not key:
                raise typer.BadParameter("Environment variable key cannot be empty")
            values[key] = value
        state = set_env_profile_fn(name, profile, values, family=family)
        console.print_json(json.dumps(state).decode())

    @env_app.command("profile-show", help="Show active or named env profile for target run commands.")
    def env_profile_show_cmd(
        name: str = typer.Argument(..., help="Target name."),
        family: str | None = typer.Option(None, "--family", help="Optional target family namespace."),
        profile: str | None = typer.Option(None, "--profile", help="Optional profile name."),
    ) -> None:
        payload = {
            "target": name,
            "profile": profile or "active",
            "env": get_env_profile_fn(name, profile=profile, family=family),
        }
        console.print_json(json.dumps(payload).decode())
