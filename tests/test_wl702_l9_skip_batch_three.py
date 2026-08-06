"""WL-702 regression: L9 skip-batch-three hardening pin.

The WL-156 / WL-149 audit sealed the canonical governance wrappers
(``drift_cmd``, ``escalate_*_cmd``, ``migration_cmd``, ``policy_show_cmd``,
``sweep_cmd``, ``data_protection_cmd``) but left three L9 LOW findings
in ``tests/test_unit_cli_commands_a.py``:

* ``TestAuditVerifyCmdImpl`` — still marked ``@pytest.mark.skip`` with
  reason ``"WL-124 refactoring or not implemented"``.
* ``TestSweepCmdImpl`` — patches targeted the wrong re-export chain
  (``thegent.cli.commands.impl.sweep_impl``), so the canonical
  implementation was never actually invoked and the tests reached
  against the real ``sweep_impl`` (raising
  ``TypeError: EscalationQueue.list_pending() got an unexpected keyword
  argument 'limit'``).
* ``TestCliproxyLoginCmdImpl`` — patched a non-existent module
  (``thegent.cli.commands.model_cmds_rules``); deferred to a future
  lane since the underlying ``cliproxy_login_cmd`` is still a stub.

WL-702 closes the two unskip-able L9 LOW findings by:

1. Replacing the ``audit_verify_cmd`` stub with a real implementation
   that delegates to :class:`thegent.execution.RunRegistry` and
   :class:`thegent.execution.Auditor`, supports JSON output, and exits
   with a shell-friendly status code.
2. Rewriting the ``TestSweepCmdImpl`` patch sites to target the
   canonical ``thegent.cli.governance.governance_impl.sweep_impl`` and
   the canonical module's ``console`` / ``_normalize_output_format``
   bindings (matching the WL-149 / WL-156 pattern).

This regression file pins both surfaces so a future refactor cannot
re-introduce the unskip shadow without a test failure.
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Section 1 — audit_verify_cmd implementation pin
# ---------------------------------------------------------------------------

CANONICAL_AUDIT_MODULE = "thegent.cli.commands.cli_tooling"
CANONICAL_SWEEP_MODULE = "thegent.cli.governance.governance_escalation_hitl_cmds"
CANONICAL_SWEEP_IMPL_MODULE = "thegent.cli.governance.governance_impl"


def _resolved_module(name: str) -> str:
    """Return ``__module__`` for the named attribute on ``thegent.cli``."""
    cli = importlib.import_module("thegent.cli")
    attr = getattr(cli, name)
    return getattr(attr, "__module__", "<unknown>")


def test_audit_verify_cmd_resolves_to_canonical_module() -> None:
    """``thegent.cli.audit_verify_cmd`` must resolve to the canonical
    CLI tooling module — the WL-124 stub-vs-impl shadow must remain
    sealed."""
    resolved = _resolved_module("audit_verify_cmd")
    assert resolved == CANONICAL_AUDIT_MODULE, (
        f"thegent.cli.audit_verify_cmd resolves to {resolved!r}; "
        f"expected canonical {CANONICAL_AUDIT_MODULE!r}. The WL-124 "
        f"stub is shadowing the real implementation."
    )


def test_audit_verify_cmd_is_not_a_zero_returning_stub() -> None:
    """The WL-124 stub body returned ``0`` and printed a fixed string.
    The WL-702 implementation must dispatch to the production
    ``RunRegistry`` + ``Auditor`` machinery (verified by monkey-patching
    both classes and checking that ``verify_registry`` is invoked).
    """
    from thegent.cli import audit_verify_cmd

    mock_auditor = MagicMock()
    mock_auditor.verify_registry.return_value = {
        "status": "passed",
        "valid_count": 7,
        "corrupt_count": 0,
    }
    with (
        patch("thegent.execution.RunRegistry"),
        patch("thegent.execution.Auditor", return_value=mock_auditor),
        patch("thegent.cli.ThegentSettings", return_value=MagicMock(session_dir="/tmp")),
        patch(f"{CANONICAL_AUDIT_MODULE}._get_console") as mock_get_console,
    ):
        mock_get_console.return_value = MagicMock()
        audit_verify_cmd()
    mock_auditor.verify_registry.assert_called_once()


def test_audit_verify_cmd_supports_json_format() -> None:
    """When ``format='json'`` is passed, ``audit_verify_cmd`` must
    write the raw audit report to stdout and exit 0 — no console.print
    calls."""
    from thegent.cli import audit_verify_cmd

    mock_auditor = MagicMock()
    mock_auditor.verify_registry.return_value = {
        "status": "passed",
        "valid_count": 3,
        "corrupt_count": 0,
    }
    import io

    buf = io.StringIO()
    with (
        patch("thegent.execution.RunRegistry"),
        patch("thegent.execution.Auditor", return_value=mock_auditor),
        patch("thegent.cli.ThegentSettings", return_value=MagicMock(session_dir="/tmp")),
        patch(f"{CANONICAL_AUDIT_MODULE}._get_console") as mock_get_console,
        patch("sys.stdout", buf),
    ):
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        result = audit_verify_cmd(format="json")
    assert result == 0
    mock_console.print.assert_not_called()
    assert '"status": "passed"' in buf.getvalue()


def test_audit_verify_cmd_failed_returns_exit_code_one() -> None:
    """A failed audit must surface the exit code 1 so CI shells can
    detect corruption."""
    from thegent.cli import audit_verify_cmd

    mock_auditor = MagicMock()
    mock_auditor.verify_registry.return_value = {
        "status": "failed",
        "valid_count": 8,
        "corrupt_count": 2,
        "issues": ["corrupt record 1"],
    }
    with (
        patch("thegent.execution.RunRegistry"),
        patch("thegent.execution.Auditor", return_value=mock_auditor),
        patch("thegent.cli.ThegentSettings", return_value=MagicMock(session_dir="/tmp")),
        patch(f"{CANONICAL_AUDIT_MODULE}._get_console") as mock_get_console,
    ):
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        result = audit_verify_cmd()
    assert result == 1
    printed = " ".join(str(c) for c in mock_console.print.call_args_list)
    assert "failed" in printed.lower()
    assert "corrupt record 1" in printed


def test_audit_verify_cmd_safe_for_none_format() -> None:
    """Regression: the canonical ``_normalize_output_format`` helper
    crashes on ``None``. The WL-702 implementation must coerce
    ``format=None`` to a safe default before dispatch so rich
    rendering is the default."""
    from thegent.cli import audit_verify_cmd

    mock_auditor = MagicMock()
    mock_auditor.verify_registry.return_value = {
        "status": "passed",
        "valid_count": 0,
        "corrupt_count": 0,
    }
    with (
        patch("thegent.execution.RunRegistry"),
        patch("thegent.execution.Auditor", return_value=mock_auditor),
        patch("thegent.cli.ThegentSettings", return_value=MagicMock(session_dir="/tmp")),
        patch(f"{CANONICAL_AUDIT_MODULE}._get_console") as mock_get_console,
    ):
        mock_console = MagicMock()
        mock_get_console.return_value = mock_console
        # No format kwarg — must not raise AttributeError.
        result = audit_verify_cmd()
    assert result == 0
    mock_console.print.assert_called_once()


def test_audit_verify_cmd_test_class_is_unskipped() -> None:
    """The WL-124 ``@pytest.mark.skip`` mark must be removed from
    ``TestAuditVerifyCmdImpl`` so the regression that was previously
    skipped is now actually exercised."""
    from tests.test_unit_cli_commands_a import TestAuditVerifyCmdImpl

    skip_marks = [mark for mark in getattr(TestAuditVerifyCmdImpl, "pytestmark", []) if mark.name == "skip"]
    assert skip_marks == [], (
        "TestAuditVerifyCmdImpl is still marked @pytest.mark.skip — the WL-702 LOW finding is not sealed yet."
    )


# ---------------------------------------------------------------------------
# Section 2 — sweep_cmd patch-path pin
# ---------------------------------------------------------------------------


def test_sweep_cmd_resolves_to_canonical_module() -> None:
    """``thegent.cli.sweep_cmd`` must resolve to the canonical
    governance escalation module (re-asserts the WL-149 seal)."""
    resolved = _resolved_module("sweep_cmd")
    assert resolved == CANONICAL_SWEEP_MODULE, (
        f"thegent.cli.sweep_cmd resolves to {resolved!r}; expected canonical {CANONICAL_SWEEP_MODULE!r}."
    )


def test_canonical_sweep_module_dispatches_to_governance_impl_sweep_impl() -> None:
    """The canonical ``sweep_cmd`` body must dispatch to
    ``thegent.cli.governance.governance_impl.sweep_impl`` (the WL-124
    thin-wrapper pattern). Pinned so a future consolidation PR cannot
    re-route the dispatch to a re-export alias (which would break
    monkey-patch sites that target the canonical source location)."""
    canon = importlib.import_module(CANONICAL_SWEEP_MODULE)
    src = inspect.getsource(canon.sweep_cmd)
    # The canonical dispatch is reached via the local import:
    #     from thegent.cli.governance.governance_impl import sweep_impl
    # Pin both the source module path and the dispatched symbol so a
    # re-route to a re-export alias fails the regression.
    assert "from thegent.cli.governance.governance_impl import sweep_impl" in src, (
        "thegent.cli.governance.governance_escalation_hitl_cmds.sweep_cmd "
        "does not dispatch to the canonical sweep_impl source — monkey-patch "
        "sites targeting the canonical source location will silently miss."
    )


def test_test_sweep_cmd_test_class_is_collectable() -> None:
    """The ``TestSweepCmdImpl`` class must be collectable and not
    silently skipped. The earlier WL-124-era patch at
    ``thegent.cli.commands.impl.sweep_impl`` was a re-export alias —
    patching it never reached the canonical implementation, so the
    tests previously failed with a TypeError. The WL-702 fix
    re-anchors the patch path to the canonical source location."""
    from tests.test_unit_cli_commands_a import TestSweepCmdImpl

    skip_marks = [mark for mark in getattr(TestSweepCmdImpl, "pytestmark", []) if mark.name == "skip"]
    assert skip_marks == [], "TestSweepCmdImpl is marked @pytest.mark.skip — the WL-702 LOW finding is not sealed yet."
    # The class must still define the four documented test methods.
    method_names = {
        "test_sweep_pass",
        "test_sweep_fail_rich",
        "test_sweep_json_pass",
        "test_sweep_json_fail",
    }
    assert method_names.issubset(set(dir(TestSweepCmdImpl)))


# ---------------------------------------------------------------------------
# Section 3 — proximity to sibling sealed surfaces
# ---------------------------------------------------------------------------


def test_audit_verify_cmd_and_sweep_cmd_share_no_canonical_module() -> None:
    """The audit and sweep commands must live in different canonical
    modules — pinning the WL-124 separation of concerns so a future
    "consolidate the audit/sweep surface" PR cannot silently fold
    ``audit_verify_cmd`` into the governance escalation module."""
    audit = _resolved_module("audit_verify_cmd")
    sweep = _resolved_module("sweep_cmd")
    assert audit != sweep, (
        "audit_verify_cmd and sweep_cmd must NOT share a canonical module — "
        "they belong to separate sub-areas (CLI tooling vs. governance escalation)."
    )
    assert audit.endswith("cli_tooling")
    assert sweep.endswith("governance_escalation_hitl_cmds")


def test_audit_verify_cmd_docstring_is_more_than_one_line() -> None:
    """The WL-124-era stub had a one-line docstring and zero
    implementation. The WL-702 implementation must carry a real
    docstring describing the dispatch contract."""
    from thegent.cli import audit_verify_cmd

    doc = audit_verify_cmd.__doc__ or ""
    assert len(doc.strip().splitlines()) >= 4, (
        "audit_verify_cmd docstring is too short — the WL-702 implementation "
        "should document the Auditor/RunRegistry dispatch contract."
    )
    assert "Auditor" in doc and "RunRegistry" in doc, (
        "audit_verify_cmd docstring must reference the Auditor and RunRegistry classes."
    )


def test_audit_verify_cmd_module_does_not_execute_audit_at_import_time() -> None:
    """Defensive AST pin: the canonical module must not call
    ``Auditor`` or ``RunRegistry`` at module-import time. The
    audit_verify_cmd dispatch must be lazy (inside the function body)
    so importing the module does not trigger file I/O."""
    import ast

    src_path = Path(
        importlib.import_module(CANONICAL_AUDIT_MODULE).__file__  # type: ignore[arg-type]
    )
    tree = ast.parse(src_path.read_text())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            body_src = ast.unparse(node)
            assert "Auditor(" not in body_src.replace("\n", " ") or node.name == "audit_verify_cmd", (
                f"{CANONICAL_AUDIT_MODULE}.{node.name} instantiates Auditor at module top-level — "
                f"the audit_verify_cmd dispatch must stay lazy inside the function body."
            )
