"""WL-703 hardening: L9 cliproxy_login_cmd canonical-surface pins.

WL-149 surfaced three L9 LOW findings in ``tests/test_unit_cli_commands_a.py``
-- WL-702 sealed ``TestAuditVerifyCmdImpl`` + ``TestSweepCmdImpl``;
``TestCliproxyLoginCmdImpl`` was the third LOW finding deferred because
its monkey-patch sites targeted a non-existent
``thegent.cli.commands.model_cmds_rules`` module. WL-703 ships the
canonical surface so the three tests now run for real and the rules-
layer contract is pinned against future drift.

Pins covered:

1. **Canonical module resolution.** Both ``console`` and
   ``_run_cliproxyctl_machine_command`` are reachable at the canonical
   location -- ``thegent.cli.commands.model_cmds_rules`` -- distinct
   from ``thegent.cli.commands.model_cmds`` (the WL-124 stable-import
   alias module that hosts the thin ``cliproxy_login_cmd`` dispatcher).
2. **Dispatcher contract.** ``cliproxy_login_cmd`` is no longer a
   single-line ``return 0`` stub. It dispatches to
   ``_run_cliproxyctl_machine_command`` and converts the canonical
   ``ValueError`` / ``FileNotFoundError`` exceptions into
   ``typer.Exit(code=1)`` with a console message.
3. **Delegate pin.** The helper delegates to
   :func:`thegent.use_cases.manage_cliproxy_login.run_login` (the
   canonical implementation) rather than duplicating logic.
4. **AST purity.** No ``run_login(`` invocation at module top-level of
   ``model_cmds.py`` (lazy dispatch -- importing the dispatcher does
   not trigger the use-case layer).
5. **Console pin.** The rules-layer ``console`` is a Rich ``Console``
   instance, monkey-patchable at the canonical location.
6. **Unskip pin.** ``TestCliproxyLoginCmdImpl`` carries no skip mark.
7. **Docstring pin.** ``cliproxy_login_cmd`` docstring is >=4 lines
   mentioning both ``_run_cliproxyctl_machine_command`` and
   ``model_cmds_rules``.
"""

from __future__ import annotations

import ast
import importlib
from unittest.mock import MagicMock, patch

import pytest
import typer
from rich.console import Console


# ---------------------------------------------------------------------------
# Canonical module resolution
# ---------------------------------------------------------------------------


def test_model_cmds_rules_module_exists() -> None:
    """Canonical rules module imports cleanly at the WL-703 path."""
    mod = importlib.import_module("thegent.cli.commands.model_cmds_rules")
    assert mod is not None
    assert hasattr(mod, "console")
    assert hasattr(mod, "_run_cliproxyctl_machine_command")


def test_model_cmds_rules_distinct_from_model_cmds() -> None:
    """Rules layer lives in a separate module from the dispatcher."""
    rules = importlib.import_module("thegent.cli.commands.model_cmds_rules")
    cmds = importlib.import_module("thegent.cli.commands.model_cmds")
    assert rules is not cmds
    assert hasattr(cmds, "cliproxy_login_cmd")
    assert not hasattr(cmds, "_run_cliproxyctl_machine_command")


def test_console_is_rich_console() -> None:
    """``console`` is a Rich ``Console`` (monkey-patchable at canonical path)."""
    from thegent.cli.commands.model_cmds_rules import console

    assert isinstance(console, Console)


def test_rules_layer_exports_canonical_symbols() -> None:
    """``__all__`` exposes both ``console`` and ``_run_cliproxyctl_machine_command``."""
    mod = importlib.import_module("thegent.cli.commands.model_cmds_rules")
    assert "console" in mod.__all__
    assert "_run_cliproxyctl_machine_command" in mod.__all__


# ---------------------------------------------------------------------------
# Dispatcher contract
# ---------------------------------------------------------------------------


