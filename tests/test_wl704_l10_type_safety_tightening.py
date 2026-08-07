"""WL-704 hardening: L10 type-safety tightening for WL702/WL703 surfaces.

WL-703 left L10 type-safety tightening as the final Phase 3/4 hardening
candidate. This suite pins the canonical type guarantees so future
``Any``-drift on the WL-155 / WL-156 / WL-702 / WL-703 surfaces is caught
at type-check / mypy time rather than only at runtime:

1. **TypedDict-backed canonical shapes.**
   * :class:`thegent.cli.commands.model_cmds_rules.CliproxyLoginResult`
     replaces the prior ``dict[str, Any]`` annotation of
     :func:`thegent.cli.commands.model_cmds_rules._run_cliproxyctl_machine_command`.
     ``total=True`` enforces both keys at construction.
   * :class:`thegent.cli.commands.cli_tooling._VerifyReport` documents
     the canonical ``Auditor.verify_registry()`` payload shape and the
     :func:`thegent.cli.commands.cli_tooling._extract_verify_report`
     helper absorbs the loose ``str(...)`` / ``int(...)`` / ``list(...)``
     coercions so :func:`audit_verify_cmd` operates on typed locals.

2. **Tightened settings annotations.** The ``settings: Any`` slots in
   ``thegent.cli.commands.session_meta_impl`` become
   ``ThegentSettings`` (the canonical settings type).

3. **WL-124 vocabulary parity preserved.** The ``*args: Any, **kwargs: Any``
   signatures on the surrounding stub commands (``benchmark_cmd``,
   ``deep_research_cmd``, ``drift_monitor_cmd``, ``roadmap_cmd``,
   ``audit_verify_cmd``) are intentionally **kept** -- they are the
   WL-124 vocabulary parity surface for stable-import re-export. Only
   the **inner locals** of ``audit_verify_cmd`` are typed.
"""

from __future__ import annotations

import importlib
import inspect
import typing
from pathlib import Path
from typing import get_type_hints
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# CliproxyLoginResult TypedDict
# ---------------------------------------------------------------------------


def test_cliproxy_login_result_typed_dict_exists() -> None:
    """``CliproxyLoginResult`` is a TypedDict at the canonical module path."""
    from thegent.cli.commands.model_cmds_rules import CliproxyLoginResult

    assert isinstance(CliproxyLoginResult, typing._TypedDictMeta) or (hasattr(CliproxyLoginResult, "__total__"))


def test_cliproxy_login_result_total_is_true() -> None:
    """``total=True`` so both keys are required at construction time."""
    from thegent.cli.commands.model_cmds_rules import CliproxyLoginResult

    # TypedDict.__total__ is True when total=True was passed at creation.
    assert getattr(CliproxyLoginResult, "__total__", None) is True


def test_cliproxy_login_result_field_annotations() -> None:
    """``exit_code: int`` and ``message: str`` annotations are pinned."""
    from thegent.cli.commands.model_cmds_rules import CliproxyLoginResult

    hints = get_type_hints(CliproxyLoginResult)
    assert hints["exit_code"] is int
    assert hints["message"] is str


def test_cliproxy_login_result_required_keys_pinned() -> None:
    """``__required_keys__`` is the full key set under ``total=True``.

    TypedDict's ``total=True`` is enforced statically (mypy/pyright) and
    exposed at runtime via ``__required_keys__``. This test pins the
    canonical required-key set so future drift (e.g. dropping ``total=True``
    or removing a key) is caught by pytest rather than only at type-check.
    """
    from thegent.cli.commands.model_cmds_rules import CliproxyLoginResult

    assert frozenset(CliproxyLoginResult.__required_keys__) == frozenset({"exit_code", "message"})
    assert frozenset(CliproxyLoginResult.__optional_keys__) == frozenset()


def test_cliproxy_login_result_in_module_all() -> None:
    """``CliproxyLoginResult`` is exported via ``__all__``."""
    mod = importlib.import_module("thegent.cli.commands.model_cmds_rules")
    assert "CliproxyLoginResult" in mod.__all__


# ---------------------------------------------------------------------------
# _run_cliproxyctl_machine_command
# ---------------------------------------------------------------------------


