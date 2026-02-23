"""Unit tests for the modular CLI app entrypoints."""

import json
from pathlib import Path
from unittest.mock import ANY, patch

from typer.testing import CliRunner

from thegent.cli.apps.main import app

runner = CliRunner()


def test_top_level_ps_shortcut_routes_to_run_ps() -> None:
    """`thegent ps` should route through the run stream implementation."""
    with patch("thegent.cli.apps.run.run_ps") as mock_run_ps:
        result = runner.invoke(
            app,
            ["ps", "--all", "--owner", "alice", "--format", "json", "--include-contract"],
        )

    assert result.exit_code == 0
    mock_run_ps.assert_called_once_with(
        all_sessions=True,
        owner="alice",
        format="json",
        include_contract=True,
    )


def test_top_level_do_shortcut_routes_to_run_agent() -> None:
    """`thegent do` should route through the run stream implementation."""
    with patch("thegent.cli.apps.run.run_agent") as mock_run_agent:
        result = runner.invoke(app, ["do", "hello"])

    assert result.exit_code == 0
    mock_run_agent.assert_called_once_with(prompt="hello")


def test_install_compat_routes_to_run_install() -> None:
    """`thegent install` should remain available in the new app tree."""
    with patch("thegent.install.run_install") as mock_run_install:
        mock_run_install.return_value = {}
        result = runner.invoke(
            app,
            ["install", "--target", "codex", "--mode", "smart", "--dry-run", "--verbose"],
        )

    assert result.exit_code == 0
    mock_run_install.assert_called_once_with(
        target="codex",
        mode="smart",
        dry_run=True,
        verbose=True,
        url=None,
        install_service=False,
    )


def test_install_invocation_can_run_system_install_with_setup() -> None:
    """`thegent install --system` should route to system-wide installer and optional setup."""
    with (
        patch("thegent.install.run_install_system") as mock_run_install_system,
        patch("thegent.cli.commands.model_cmds.setup_cmd") as mock_setup_cmd,
    ):
        mock_run_install_system.return_value = {"errors": 0}
        result = runner.invoke(app, ["install", "--system", "--setup"])

    assert result.exit_code == 0
    mock_run_install_system.assert_called_once_with(
        prefix=Path("/opt/thegent"),
        dry_run=False,
        verbose=False,
    )
    mock_setup_cmd.assert_called_once_with(wizard=True)


def test_install_invocation_can_run_both_scope() -> None:
    """`thegent install --scope both` should run user and system installers."""
    with (
        patch("thegent.install.run_install") as mock_run_install,
        patch("thegent.install.run_install_system") as mock_run_install_system,
    ):
        mock_run_install.return_value = {"errors": 0}
        mock_run_install_system.return_value = {"errors": 0}
        result = runner.invoke(
            app,
            [
                "install",
                "--scope",
                "both",
                "--system-prefix",
                "/tmp/thegent",
                "--dry-run",
            ],
        )

    assert result.exit_code == 0
    mock_run_install.assert_called_once_with(
        target="all",
        mode="smart",
        dry_run=True,
        verbose=False,
        url=None,
        install_service=False,
    )
    mock_run_install_system.assert_called_once_with(
        prefix=Path("/tmp/thegent"),
        dry_run=True,
        verbose=False,
    )


def test_install_invalid_scope_fails() -> None:
    """`thegent install --scope invalid` should fail and call no installer."""
    with (
        patch("thegent.install.run_install") as mock_run_install,
        patch("thegent.install.run_install_system") as mock_run_install_system,
    ):
        result = runner.invoke(app, ["install", "--scope", "broken"])

    assert result.exit_code != 0
    mock_run_install.assert_not_called()
    mock_run_install_system.assert_not_called()


def test_install_scope_system_runs_system_only_with_custom_prefix() -> None:
    """`thegent install --scope system` should run only the system installer path."""
    with (
        patch("thegent.install.run_install") as mock_run_install,
        patch("thegent.install.run_install_system") as mock_run_install_system,
    ):
        mock_run_install_system.return_value = {"errors": 0}
        result = runner.invoke(
            app,
            [
                "install",
                "--scope",
                "system",
                "--system-prefix",
                "/usr/local/thegent",
            ],
        )

    assert result.exit_code == 0
    mock_run_install.assert_not_called()
    mock_run_install_system.assert_called_once_with(
        prefix=Path("/usr/local/thegent"),
        dry_run=False,
        verbose=False,
    )


def test_install_alias_user_target_routes_to_all() -> None:
    """`thegent install --target user` should normalize to user install (`all`)."""
    with patch("thegent.install.run_install") as mock_run_install:
        mock_run_install.return_value = {}
        result = runner.invoke(app, ["install", "--target", "user"])

    assert result.exit_code == 0
    mock_run_install.assert_called_once_with(
        target="all",
        mode="smart",
        dry_run=False,
        verbose=False,
        url=None,
        install_service=False,
    )