def test_cliproxy_login_cmd_resolves_to_canonical_module() -> None:
    """``cliproxy_login_cmd`` is the canonical dispatch from ``model_cmds``."""
    from thegent.cli.commands.model_cmds import cliproxy_login_cmd

    import thegent.cli.commands.model_cmds as cmds_mod

    assert cmds_mod.cliproxy_login_cmd is cliproxy_login_cmd


def test_cliproxy_login_cmd_is_not_zero_returning_stub() -> None:
    """``cliproxy_login_cmd`` body is no longer a single-line ``return 0``."""
    src = importlib.import_module("thegent.cli.commands.model_cmds").cliproxy_login_cmd
    import inspect

    source = inspect.getsource(src)
    # Reject the single-line stub form WL-124.
    body_lines = [line.strip() for line in source.splitlines() if line.strip()]
    non_doc_lines = [line for line in body_lines if not line.startswith('"""') and not line.startswith("'''")]
    assert not (len(non_doc_lines) <= 2 and any("return 0" in line for line in non_doc_lines))
    # Body must reference the rules-layer dispatcher.
    assert "_run_cliproxyctl_machine_command" in source


def test_cliproxy_login_cmd_success_exits_zero() -> None:
    """Successful delegated login raises ``typer.Exit(0)``."""
    from thegent.cli import cliproxy_login_cmd

    with patch(
        "thegent.cli.commands.model_cmds_rules._run_cliproxyctl_machine_command",
        return_value={"exit_code": 0, "message": "Login successful"},
    ):
        with pytest.raises(typer.Exit) as exc_info:
            cliproxy_login_cmd(provider="claude")
        assert exc_info.value.exit_code == 0


def test_cliproxy_login_cmd_value_error_exits_one_with_message() -> None:
    """``ValueError`` from the helper prints invalid/failed message + Exit(1)."""
    from thegent.cli import cliproxy_login_cmd

    with (
        patch(
            "thegent.cli.commands.model_cmds_rules.console",
        ) as mock_console,
        patch(
            "thegent.cli.commands.model_cmds_rules._run_cliproxyctl_machine_command",
            side_effect=ValueError("Invalid provider"),
        ),
    ):
        with pytest.raises(typer.Exit) as exc_info:
            cliproxy_login_cmd(provider="bad")
        assert exc_info.value.exit_code == 1
    printed = [str(c) for c in mock_console.print.call_args_list]
    assert any("invalid" in p.lower() or "failed" in p.lower() for p in printed)


def test_cliproxy_login_cmd_file_not_found_exits_one_with_message() -> None:
    """``FileNotFoundError`` from the helper prints missing-binary message + Exit(1)."""
    from thegent.cli import cliproxy_login_cmd

    with (
        patch(
            "thegent.cli.commands.model_cmds_rules.console",
        ) as mock_console,
        patch(
            "thegent.cli.commands.model_cmds_rules._run_cliproxyctl_machine_command",
            side_effect=FileNotFoundError("not found"),
        ),
    ):
        with pytest.raises(typer.Exit) as exc_info:
            cliproxy_login_cmd(provider="claude")
        assert exc_info.value.exit_code == 1
    printed = [str(c) for c in mock_console.print.call_args_list]
    assert any("missing" in p.lower() or "not found" in p.lower() or "binary" in p.lower() for p in printed)


# ---------------------------------------------------------------------------
# Delegate pin
# ---------------------------------------------------------------------------


def test_run_cliproxyctl_helper_delegates_to_use_case_run_login() -> None:
    """The rules-layer helper delegates to ``manage_cliproxy_login.run_login``."""
    from thegent.cli.commands.model_cmds_rules import _run_cliproxyctl_machine_command

    settings_obj = MagicMock()
    with patch(
        "thegent.use_cases.manage_cliproxy_login.run_login",
        return_value=0,
    ) as mock_run_login:
        result = _run_cliproxyctl_machine_command("claude", settings=settings_obj)
    mock_run_login.assert_called_once()
    assert result["exit_code"] == 0
    assert "Login successful" in result["message"]