def test_run_cliproxyctl_machine_command_settings_annotation() -> None:
    """``settings`` annotation is ``ThegentSettings | None`` (not ``Any``)."""
    from thegent.cli.commands.model_cmds_rules import _run_cliproxyctl_machine_command

    sig = inspect.signature(_run_cliproxyctl_machine_command)
    hints = get_type_hints(_run_cliproxyctl_machine_command)
    # The ``settings`` param must be annotated (no longer ``Any``).
    assert "settings" in hints
    settings_hint = hints["settings"]
    # The annotation must NOT be ``Any`` -- it's ``ThegentSettings | None``.
    assert settings_hint is not typing.Any
    # Verify it's a Union-like of ThegentSettings | None (string repr check
    # since Union evaluation depends on `from __future__ import annotations`).
    assert "ThegentSettings" in str(settings_hint)
    assert "None" in str(settings_hint)


def test_run_cliproxyctl_machine_command_return_annotation() -> None:
    """Return annotation is ``CliproxyLoginResult`` (no longer ``dict[str, Any]``).

    Uses :func:`typing.get_type_hints` so the ``from __future__ import
    annotations`` string-vs-class mismatch is bypassed -- ``get_type_hints``
    resolves the string annotation against the module's runtime namespace
    and returns the actual ``CliproxyLoginResult`` class object.
    """
    from thegent.cli.commands.model_cmds_rules import (
        CliproxyLoginResult,
        _run_cliproxyctl_machine_command,
    )

    hints = get_type_hints(_run_cliproxyctl_machine_command)
    assert hints["return"] is CliproxyLoginResult


def test_run_cliproxyctl_machine_command_accepts_none_settings() -> None:
    """``settings=None`` default path still works (no constructor invocation)."""
    from thegent.cli.commands.model_cmds_rules import _run_cliproxyctl_machine_command

    with patch(
        "thegent.use_cases.manage_cliproxy_login.run_login",
        return_value=0,
    ):
        result = _run_cliproxyctl_machine_command(provider="claude")
    assert result["exit_code"] == 0
    assert "claude" in result["message"]


def test_run_cliproxyctl_machine_command_accepts_settings_instance() -> None:
    """``ThegentSettings`` instance is accepted (parity with the tightened annotation)."""
    from thegent.cli.commands.model_cmds_rules import _run_cliproxyctl_machine_command
    from thegent.config.settings import ThegentSettings

    settings = ThegentSettings()
    with patch(
        "thegent.use_cases.manage_cliproxy_login.run_login",
        return_value=0,
    ):
        result = _run_cliproxyctl_machine_command(
            provider="codex",
            settings=settings,
        )
    assert result["exit_code"] == 0
    assert "codex" in result["message"]


def test_run_cliproxyctl_machine_command_returns_cliproxy_login_result() -> None:
    """Runtime return shape is dict-compatible (TypedDict is a dict at runtime)."""
    from thegent.cli.commands.model_cmds_rules import _run_cliproxyctl_machine_command

    with patch(
        "thegent.use_cases.manage_cliproxy_login.run_login",
        return_value=1,
    ):
        result = _run_cliproxyctl_machine_command(provider="gemini")
    # TypedDict is a dict at runtime -- shape must remain canonical.
    assert isinstance(result, dict)
    assert result["exit_code"] == 1
    assert "gemini" in result["message"]


def test_run_cliproxyctl_machine_command_delegate_pin() -> None:
    """Helper still delegates to ``manage_cliproxy_login.run_login`` (regression)."""
    from thegent.cli.commands.model_cmds_rules import _run_cliproxyctl_machine_command

    with patch(
        "thegent.use_cases.manage_cliproxy_login.run_login",
        return_value=2,
    ) as mock_run_login:
        result = _run_cliproxyctl_machine_command(provider="claude")
    mock_run_login.assert_called_once()
    assert result["exit_code"] == 2


# ---------------------------------------------------------------------------
# audit_verify_cmd locals
# ---------------------------------------------------------------------------


def test_extract_verify_report_helper_exists() -> None:
    """``_extract_verify_report`` is exported from ``cli_tooling``."""
    mod = importlib.import_module("thegent.cli.commands.cli_tooling")
    assert hasattr(mod, "_extract_verify_report")
    assert "_extract_verify_report" in mod.__all__


