"""WL-156 regression: data_protection_cmd must be wired and dispatch
through the canonical ``_normalize_output_format`` helper.

The WL-149 audit sealed the seven ``drift_cmd / escalate_*_cmd /
migration_cmd / policy_show_cmd / sweep_cmd`` shadow surfaces, but
left ``data_protection_cmd`` as a LOW finding because:

1. ``thegent.cli.data_protection_cmd`` was not re-exported at the
   cli root (callers could not resolve the canonical implementation).
2. The canonical implementation in
   ``thegent.cli.governance.governance_data_protection_cmds`` only
   recognized ``format == "json"`` directly — it bypassed the
   canonical ``_normalize_output_format`` dispatch helper.
3. The associated test class ``TestDataProtectionCmdImpl`` was
   marked ``@pytest.mark.skip(reason="WL-124 refactoring or not
   implemented")``.

WL-156 closes the LOW finding by:

* Re-exporting ``data_protection_cmd`` from ``thegent.cli``.
* Routing the format dispatch through ``_normalize_output_format``
  so rich / json / csv / md / unknown all render correctly.
* Removing the skip mark on the test class and fixing the test
  bug that was lurking behind the skip (``mock_console`` parameter
  missing on the JSON test).

This regression test pins the resolved module and the dispatch
behaviour so a future "consolidate the governance wrappers" PR
cannot re-introduce the gap without a test failure.
"""

from __future__ import annotations

import importlib
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Section 1 — wiring pins
# ---------------------------------------------------------------------------

CANONICAL_MODULE = "thegent.cli.governance.governance_data_protection_cmds"
STUB_MODULE = "thegent.cli.commands.governance_cmds"
CLI_ROOT = "thegent.cli"


def _resolved_module(name: str) -> str:
    """Return ``__module__`` for the named attribute on ``thegent.cli``."""
    cli = importlib.import_module(CLI_ROOT)
    attr = getattr(cli, name)
    return getattr(attr, "__module__", "<unknown>")


def test_data_protection_cmd_resolves_to_canonical_module() -> None:
    """``from thegent.cli import data_protection_cmd`` must resolve to
    the canonical governance module, not the WL-124 stub monolith.

    The canonical module is the one that contains the real
    implementation (real ``_normalize_output_format`` dispatch, real
    ``*_impl`` call, real rich/json rendering). The stub module only
    contains a zero-returning placeholder.
    """
    resolved = _resolved_module("data_protection_cmd")
    assert resolved == CANONICAL_MODULE, (
        f"thegent.cli.data_protection_cmd resolves to {resolved!r}; "
        f"expected canonical {CANONICAL_MODULE!r}. The WL-124 stub in "
        f"{STUB_MODULE!r} is shadowing the real implementation."
    )


def test_data_protection_cmd_is_in_cli_root_all() -> None:
    """``data_protection_cmd`` must be in ``thegent.cli.__all__`` so
    that ``from thegent.cli import *`` consumers see it.

    The WL-124 stable-import surface intentionally re-exports every
    ``*_cmd`` wrapper; ``data_protection_cmd`` was the LOW-finding
    missing entry.
    """
    cli = importlib.import_module(CLI_ROOT)
    assert "data_protection_cmd" in cli.__all__, (
        "thegent.cli.__all__ does not list 'data_protection_cmd' — the WL-124 re-export surface is incomplete."
    )


def test_canonical_module_exposes_real_implementation() -> None:
    """The canonical module must expose ``data_protection_cmd`` as a
    callable that accepts ``format`` (positional or keyword) and
    returns ``None``.
    """
    canon = importlib.import_module(CANONICAL_MODULE)
    assert hasattr(canon, "data_protection_cmd")
    fn = canon.data_protection_cmd
    assert callable(fn)

    # Signature: format is the only documented arg.
    import inspect

    sig = inspect.signature(fn)
    assert "format" in sig.parameters
    # Returns None (CLI commands print via console, no return value).
    assert sig.return_annotation in (None, "None", inspect.Signature.empty)


def test_stub_module_is_safe_zero_returning() -> None:
    """Defensive pin: if anyone ever re-imports from the stub module,
    the function must still be a zero-returning stub so the shadow
    cannot silently swallow a real CLI invocation.
    """
    stub = importlib.import_module(STUB_MODULE)
    assert hasattr(stub, "data_protection_cmd"), (
        f"{STUB_MODULE} no longer exposes data_protection_cmd (stub namespace shrunk)"
    )
    result = stub.data_protection_cmd("r1", "blocked", format="json")
    assert result in (0, None), (
        f"{STUB_MODULE}.data_protection_cmd returned {result!r}; "
        f"WL-124 stubs must be zero-returning so they cannot shadow "
        f"real implementations with side effects."
    )


