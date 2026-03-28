"""Agent browser stream: launch, doctor, and journey management."""

from __future__ import annotations

import typer

app = typer.Typer(help="Agent browser operations (launch, auth journeys, task journeys).")
journey_app = typer.Typer(help="Programmatic browser journey registry and launch.")
app.add_typer(journey_app, name="journey")


@app.command("install", help="Install/update universal agent-browser launcher and app symlink.")
def browser_install(
    force: bool = typer.Option(False, "--force", help="Overwrite existing launcher."),
) -> None:
    from thegent_cli.cli.commands.browser import browser_install_cmd

    browser_install_cmd(force=force)


@app.command("doctor", help="Verify Agent Browser prerequisites and expected paths.")
def browser_doctor() -> None:
    from thegent_cli.cli.commands.browser import browser_doctor_cmd

    browser_doctor_cmd()


@app.command("launch", help="Launch the agent browser in visible or headless mode.")
def browser_launch(
    browser: str = typer.Option("auto", "--browser", help="Browser: auto|edge|chrome"),
    headless: bool = typer.Option(False, "--headless", help="Run headless."),
    cdp_port: int = typer.Option(9222, "--cdp-port", help="Chrome DevTools Protocol port."),
    url: str | None = typer.Option(None, "--url", help="Optional URL to open immediately."),
) -> None:
    from thegent_cli.cli.commands.browser import browser_launch_cmd

    browser_launch_cmd(browser=browser, headless=headless, cdp_port=cdp_port, url=url)


@journey_app.command("add", help="Register or update a named auth/task journey.")
def journey_add(
    name: str = typer.Argument(..., help="Stable journey name."),
    url: str = typer.Option(..., "--url", help="Starting URL."),
    kind: str = typer.Option("auth", "--kind", help="Journey type: auth|task"),
    notes: str | None = typer.Option(None, "--notes", help="Optional notes."),
) -> None:
    from thegent_cli.cli.commands.browser import browser_journey_add_cmd

    browser_journey_add_cmd(name=name, url=url, kind=kind, notes=notes)


@journey_app.command("list", help="List all registered journeys.")
def journey_list() -> None:
    from thegent_cli.cli.commands.browser import browser_journey_list_cmd

    browser_journey_list_cmd()


@journey_app.command("open", help="Open a named journey in agent browser.")
def journey_open(
    name: str = typer.Argument(..., help="Journey name."),
    browser: str = typer.Option("auto", "--browser", help="Browser: auto|edge|chrome"),
    headless: bool = typer.Option(False, "--headless", help="Run headless."),
    cdp_port: int = typer.Option(9222, "--cdp-port", help="Chrome DevTools Protocol port."),
) -> None:
    from thegent_cli.cli.commands.browser import browser_journey_open_cmd

    browser_journey_open_cmd(name=name, browser=browser, headless=headless, cdp_port=cdp_port)