def test_extract_verify_report_signature() -> None:
    """``_extract_verify_report(report) -> (str, int, int, list[str])`` typed locals.

    Uses :func:`typing.get_type_hints` to bypass ``from __future__ import
    annotations`` and resolve the string annotations against the module's
    runtime namespace.
    """
    from thegent.cli.commands.cli_tooling import _extract_verify_report

    hints = get_type_hints(_extract_verify_report)
    assert hints["report"] == dict[str, object]
    assert hints["return"] == tuple[str, int, int, list[str]]


def test_extract_verify_report_coerces_string_int_list() -> None:
    """``str(...)``, ``int(...)``, ``list(...)`` coercions produce typed locals."""
    from thegent.cli.commands.cli_tooling import _extract_verify_report

    status, valid, corrupt, issues = _extract_verify_report(
        {
            "status": "passed",
            "valid_count": 7,
            "corrupt_count": 0,
            "issues": [],
        }
    )
    assert status == "passed"
    assert valid == 7
    assert corrupt == 0
    assert issues == []


def test_extract_verify_report_defaults_when_keys_missing() -> None:
    """Missing keys default to safe sentinels (``"failed"``, ``0``, ``0``, ``[]``)."""
    from thegent.cli.commands.cli_tooling import _extract_verify_report

    status, valid, corrupt, issues = _extract_verify_report({})
    assert status == "failed"
    assert valid == 0
    assert corrupt == 0
    assert issues == []


def test_extract_verify_report_handles_non_int_counts() -> None:
    """``valid_count`` / ``corrupt_count`` coerce defensively (string → int)."""
    from thegent.cli.commands.cli_tooling import _extract_verify_report

    status, valid, corrupt, issues = _extract_verify_report(
        {"status": "failed", "valid_count": "5", "corrupt_count": "2", "issues": ["a", "b"]}
    )
    assert status == "failed"
    assert valid == 5
    assert corrupt == 2
    assert issues == ["a", "b"]


def test_extract_verify_report_handles_non_list_issues() -> None:
    """``issues`` coerces to ``[]`` when not a list (defensive default)."""
    from thegent.cli.commands.cli_tooling import _extract_verify_report

    _status, _valid, _corrupt, issues = _extract_verify_report({"status": "failed", "issues": "not a list"})
    assert issues == []


def test_audit_verify_cmd_locals_are_typed() -> None:
    """``audit_verify_cmd`` body uses typed locals (no ``Any`` in source)."""
    import ast

    src = Path("src/thegent/cli/commands/cli_tooling.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    audit_fn = next(
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "audit_verify_cmd"
    )
    # The function must contain typed local annotations for the canonical locals.
    annotated_names = {
        ann.target.id  # type: ignore[union-attr]
        for ann in ast.walk(audit_fn)
        if isinstance(ann, ast.AnnAssign) and isinstance(ann.target, ast.Name)
    }
    # The 5 typed locals introduced by WL-704:
    for required in ("status", "valid_count", "corrupt_count", "issues", "fmt"):
        assert required in annotated_names, f"audit_verify_cmd missing typed annotation for local {required!r}"


def test_audit_verify_cmd_uses_extract_helper() -> None:
    """``audit_verify_cmd`` body calls ``_extract_verify_report`` (delegate pin)."""
    import ast

    src = Path("src/thegent/cli/commands/cli_tooling.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    audit_fn = next(
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "audit_verify_cmd"
    )
    # _extract_verify_report must be invoked at least once inside audit_verify_cmd.
    calls = [
        node
        for node in ast.walk(audit_fn)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_extract_verify_report"
    ]
    assert len(calls) >= 1