# ---------------------------------------------------------------------------
# Section 2 — dispatch helper parity
# ---------------------------------------------------------------------------

_STATUS = {
    "session_dir": "/tmp/sessions",
    "permissions_restricted": True,
    "masking_enabled": True,
    "retention_policy_days": 30,
}


def _patched_status():
    """Patch the canonical ``get_data_protection_status_impl`` at the
    source module the canonical implementation imports from. The
    WL-124 re-export under ``thegent.cli.commands.impl`` is a name
    binding — the canonical implementation imports from the source
    module directly, so patching the source path is the only way to
    redirect the dispatch.
    """
    return patch(
        "thegent.cli.governance.governance_impl.get_data_protection_status_impl",
        return_value=_STATUS,
    )


def test_dispatch_uses_normalize_output_format_helper() -> None:
    """The canonical implementation must dispatch through
    ``thegent.cli._normalize_output_format`` instead of branch-on
    ``format == "json"`` directly.

    Pins the contract that the canonical re-export surface drives
    the dispatcher. If a future refactor reverts to a direct
    ``format == "json"`` check, the rich path will stop honouring
    the helper and callers will see raw bytes instead of tables.
    """
    from thegent.cli.commands._cli_shared import _normalize_output_format

    from thegent.cli.governance.governance_data_protection_cmds import (
        data_protection_cmd,
    )

    # The helper is the canonical entry point. Pin its presence.
    assert callable(_normalize_output_format)

    # If the implementation stops calling _normalize_output_format,
    # this spy will never be invoked when format='json' is passed.
    # Patch the SOURCE module — the canonical implementation does
    # `from thegent.cli.commands._cli_shared import _normalize_output_format`
    # inside the function body, so the source module is the only
    # patch point that intercepts the call.
    with patch(
        "thegent.cli.commands._cli_shared._normalize_output_format",
        wraps=_normalize_output_format,
    ) as spy:
        with _patched_status():
            with patch("thegent.cli.console"):
                data_protection_cmd(format="json")

    spy.assert_called_once_with("json")


def test_rich_dispatch_when_format_is_none() -> None:
    """``data_protection_cmd()`` (no format) must render the rich
    table — the canonical CLI default. Pins the default-rendering
    contract so the LOW finding's "no rich rendering" regression
    cannot recur.
    """
    from thegent.cli.governance.governance_data_protection_cmds import (
        data_protection_cmd,
    )

    with _patched_status():
        with patch("thegent.cli.console") as mock_console:
            data_protection_cmd()

    mock_console.print.assert_called_once()
    # The Table is rendered via console.print — confirm we hit the
    # rich path (a Rich.Table instance) and not a raw bytes dump.
    rendered = mock_console.print.call_args.args[0]
    # Rich's Table class — duck-type check (avoids import in test).
    assert hasattr(rendered, "title"), (
        "data_protection_cmd() did not render a Rich Table; got a non-Rich printable instead."
    )
    assert rendered.title == "Data Protection Status"


def test_json_dispatch_when_format_is_json_string() -> None:
    """``data_protection_cmd(format='json')`` must call
    ``_normalize_output_format('json')`` and emit the JSON payload
    via ``console.print``.
    """
    from thegent.cli.governance.governance_data_protection_cmds import (
        data_protection_cmd,
    )

    with _patched_status():
        with patch("thegent.cli.console") as mock_console:
            data_protection_cmd(format="json")

    mock_console.print.assert_called_once()
    # The JSON payload is orjson bytes — confirm the canonical
    # dispatcher rendered through console.print.
    call_args = str(mock_console.print.call_args)
    assert "retention_policy_days" in call_args
    assert "30" in call_args


def test_dispatch_via_normalized_rich() -> None:
    """When ``format`` is passed but normalizes to ``rich`` (e.g.
    ``'table'`` passes through unchanged), the rich path must be
    taken. Pins the helper's pass-through semantics for the
    canonical 'rich' lane.
    """
    from thegent.cli.governance.governance_data_protection_cmds import (
        data_protection_cmd,
    )

    with patch(
        "thegent.cli.commands._cli_shared._normalize_output_format",
        return_value="rich",
    ) as spy:
        with _patched_status():
            with patch("thegent.cli.console") as mock_console:
                data_protection_cmd(format="table")

    spy.assert_called_once_with("table")
    mock_console.print.assert_called_once()
    rendered = mock_console.print.call_args.args[0]
    assert hasattr(rendered, "title")


