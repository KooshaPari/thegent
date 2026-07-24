"""WL-124 hardening: verify new CLI command stubs return expected types."""

from __future__ import annotations

import importlib


def test_project_commands_new_exports_exist() -> None:
    mod = importlib.import_module("thegent.cli.commands.project_commands")

    assert hasattr(mod, "project_get_cmd")
    assert hasattr(mod, "project_register_cmd")
    assert hasattr(mod, "project_list_cmd")


def test_project_get_cmd_returns_dict() -> None:
    from thegent.cli.commands.project_commands import project_get_cmd

    result = project_get_cmd()
    assert isinstance(result, dict)


def test_queue_commands_new_exports_exist() -> None:
    mod = importlib.import_module("thegent.cli.commands.queue_commands")

    assert hasattr(mod, "queue_list_cmd")
    assert hasattr(mod, "queue_status_cmd")
    assert hasattr(mod, "queue_drain_cmd")


def test_queue_status_cmd_returns_dict() -> None:
    from thegent.cli.commands.queue_commands import queue_status_cmd

    result = queue_status_cmd()
    assert isinstance(result, dict)


def test_queue_drain_cmd_returns_dict() -> None:
    from thegent.cli.commands.queue_commands import queue_drain_cmd

    result = queue_drain_cmd()
    assert isinstance(result, dict)


def test_recovery_commands_new_exports_exist() -> None:
    mod = importlib.import_module("thegent.cli.commands.recovery_commands")

    assert hasattr(mod, "recover_status_cmd")
    assert hasattr(mod, "forensics_snapshot_cmd")
    assert hasattr(mod, "recover_run_cmd")
    assert hasattr(mod, "recover_drill_cmd")


def test_recover_run_cmd_returns_dict() -> None:
    from thegent.cli.commands.recovery_commands import recover_run_cmd

    result = recover_run_cmd()
    assert isinstance(result, dict)


def test_recover_drill_cmd_returns_dict() -> None:
    from thegent.cli.commands.recovery_commands import recover_drill_cmd

    result = recover_drill_cmd()
    assert isinstance(result, dict)


def test_operations_commands_new_exports_exist() -> None:
    mod = importlib.import_module("thegent.cli.commands.operations_commands")

    assert hasattr(mod, "ops_runbook_cmd")
    assert hasattr(mod, "ops_health_cmd")
    assert hasattr(mod, "ops_audit_cmd")
    assert hasattr(mod, "operations_cmd")  # backward compat alias


def test_ops_runbook_cmd_returns_dict() -> None:
    from thegent.cli.commands.operations_commands import ops_runbook_cmd

    result = ops_runbook_cmd()
    assert isinstance(result, dict)


def test_ops_health_cmd_returns_dict() -> None:
    from thegent.cli.commands.operations_commands import ops_health_cmd

    result = ops_health_cmd()
    assert isinstance(result, dict)


def test_ops_audit_cmd_returns_dict() -> None:
    from thegent.cli.commands.operations_commands import ops_audit_cmd

    result = ops_audit_cmd()
    assert isinstance(result, dict)


def test_operations_cmd_backward_compat_returns_int() -> None:
    from thegent.cli.commands.operations_commands import operations_cmd

    result = operations_cmd()
    assert isinstance(result, int)
    assert result == 0


def test_governance_cmds_new_exports_exist() -> None:
    mod = importlib.import_module("thegent.cli.commands.governance_cmds")

    assert hasattr(mod, "gov_policy_lint_cmd")
    assert hasattr(mod, "gov_policy_apply_cmd")
    assert hasattr(mod, "gov_policy_diff_cmd")


def test_gov_policy_lint_cmd_returns_dict() -> None:
    from thegent.cli.commands.governance_cmds import gov_policy_lint_cmd

    result = gov_policy_lint_cmd()
    assert isinstance(result, dict)


def test_gov_policy_apply_cmd_returns_dict() -> None:
    from thegent.cli.commands.governance_cmds import gov_policy_apply_cmd

    result = gov_policy_apply_cmd()
    assert isinstance(result, dict)


def test_gov_policy_diff_cmd_returns_dict() -> None:
    from thegent.cli.commands.governance_cmds import gov_policy_diff_cmd

    result = gov_policy_diff_cmd()
    assert isinstance(result, dict)


def test_all_modules_have_all_list() -> None:
    """Every hardened module must export a non-empty __all__ list."""
    modules = [
        "thegent.cli.commands.project_commands",
        "thegent.cli.commands.queue_commands",
        "thegent.cli.commands.recovery_commands",
        "thegent.cli.commands.operations_commands",
        "thegent.cli.commands.governance_cmds",
    ]
    for mod_path in modules:
        mod = importlib.import_module(mod_path)
        assert hasattr(mod, "__all__"), f"{mod_path} missing __all__"
        assert len(mod.__all__) > 0, f"{mod_path} __all__ is empty"