def test_audit_verify_cmd_dispatches_to_run_registry_and_auditor() -> None:
    """Regression pin: ``audit_verify_cmd`` still resolves via the canonical classes.

    Mirrors the four ``*_cmd`` tests in
    ``tests/test_unit_cli_commands_a.py::TestAuditVerifyCmdImpl`` which mock
    at the canonical patch sites (``thegent.cli.ThegentSettings``,
    ``thegent.execution.RunRegistry``, ``thegent.execution.Auditor``) and
    the ``_get_console`` helper at ``thegent.cli.commands.cli_tooling``.
    """
    from thegent.cli.commands.cli_tooling import _extract_verify_report
    from thegent.cli.commands.cli_tooling import audit_verify_cmd

    mock_auditor = MagicMock()
    mock_auditor.verify_registry.return_value = {
        "status": "passed",
        "valid_count": 3,
        "corrupt_count": 0,
        "issues": [],
    }
    mock_registry_instance = MagicMock()
    mock_registry_instance.registry_path = Path("/tmp/wl704-registry")
    mock_console = MagicMock()

    with (
        patch("thegent.cli.ThegentSettings") as mock_settings_cls,
        patch("thegent.execution.RunRegistry", return_value=mock_registry_instance) as mock_run_registry,
        patch("thegent.execution.Auditor", return_value=mock_auditor) as mock_auditor_cls,
        patch(
            "thegent.cli.commands.cli_tooling._get_console",
            return_value=mock_console,
        ),
    ):
        # Pin the extractor still routes through _extract_verify_report.
        with patch(
            "thegent.cli.commands.cli_tooling._extract_verify_report",
            side_effect=_extract_verify_report,
        ) as mock_extract:
            rc = audit_verify_cmd(format="rich")

    # Verify the canonical dispatch chain executed exactly once.
    mock_settings_cls.assert_called_once()
    mock_run_registry.assert_called_once()
    mock_auditor_cls.assert_called_once()
    mock_auditor.verify_registry.assert_called_once()
    mock_extract.assert_called_once()

    # "passed" status → exit 0 (parity with the canonical contract).
    assert rc == 0
    printed = " ".join(str(c) for c in mock_console.print.call_args_list)
    assert "passed" in printed.lower()
    assert "3" in printed


# ---------------------------------------------------------------------------
# session_meta_impl settings tightening
# ---------------------------------------------------------------------------


def test_session_meta_impl_load_settings_annotation() -> None:
    """``_load_prior_session_output`` annotation is ``ThegentSettings`` (not ``Any``)."""
    from thegent.cli.commands.session_meta_impl import _load_prior_session_output

    hints = get_type_hints(_load_prior_session_output)
    assert "settings" in hints
    settings_hint = hints["settings"]
    assert settings_hint is not typing.Any
    assert "ThegentSettings" in str(settings_hint)


def test_session_meta_impl_build_settings_annotation() -> None:
    """``_build_continuation_prompt`` annotation is ``ThegentSettings`` (not ``Any``)."""
    from thegent.cli.commands.session_meta_impl import _build_continuation_prompt

    hints = get_type_hints(_build_continuation_prompt)
    assert "settings" in hints
    settings_hint = hints["settings"]
    assert settings_hint is not typing.Any
    assert "ThegentSettings" in str(settings_hint)


def test_session_meta_impl_accepts_thegent_settings_instance(tmp_path: Path) -> None:
    """``_build_continuation_prompt`` accepts a real ``ThegentSettings`` instance.

    ``session_dir`` is a Pydantic ``Field`` so it cannot be patched via
    :func:`unittest.mock.patch.object` on the class (the attribute does not
    exist on the class -- it is set per-instance by Pydantic). Instead we
    pre-set the attribute on the instance so the helper's
    ``getattr(settings, "session_dir", None)`` resolves to ``tmp_path``,
    then assert the prompt body matches ``prompt`` unchanged (no prior
    sessions → no blocks appended).
    """
    from thegent.cli.commands.session_meta_impl import _build_continuation_prompt
    from thegent.config.settings import ThegentSettings

    settings = ThegentSettings()
    # Pre-set session_dir on the instance so the test does not depend on
    # the resolved config path. ``_build_continuation_prompt`` reads it
    # via ``getattr(settings, "session_dir", None)``.
    settings.session_dir = tmp_path
    result = _build_continuation_prompt(
        settings,
        "nonexistent-session",
        "hello world",
        include_stderr=False,
    )
    # No prior output → prompt is returned unchanged.
    assert result == "hello world"


def test_session_meta_impl_load_accepts_thegent_settings_instance(tmp_path: Path) -> None:
    """``_load_prior_session_output`` accepts a real ``ThegentSettings`` instance.

    Mirrors the ``session_dir`` attribute pattern from
    ``test_session_meta_impl_accepts_thegent_settings_instance`` (Pydantic
    fields are per-instance, not patchable on the class).
    """
    from thegent.cli.commands.session_meta_impl import _load_prior_session_output
    from thegent.config.settings import ThegentSettings

    settings = ThegentSettings()
    settings.session_dir = tmp_path
    result = _load_prior_session_output(settings, "nonexistent-session")
    # No stdout.log → empty string.
    assert result == ""