def test_run_cliproxyctl_helper_returns_dict_shape() -> None:
    """Helper returns ``{"exit_code": <int>, "message": <str>}`` shape."""
    from thegent.cli.commands.model_cmds_rules import _run_cliproxyctl_machine_command

    settings_obj = MagicMock()
    with patch(
        "thegent.use_cases.manage_cliproxy_login.run_login",
        return_value=2,
    ):
        result = _run_cliproxyctl_machine_command("claude", settings=settings_obj)
    assert isinstance(result, dict)
    assert "exit_code" in result
    assert "message" in result
    assert result["exit_code"] == 2


# ---------------------------------------------------------------------------
# AST purity
# ---------------------------------------------------------------------------


def test_model_cmds_no_top_level_run_login_invocation() -> None:
    """No ``run_login(`` at module top-level -- lazy dispatch pattern."""
    from pathlib import Path

    src = Path("src/thegent/cli/commands/model_cmds.py").read_text()
    tree = ast.parse(src)
    calls = [node for node in tree.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)]
    bad = [
        c.value.func
        for c in calls
        if (isinstance(c.value.func, ast.Name) and c.value.func.id == "run_login")
        or (isinstance(c.value.func, ast.Attribute) and c.value.func.attr == "run_login")
    ]
    assert bad == []


def test_model_cmds_rules_docstring_is_substantial() -> None:
    """Rules-layer module docstring documents the canonical contract."""
    from thegent.cli.commands.model_cmds_rules import __doc__

    assert __doc__ is not None
    assert len(__doc__.strip().splitlines()) >= 4
    assert "console" in __doc__
    assert "_run_cliproxyctl_machine_command" in __doc__


# ---------------------------------------------------------------------------
# Docstring + unskip pins
# ---------------------------------------------------------------------------


def test_cliproxy_login_cmd_docstring_is_substantial() -> None:
    """``cliproxy_login_cmd`` docstring mentions the helper + rules module."""
    import inspect

    from thegent.cli.commands.model_cmds import cliproxy_login_cmd

    doc = inspect.getdoc(cliproxy_login_cmd)
    assert doc is not None
    lines = [line for line in doc.splitlines() if line.strip()]
    assert len(lines) >= 4
    assert "_run_cliproxyctl_machine_command" in doc
    assert "model_cmds_rules" in doc


def test_test_cliproxy_login_cmd_impl_has_no_skip_mark() -> None:
    """``TestCliproxyLoginCmdImpl`` carries no ``skip`` mark (no WL-124 reason)."""
    # Lazy import so the skip is observable even if any decorator is
    # re-added in the future.
    import importlib

    test_mod = importlib.import_module("tests.test_unit_cli_commands_a")
    cls = getattr(test_mod, "TestCliproxyLoginCmdImpl", None)
    assert cls is not None
    skip_marker = getattr(cls, "pytestmark", None)
    if skip_marker is not None:
        # ``pytestmark`` is a list-like; iterate it.
        markers = list(skip_marker)
        skip_reasons = [m.kwargs.get("reason", "") for m in markers if getattr(m, "name", "") == "skip"]
        assert not any("WL-124" in r for r in skip_reasons)


# ---------------------------------------------------------------------------
# Source path pin (parity with WL-702 sweep patch repair)
# ---------------------------------------------------------------------------


def test_dispatcher_sources_helper_via_local_import() -> None:
    """``cliproxy_login_cmd`` body imports the rules-layer helper at call time."""
    import inspect

    from thegent.cli.commands.model_cmds import cliproxy_login_cmd

    source = inspect.getsource(cliproxy_login_cmd)
    # Local import from the canonical rules module is the WL-702 pattern.
    assert "from thegent.cli.commands.model_cmds_rules import" in source
    # No re-export alias -- monkey-patches resolve cleanly.
    assert "model_cmds_rules._run_cliproxyctl_machine_command" in source
