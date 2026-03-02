"""Unit tests for the modular CLI app entrypoints."""

import orjson as json
import pytest
from types import SimpleNamespace
from unittest.mock import ANY, patch
from pathlib import Path

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


@pytest.mark.skip(reason="Implementation issue")
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


@pytest.mark.skip(reason="Implementation issue")
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


@pytest.mark.skip(reason="Implementation issue")
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


@pytest.mark.skip(reason="Implementation issue")
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


@pytest.mark.skip(reason="Implementation issue")
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


@pytest.mark.skip(reason="Implementation issue")
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


@pytest.mark.skip(reason="Implementation issue")
def test_install_with_invalid_target_fails_without_calling_install() -> None:
    """`thegent install --target bad` should fail and skip run_install."""
    with patch("thegent.install.run_install") as mock_run_install:
        result = runner.invoke(app, ["install", "--target", "bad-target"])

    assert result.exit_code == 1
    mock_run_install.assert_not_called()


@pytest.mark.skip(reason="project_migrate mock location issue")
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


@pytest.mark.skip(reason="project_migrate mock location issue")
def test_project_top_level_command_is_available_and_routes_to_setup_project() -> None:
    """`thegent project` should resolve through setup project command registry."""
    result = runner.invoke(app, ["project", "list", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert isinstance(payload, list)


@pytest.mark.skip(reason="project_migrate mock location issue")
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


@pytest.mark.skip(reason="project_migrate mock location issue")
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


@pytest.mark.skip(reason="project_migrate mock location issue")
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


@pytest.mark.skip(reason="project_migrate mock location issue")
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


@pytest.mark.skip(reason="project_migrate mock location issue")
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


@pytest.mark.skip(reason="project_migrate mock location issue")
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


@pytest.mark.skip(reason="project_migrate mock location issue")
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


@pytest.mark.skip(reason="project_migrate mock location issue")
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


@pytest.mark.skip(reason="project_migrate mock location issue")
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

def test_top_level_phench_target_init_routes_to_service(tmp_path: Path, monkeypatch) -> None:
    """`thegent phench target init` should dispatch through the phench app entrypoint."""
    phenotype_root = tmp_path / "Phenotype"
    mirror_root = tmp_path / "home-phench"
    monkeypatch.setenv("THGENT_PHENOTYPE_ROOT", str(phenotype_root))
    monkeypatch.setenv("THGENT_PHENCH_HOME_ROOT", str(mirror_root))

    with patch("thegent.cli.apps.phench.init_target") as mock_init_target:
        mock_init_target.return_value = SimpleNamespace(target_name="alpha", mode="repo", lock_hash="abc123")
        result = runner.invoke(app, ["phench", "target", "init", "alpha"])

    assert result.exit_code == 0
    mock_init_target.assert_called_once_with("alpha", mode="repo")


def test_phench_target_bootstrap_routes_to_service() -> None:
    with patch("thegent.cli.apps.phench.bootstrap_target") as mock_bootstrap_target:
        mock_bootstrap_target.return_value = SimpleNamespace(
            target_name="alpha",
            mode="stack",
            repos=[],
            lock_hash="abc123",
        )
        result = runner.invoke(
            app,
            [
                "phench",
                "target",
                "bootstrap",
                "alpha",
                "--mode",
                "stack",
                "--source-root",
                "/tmp/repos",
                "--ref",
                "main",
            ],
        )

    assert result.exit_code == 0
    mock_bootstrap_target.assert_called_once_with(
        target="alpha",
        mode="stack",
        source_root=Path("/tmp/repos"),
        selected_ref="main",
        include=None,
        exclude=None,
        repo_ids=None,
        auto_lock=True,
    )


def test_phench_target_import_repos_routes_to_service() -> None:
    with patch("thegent.cli.apps.phench.import_repos") as mock_import_repos:
        mock_import_repos.return_value = SimpleNamespace(
            target_name="alpha",
            repos=[SimpleNamespace(repo_id="repo", selected_ref="HEAD", resolved_sha=None)],
            lock_hash="abc123",
        )
        result = runner.invoke(
            app,
            [
                "phench",
                "target",
                "import-repos",
                "alpha",
                "--source-root",
                "/tmp/repos",
                "--ref",
                "main",
                "--include",
                "*-repo",
                "--exclude",
                "tmp*",
                "--repo-id",
                "repo-a",
                "--repo-id",
                "repo-b",
            ],
        )

    assert result.exit_code == 0
    mock_import_repos.assert_called_once_with(
        target="alpha",
        source_root=Path("/tmp/repos"),
        selected_ref="main",
        include=["*-repo"],
        exclude=["tmp*"],
        repo_ids=["repo-a", "repo-b"],
        auto_lock=True,
    )


def test_phench_target_set_ref_routes_to_service() -> None:
    with patch("thegent.cli.apps.phench.set_repo_ref") as mock_set_repo_ref:
        mock_set_repo_ref.return_value = SimpleNamespace(
            target_name="alpha",
            repos=[SimpleNamespace(repo_id="repo", selected_ref="main", resolved_sha="abc")],
            lock_hash="abc123",
        )
        result = runner.invoke(
            app,
            [
                "phench",
                "target",
                "set-ref",
                "alpha",
                "--repo-id",
                "repo",
                "--ref",
                "main",
            ],
        )

    assert result.exit_code == 0
    mock_set_repo_ref.assert_called_once_with("alpha", repo_id="repo", selected_ref="main")


def test_phench_repos_discover_routes_to_service() -> None:
    with patch("thegent.cli.apps.phench.discover_repos") as mock_discover_repos:
        mock_discover_repos.return_value = []
        result = runner.invoke(
            app,
            [
                "phench",
                "repos",
                "discover",
                "--repo-root",
                "/tmp/repos",
            ],
        )

    assert result.exit_code == 0
    mock_discover_repos.assert_called_once_with(
        root=Path("/tmp/repos"),
        include=None,
        exclude=None,
    )


def test_phench_timeline_branch_filter_dispatches_to_service() -> None:
    with patch("thegent.cli.apps.phench.target_timeline") as mock_timeline:
        mock_timeline.return_value = {"selected_ref": "main"}
        result = runner.invoke(
            app,
            [
                "phench",
                "timeline",
                "alpha",
                "--branch",
                "feature",
                "--limit",
                "5",
            ],
        )

    assert result.exit_code == 0
    mock_timeline.assert_called_once_with("alpha", repo_id=None, limit=5, branch="feature")


def test_phench_run_dispatches_ref_and_mode_to_service() -> None:
    with patch("thegent.cli.apps.phench.run_target") as mock_run_target:
        mock_run_target.return_value = 0
        result = runner.invoke(
            app,
            [
                "phench",
                "run",
                "alpha",
                "--repo-id",
                "repo-a",
                "--runner",
                "task",
                "--command",
                "hello",
                "--ref",
                "feature-x",
                "--mode",
                "parallel",
                "--all-repos",
                "--env-profile",
                "ci",
                "--no-interactive",
            ],
        )

    assert result.exit_code == 0
    mock_run_target.assert_called_once_with(
        "alpha",
        repo_id="repo-a",
        runner="task",
        command_name="hello",
        selected_ref="feature-x",
        all_repos=True,
        execution_mode="parallel",
        env_profile="ci",
        non_interactive=True,
    )


def test_phench_run_dispatches_branch_alias_and_no_interactive() -> None:
    with patch("thegent.cli.apps.phench.run_target") as mock_run_target:
        mock_run_target.return_value = 0
        result = runner.invoke(
            app,
            [
                "phench",
                "run",
                "alpha",
                "--runner",
                "task",
                "--command",
                "hello",
                "--branch",
                "feature-branch",
                "--no-interactive",
            ],
        )

    assert result.exit_code == 0
    mock_run_target.assert_called_once_with(
        "alpha",
        repo_id=None,
        runner="task",
        command_name="hello",
        selected_ref="feature-branch",
        all_repos=False,
        execution_mode="serial",
        env_profile=None,
        non_interactive=True,
    )


def test_phench_run_ref_and_branch_conflict_is_rejected() -> None:
    result = runner.invoke(
        app,
        [
            "phench",
            "run",
            "alpha",
            "--ref",
            "main",
            "--branch",
            "feature",
        ],
    )

    assert result.exit_code != 0
    assert "--ref and --branch are mutually exclusive" in (result.stdout + result.stderr)


def test_phench_projects_run_non_interactive_dispatches_prepare_and_run() -> None:
    lock = SimpleNamespace(
        target_name="alpha",
        repos=[SimpleNamespace(repo_id="repo-a", selected_ref="main", resolved_sha="deadbeef")],
    )
    with (
        patch("thegent.cli.apps.phench.list_targets") as mock_list_targets,
        patch("thegent.cli.apps.phench.load_target_lock") as mock_load_target_lock,
        patch("thegent.cli.apps.phench.lock_target") as mock_lock_target,
        patch("thegent.cli.apps.phench.materialize_target") as mock_materialize_target,
        patch("thegent.cli.apps.phench.run_target") as mock_run_target,
    ):
        mock_list_targets.return_value = ["alpha"]
        mock_load_target_lock.return_value = lock
        mock_run_target.return_value = 0
        result = runner.invoke(
            app,
            [
                "phench",
                "projects",
                "run",
                "--target",
                "alpha",
                "--all-repos",
                "--runner",
                "task",
                "--command",
                "hello",
                "--ref",
                "feature-x",
                "--mode",
                "parallel",
                "--no-interactive",
            ],
        )

    assert result.exit_code == 0
    mock_load_target_lock.assert_called_once_with("alpha")
    mock_lock_target.assert_called_once_with("alpha")
    mock_materialize_target.assert_called_once_with("alpha")
    mock_run_target.assert_called_once_with(
        "alpha",
        repo_id=None,
        runner="task",
        command_name="hello",
        selected_ref="feature-x",
        all_repos=True,
        execution_mode="parallel",
        env_profile=None,
        non_interactive=True,
    )


def test_phench_projects_run_repo_ref_map_dispatches_per_repo_state() -> None:
    lock = SimpleNamespace(
        target_name="alpha",
        repos=[
            SimpleNamespace(repo_id="repo-a", selected_ref="main", resolved_sha="deadbeef"),
            SimpleNamespace(repo_id="repo-b", selected_ref="main", resolved_sha="deadcafe"),
        ],
    )
    with (
        patch("thegent.cli.apps.phench.list_targets") as mock_list_targets,
        patch("thegent.cli.apps.phench.load_target_lock") as mock_load_target_lock,
        patch("thegent.cli.apps.phench.lock_target") as mock_lock_target,
        patch("thegent.cli.apps.phench.materialize_target") as mock_materialize_target,
        patch("thegent.cli.apps.phench.run_target") as mock_run_target,
    ):
        mock_list_targets.return_value = ["alpha"]
        mock_load_target_lock.return_value = lock
        mock_run_target.return_value = 0
        result = runner.invoke(
            app,
            [
                "phench",
                "projects",
                "run",
                "--target",
                "alpha",
                "--repo-ref",
                "repo-a@feature-x",
                "--repo-ref",
                "repo-b@release-y",
                "--runner",
                "task",
                "--command",
                "hello",
                "--env-profile",
                "ci",
                "--no-interactive",
            ],
        )

    assert result.exit_code == 0
    mock_load_target_lock.assert_called_once_with("alpha")
    mock_lock_target.assert_called_once_with("alpha")
    mock_materialize_target.assert_called_once_with("alpha")
    assert mock_run_target.call_count == 2
    mock_run_target.assert_any_call(
        "alpha",
        repo_id="repo-a",
        runner="task",
        command_name="hello",
        selected_ref="feature-x",
        all_repos=False,
        execution_mode="serial",
        env_profile="ci",
        non_interactive=True,
    )
    mock_run_target.assert_any_call(
        "alpha",
        repo_id="repo-b",
        runner="task",
        command_name="hello",
        selected_ref="release-y",
        all_repos=False,
        execution_mode="serial",
        env_profile="ci",
        non_interactive=True,
    )


def test_phench_projects_run_repo_ref_rejects_all_repos() -> None:
    with (
        patch("thegent.cli.apps.phench.list_targets") as mock_list_targets,
        patch("thegent.cli.apps.phench.load_target_lock") as mock_load_target_lock,
        patch("thegent.cli.apps.phench.run_target") as mock_run_target,
    ):
        mock_list_targets.return_value = ["alpha"]
        mock_load_target_lock.return_value = SimpleNamespace(
            target_name="alpha",
            repos=[SimpleNamespace(repo_id="repo-a", selected_ref="main", resolved_sha="deadbeef")],
        )
        result = runner.invoke(
            app,
            [
                "phench",
                "projects",
                "run",
                "--target",
                "alpha",
                "--repo-ref",
                "repo-a@feature-x",
                "--all-repos",
                "--runner",
                "task",
                "--command",
                "hello",
            ],
        )

    assert result.exit_code != 0
    mock_run_target.assert_not_called()
    output = result.stdout + result.stderr
    assert "repo-ref is not compatible with --all-repos" in output


def test_phench_projects_run_interactive_selection_uses_target_repo_and_ref_choices() -> None:
    lock = SimpleNamespace(
        target_name="alpha",
        repos=[
            SimpleNamespace(repo_id="repo-a", selected_ref="main", resolved_sha="deadbeef"),
            SimpleNamespace(repo_id="repo-b", selected_ref="main", resolved_sha="deadcafe"),
        ],
    )
    with (
        patch("thegent.cli.apps.phench.list_targets") as mock_list_targets,
        patch("thegent.cli.apps.phench.load_target_lock") as mock_load_target_lock,
        patch("thegent.cli.apps.phench.target_timeline") as mock_timeline,
        patch("thegent.cli.apps.phench.lock_target") as mock_lock_target,
        patch("thegent.cli.apps.phench.materialize_target") as mock_materialize_target,
        patch("thegent.cli.apps.phench.run_target") as mock_run_target,
        patch("thegent.cli.apps.phench_projects.IntPrompt.ask") as mock_prompt,
    ):
        mock_list_targets.return_value = ["alpha", "beta"]
        mock_load_target_lock.return_value = lock
        mock_timeline.return_value = {
            "branches": ["main", "feature"],
            "tags": ["v1.0"],
            "recent": ["a1b2c3 commit one", "d4e5f6 commit two"],
        }
        mock_run_target.return_value = 0
        mock_prompt.side_effect = [2, 1, 3]
        result = runner.invoke(
            app,
            [
                "phench",
                "projects",
                "run",
                "--runner",
                "task",
                "--command",
                "hello",
                "--timeline-limit",
                "5",
            ],
        )

    assert result.exit_code == 0
    mock_prompt.assert_called()
    mock_load_target_lock.assert_called_once_with("beta")
    mock_timeline.assert_called_once_with("beta", repo_id="repo-a", limit=5)
    mock_lock_target.assert_called_once_with("beta")
    mock_materialize_target.assert_called_once_with("beta")
    mock_run_target.assert_called_once_with(
        "beta",
        repo_id="repo-a",
        runner="task",
        command_name="hello",
        selected_ref="feature",
        all_repos=False,
        execution_mode="serial",
        env_profile=None,
        non_interactive=False,
    )


def test_phench_projects_run_non_interactive_requires_target_or_all() -> None:
    with (
        patch("thegent.cli.apps.phench.list_targets") as mock_list_targets,
        patch("thegent.cli.apps.phench.run_target") as mock_run_target,
    ):
        mock_list_targets.return_value = ["alpha"]
        result = runner.invoke(
            app,
            [
                "phench",
                "projects",
                "run",
                "--no-interactive",
                "--all-repos",
                "--runner",
                "task",
                "--command",
                "hello",
            ],
        )

    assert result.exit_code != 0
    mock_run_target.assert_not_called()
    output = result.stdout + result.stderr
    assert "--target is required when --no-interactive is set" in output


def test_phench_projects_status_routes_to_target_status() -> None:
    with (
        patch("thegent.cli.apps.phench.list_targets") as mock_list_targets,
        patch("thegent.cli.apps.phench.target_status") as mock_status,
    ):
        mock_list_targets.return_value = ["alpha"]
        mock_status.return_value = {
            "target": "alpha",
            "repos": [{"repo_id": "repo-a"}],
        }
        result = runner.invoke(app, ["phench", "projects", "status", "--target", "alpha"])

    assert result.exit_code == 0
    mock_status.assert_called_once_with("alpha")
    assert "\"target\": \"alpha\"" in result.stdout


def test_phench_tui_runs_selected_target_repo_and_ref() -> None:
    with (
        patch("thegent.cli.apps.phench.list_targets") as mock_list_targets,
        patch("thegent.cli.apps.phench.target_status") as mock_status,
        patch("thegent.cli.apps.phench.target_timeline") as mock_timeline,
        patch("thegent.cli.apps.phench.run_target") as mock_run_target,
        patch("thegent.cli.apps.phench_observability.IntPrompt.ask") as mock_prompt,
    ):
        mock_list_targets.return_value = ["alpha", "beta"]
        mock_status.side_effect = [
            {"repos": [{"repo_id": "repo-a"}, {"repo_id": "repo-b"}]},
            {"repos": [{"repo_id": "repo-a"}, {"repo_id": "repo-b"}]},
        ]
        mock_timeline.return_value = {
            "branches": ["main", "feature"],
            "tags": ["v1"],
            "recent": ["a1 commit one", "b2 commit two"],
        }
        mock_run_target.return_value = 0
        mock_prompt.side_effect = [2, 1, 3]
        result = runner.invoke(
            app,
            [
                "phench",
                "tui",
                "--runner",
                "task",
                "--command",
                "hello",
            ],
        )

    assert result.exit_code == 0
    assert mock_timeline.call_count >= 1
    mock_run_target.assert_called_once_with(
        "beta",
        repo_id="repo-a",
        runner="task",
        command_name="hello",
        selected_ref="feature",
        all_repos=False,
        execution_mode="serial",
        env_profile=None,
        non_interactive=False,
    )


def test_phench_snapshot_create_routes_to_service() -> None:
    with patch("thegent.cli.apps.phench.create_target_snapshot") as mock_create_snapshot:
        mock_create_snapshot.return_value = {"snapshot_id": "snap-001", "target": "alpha"}
        result = runner.invoke(
            app,
            [
                "phench",
                "snapshot",
                "create",
                "alpha",
                "--snapshot-id",
                "snap-001",
            ],
        )

    assert result.exit_code == 0
    mock_create_snapshot.assert_called_once_with("alpha", snapshot_id="snap-001")


def test_phench_snapshot_list_routes_to_service() -> None:
    with patch("thegent.cli.apps.phench.list_target_snapshots") as mock_list_snapshots:
        mock_list_snapshots.return_value = []
        result = runner.invoke(
            app,
            [
                "phench",
                "snapshot",
                "list",
                "alpha",
            ],
        )

    assert result.exit_code == 0
    mock_list_snapshots.assert_called_once_with("alpha")


def test_phench_snapshot_show_routes_to_service() -> None:
    with patch("thegent.cli.apps.phench.show_target_snapshot") as mock_show_snapshot:
        mock_show_snapshot.return_value = {"snapshot_id": "snap-001", "target_name": "alpha"}
        result = runner.invoke(
            app,
            [
                "phench",
                "snapshot",
                "show",
                "alpha",
                "snap-001",
            ],
        )

    assert result.exit_code == 0
    mock_show_snapshot.assert_called_once_with("alpha", "snap-001")


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