def test_install_with_invalid_target_fails_without_calling_install() -> None:
    """`thegent install --target bad` should fail and skip run_install."""
    with patch("thegent.install.run_install") as mock_run_install:
        result = runner.invoke(app, ["install", "--target", "bad-target"])

    assert result.exit_code == 1
    mock_run_install.assert_not_called()


def test_install_project_subcommand_still_routes_to_project_installer() -> None:
    """`thegent install project` should still resolve the project-install command."""
    with (
        patch("thegent.install.run_install") as mock_run_install,
        patch("thegent.install.run_install_system") as mock_run_install_system,
        patch("thegent.install.run_install_project") as mock_run_install_project,
    ):
        mock_run_install_project.return_value = {
            "project_name": "foo",
            "path": "/tmp/foo",
            "template": "none",
            "installed": [],
            "skipped": [],
            "errors": [],
        }
        result = runner.invoke(
            app,
            ["install", "project", "--project", "foo", "--json"],
        )

    assert result.exit_code == 0
    mock_run_install.assert_not_called()
    mock_run_install_system.assert_not_called()
    mock_run_install_project.assert_called_once_with(
        project_selector="foo",
        template="none",
        mode="smart",
        dry_run=False,
        registry_path=ANY,
    )


def test_project_top_level_command_is_available_and_routes_to_setup_project() -> None:
    """`thegent project` should resolve through setup project command registry."""
    result = runner.invoke(app, ["project", "list", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert isinstance(payload, list)


def test_install_project_brownfield_routes_to_setup_project_migrate() -> None:
    """`thegent install project brownfield` should delegate to migrate workflow."""
    with patch("thegent.cli.apps.project.project_migrate") as mock_project_migrate:
        result = runner.invoke(
            app,
            [
                "install",
                "project",
                "brownfield",
                "/tmp/existing",
                "--template",
                "auto",
                "--mode",
                "overwrite",
                "--name",
                "existing-app",
                "--tenant",
                "tenant-x",
                "--json",
            ],
        )

    assert result.exit_code == 0
    mock_project_migrate.assert_called_once_with(
        project="/tmp/existing",
        name="existing-app",
        tenant="tenant-x",
        template="auto",
        mode="overwrite",
        reconcile=True,
        register=True,
        install_runtime=True,
        dry_run=False,
        json_output=True,
    )


def test_scaffold_greenfield_routes_to_sys_setup_project_scaffold() -> None:
    """`thegent scaffold greenfield` should delegate to the setup-project scaffold command."""
    with patch("thegent.cli.apps.project.project_scaffold") as mock_project_scaffold:
        result = runner.invoke(app, ["scaffold", "greenfield", "/tmp/gf", "--profile", "cli_tool", "--name", "name"])

    assert result.exit_code == 0
    mock_project_scaffold.assert_called_once_with(
        destination="/tmp/gf",
        profile="cli_tool",
        name="name",
        description="",
        include_act=True,
        include_qa_tools=True,
        include_pm_tools=True,
        language="python",
        register=False,
        install_runtime=False,
        tenant="",
        dry_run=False,
        json_output=False,
    )


def test_scaffold_brownfield_routes_to_sys_setup_project_migrate() -> None:
    """`thegent scaffold brownfield` should delegate to the setup-project migrate command."""
    with patch("thegent.cli.apps.project.project_migrate") as mock_project_migrate:
        result = runner.invoke(app, ["scaffold", "brownfield", "/tmp/proj", "--template", "ag-dd", "--mode", "skip"])

    assert result.exit_code == 0
    mock_project_migrate.assert_called_once_with(
        project="/tmp/proj",
        name="",
        tenant="",
        template="ag-dd",
        mode="skip",
        reconcile=True,
        register=True,
        install_runtime=True,
        dry_run=False,
        json_output=False,
    )


def test_scaffold_agdd_alias_routes_to_project_migrate() -> None:
    """`thegent scaffold ag-dd` should fix template to ag-dd."""
    with patch("thegent.cli.apps.project.project_migrate") as mock_project_migrate:
        result = runner.invoke(
            app,
            [
                "scaffold",
                "ag-dd",
                "/tmp/proj",
                "--mode",
                "overwrite",
                "--tenant",
                "tenant-x",
            ],
        )

    assert result.exit_code == 0
    mock_project_migrate.assert_called_once_with(
        project="/tmp/proj",
        name="",
        tenant="tenant-x",
        template="ag-dd",
        mode="overwrite",
        reconcile=True,
        register=True,
        install_runtime=True,
        dry_run=False,
        json_output=False,
    )


def test_scaffold_none_alias_routes_to_project_migrate() -> None:
    """`thegent scaffold none` should fix template to none."""
    with patch("thegent.cli.apps.project.project_migrate") as mock_project_migrate:
        result = runner.invoke(
            app,
            [
                "scaffold",
                "none",
                "/tmp/proj",
                "--mode",
                "skip",
                "--tenant",
                "tenant-y",
            ],
        )

    assert result.exit_code == 0
    mock_project_migrate.assert_called_once_with(
        project="/tmp/proj",
        name="",
        tenant="tenant-y",
        template="none",
        mode="skip",
        reconcile=True,
        register=True,
        install_runtime=True,
        dry_run=False,
        json_output=False,
    )


def test_setup_project_agdd_alias_routes_to_brownfield() -> None:
    """`thegent project ag-dd` should fix template to AG-DD."""
    with patch("thegent.cli.apps.project.setup_project_brownfield") as mock_setup_project_brownfield:
        result = runner.invoke(
            app,
            [
                "project",
                "ag-dd",
                "/tmp/proj",
                "--mode",
                "smart",
                "--tenant",
                "tenant-x",
            ],
        )

    assert result.exit_code == 0
    mock_setup_project_brownfield.assert_called_once_with(
        project="/tmp/proj",
        name="",
        tenant="tenant-x",
        template="ag-dd",
        mode="smart",
        reconcile=True,
        register=True,
        install_runtime=True,
        dry_run=False,
        json_output=False,
    )


def test_setup_project_none_alias_routes_to_brownfield() -> None:
    """`thegent project none` should fix template to none."""
    with patch("thegent.cli.apps.project.setup_project_brownfield") as mock_setup_project_brownfield:
        result = runner.invoke(
            app,
            [
                "project",
                "none",
                "/tmp/proj",
                "--mode",
                "skip",
                "--tenant",
                "tenant-y",
            ],
        )

    assert result.exit_code == 0
    mock_setup_project_brownfield.assert_called_once_with(
        project="/tmp/proj",
        name="",
        tenant="tenant-y",
        template="none",
        mode="skip",
        reconcile=True,
        register=True,
        install_runtime=True,
        dry_run=False,
        json_output=False,
    )


def test_install_project_agdd_alias_routes_to_project_migrate() -> None:
    """`thegent install project ag-dd` should force AG-DD and route to migrate."""
    with patch("thegent.cli.apps.project.project_migrate") as mock_project_migrate:
        result = runner.invoke(
            app,
            [
                "install",
                "project",
                "ag-dd",
                "/tmp/existing",
                "--mode",
                "overwrite",
                "--tenant",
                "tenant-x",
                "--json",
            ],
        )

    assert result.exit_code == 0
    mock_project_migrate.assert_called_once_with(
        project="/tmp/existing",
        name="",
        tenant="tenant-x",
        template="ag-dd",
        mode="overwrite",
        reconcile=True,
        register=True,
        install_runtime=True,
        dry_run=False,
        json_output=True,
    )


def test_install_project_none_alias_routes_to_project_migrate() -> None:
    """`thegent install project none` should force no template and route to migrate."""
    with patch("thegent.cli.apps.project.project_migrate") as mock_project_migrate:
        result = runner.invoke(
            app,
            [
                "install",
                "project",
                "none",
                "/tmp/existing",
                "--name",
                "existing-app",
                "--tenant",
                "tenant-z",
                "--json",
            ],
        )

    assert result.exit_code == 0
    mock_project_migrate.assert_called_once_with(
        project="/tmp/existing",
        name="existing-app",
        tenant="tenant-z",
        template="none",
        mode="smart",
        reconcile=True,
        register=True,
        install_runtime=True,
        dry_run=False,
        json_output=True,
    )


def test_global_setup_command_delegates_to_setup_cmd() -> None:
    """`thegent setup` should run the legacy setup command implementation."""
    with patch("thegent.cli.apps.main.model_cmds.setup_cmd") as mock_setup_cmd:
        result = runner.invoke(
            app,
            ["setup", "--no-wizard", "--full", "--hooks", "--skills", "--harness"],
        )

    assert result.exit_code == 0
    mock_setup_cmd.assert_called_once()
    kwargs = mock_setup_cmd.call_args.kwargs
    assert kwargs["wizard"] is False
    assert kwargs["full"] is True
    assert kwargs["hooks"] is True
    assert kwargs["skills"] is True
    assert kwargs["harness"] is True


def test_global_git_command_group_is_registered() -> None:
    """`thegent git` must appear as a first-class command in help output."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "git" in result.stdout


def test_global_git_help_exits_zero() -> None:
    """`thegent git --help` should execute through the registered git typer app."""
    result = runner.invoke(app, ["git", "--help"])

    assert result.exit_code == 0
    assert "Usage: thegent git" in result.stdout