def test_dispatch_via_normalized_unknown_fallback() -> None:
    """When ``_normalize_output_format`` returns an unrecognised
    bucket (e.g. ``'csv'`` is its own bucket, but the canonical
    dispatch is rich|json — anything else falls through to the
    plain-text best-effort path). The fallback must call
    ``console.print`` so the call is never silently swallowed.
    """
    from thegent.cli.governance.governance_data_protection_cmds import (
        data_protection_cmd,
    )

    with patch(
        "thegent.cli.commands._cli_shared._normalize_output_format",
        return_value="csv",
    ):
        with _patched_status():
            with patch("thegent.cli.console") as mock_console:
                data_protection_cmd(format="csv")

    # Plain-text fallback: one print per status key (4 in our _STATUS).
    assert mock_console.print.call_count == len(_STATUS), (
        f"expected {len(_STATUS)} console.print calls; got {mock_console.print.call_count}"
    )
    # Confirm the fallback surface shows the key/value pairs.
    printed = " ".join(str(call.args[0]) for call in mock_console.print.call_args_list)
    assert "retention_policy_days" in printed
    assert "30" in printed


# ---------------------------------------------------------------------------
# Section 3 — proximity to the WL-149 sealed-pin surface
# ---------------------------------------------------------------------------


def test_data_protection_cmd_is_not_in_wl149_pin_set() -> None:
    """The WL-149 sealed-pin set explicitly covers seven shadowed
    functions. ``data_protection_cmd`` is the LOW finding that was
    NOT in the WL-149 set — pinning this conservatively so we don't
    regress the WL-149 surface by accidentally removing the WL-156
    function from the live re-export chain.
    """
    from thegent.cli import (
        data_protection_cmd,
        drift_cmd,
        escalate_add_cmd,
        escalate_list_cmd,
        escalate_resolve_cmd,
        migration_cmd,
        policy_show_cmd,
        sweep_cmd,
    )

    # All seven WL-149 names must remain reachable from the cli root.
    for name in (
        "drift_cmd",
        "escalate_add_cmd",
        "escalate_list_cmd",
        "escalate_resolve_cmd",
        "migration_cmd",
        "policy_show_cmd",
        "sweep_cmd",
    ):
        assert callable(locals()[name]), f"{name} not reachable from thegent.cli"

    # And the WL-156 name must also be reachable.
    assert callable(data_protection_cmd)


def test_data_protection_cmd_resolves_to_different_module_than_escalate_add() -> None:
    """The canonical module for ``data_protection_cmd`` is the
    ``governance_data_protection_cmds`` module, NOT the
    ``governance_escalation_hitl_cmds`` module. This guards against
    a future "consolidate the governance wrappers" PR accidentally
    folding ``data_protection_cmd`` into the wrong sibling module.
    """
    data_protection = _resolved_module("data_protection_cmd")
    escalate_add = _resolved_module("escalate_add_cmd")
    assert data_protection != escalate_add, (
        "data_protection_cmd and escalate_add_cmd must NOT share a "
        "canonical module — they are separate governance sub-areas."
    )
    assert data_protection.endswith("governance_data_protection_cmds")
    assert escalate_add.endswith("governance_escalation_hitl_cmds")


# ---------------------------------------------------------------------------
# Section 4 — defensive import-time pin
# ---------------------------------------------------------------------------


def test_canonical_module_is_pure_function_no_console_import_at_module_top() -> None:
    """The canonical module must NOT import ``thegent.cli.console``
    at module-import time. The console is imported lazily inside the
    function body so the canonical module can be imported without
    triggering rich.Table construction in test contexts.
    """
    import ast
    from pathlib import Path

    src_path = Path(
        importlib.import_module(CANONICAL_MODULE).__file__  # type: ignore[arg-type]
    )
    tree = ast.parse(src_path.read_text())
    top_level_imports = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_level_imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                top_level_imports.add(f"{mod}.{alias.name}")

    # Forbidden top-level imports — these would force-load rich
    # Table or the console at import time.
    forbidden = {
        "thegent.cli.console",
        "thegent.cli",  # would re-trigger the cli __init__.py side-effects
    }
    for name in list(top_level_imports):
        assert name not in forbidden, (
            f"{CANONICAL_MODULE} imports {name!r} at module top level — "
            f"this would force-load rich/console at import time. Move the "
            f"import inside the function body."
        )


def test_unskipped_test_class_reachable() -> None:
    """The WL-124 ``@pytest.mark.skip`` mark must be removed from
    ``TestDataProtectionCmdImpl`` so the regression that was skipped
    in the WL-149 audit is now actually exercised.

    This is the simplest possible WL-156 surface pin: pin that the
    test class is not skipped any more.
    """
    from tests.test_unit_cli_commands_a import TestDataProtectionCmdImpl

    # Skipped classes expose the skip marker via __pytest_marks__.
    skip_marks = [mark for mark in getattr(TestDataProtectionCmdImpl, "pytestmark", []) if mark.name == "skip"]
    assert skip_marks == [], (
        "TestDataProtectionCmdImpl is still marked @pytest.mark.skip — the WL-156 LOW finding is not sealed yet."
    )
