"""Tests for LintingAccelerator (oxlint / ESLint / ruff wrapper).

# @trace FR-UX-011

Uses unittest.mock to stub shutil.which and subprocess.run so no actual
linter binaries are required.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from thegent.tools.linting_accelerator import LintingAccelerator, LintResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _completed(stdout: str = "", returncode: int = 0) -> MagicMock:
    """Return a mock CompletedProcess-like object.

    Args:
        stdout:     Simulated stdout text.
        returncode: Simulated process return code.

    Returns:
        MagicMock shaped like subprocess.CompletedProcess.
    """
    proc = MagicMock()
    proc.stdout = stdout
    proc.returncode = returncode
    return proc


# ---------------------------------------------------------------------------
# LintResult model
# ---------------------------------------------------------------------------


class TestLintResult:
    def test_str_representation(self) -> None:
        r = LintResult(
            file="src/foo.ts",
            line=10,
            column=3,
            severity="error",
            rule="no-var",
            message="Unexpected var",
            source="oxlint",
        )
        assert str(r) == "src/foo.ts:10:3 [error] no-var: Unexpected var"

    def test_default_source(self) -> None:
        r = LintResult(file="a.py", line=1, column=1, severity="warning", rule="W0001", message="msg")
        assert r.source == "unknown"

    def test_warning_severity(self) -> None:
        r = LintResult(file="b.ts", line=2, column=4, severity="warning", rule="no-console", message="x")
        assert r.severity == "warning"
        assert "warning" in str(r)


# ---------------------------------------------------------------------------
# is_oxlint_available
# ---------------------------------------------------------------------------


class TestIsOxlintAvailable:
    def test_returns_true_when_found(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/usr/local/bin/oxlint"):
            assert acc.is_oxlint_available() is True

    def test_returns_false_when_not_found(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value=None):
            assert acc.is_oxlint_available() is False


# ---------------------------------------------------------------------------
# is_eslint_available / is_ruff_available
# ---------------------------------------------------------------------------


class TestIsEslintAvailable:
    def test_true_when_found(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/usr/local/bin/eslint"):
            assert acc.is_eslint_available() is True

    def test_false_when_missing(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value=None):
            assert acc.is_eslint_available() is False


class TestIsRuffAvailable:
    def test_true_when_found(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/usr/bin/ruff"):
            assert acc.is_ruff_available() is True

    def test_false_when_missing(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value=None):
            assert acc.is_ruff_available() is False


# ---------------------------------------------------------------------------
# run_oxlint
# ---------------------------------------------------------------------------


class TestRunOxlint:
    def test_raises_when_not_available(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value=None):
            with pytest.raises(FileNotFoundError, match="oxlint not found"):
                acc.run_oxlint([Path("src/")])

    def test_empty_output_returns_empty_list(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/oxlint"):
            with patch("subprocess.run", return_value=_completed("")):
                assert acc.run_oxlint([Path("src/")]) == []

    def test_parses_eslint_compat_format(self) -> None:
        payload = json.dumps(
            [
                {
                    "filePath": "src/app.ts",
                    "messages": [
                        {"severity": 2, "ruleId": "no-var", "line": 5, "column": 1, "message": "Use let"},
                        {"severity": 1, "ruleId": "no-console", "line": 8, "column": 3, "message": "No console"},
                    ],
                }
            ]
        )
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/oxlint"):
            with patch("subprocess.run", return_value=_completed(payload)):
                results = acc.run_oxlint([Path("src/")])

        assert len(results) == 2
        assert results[0].file == "src/app.ts"
        assert results[0].line == 5
        assert results[0].severity == "error"
        assert results[0].rule == "no-var"
        assert results[0].source == "oxlint"
        assert results[1].severity == "warning"
        assert results[1].rule == "no-console"

    def test_parses_flat_diagnostic_format(self) -> None:
        payload = json.dumps(
            [{"filename": "main.ts", "severity": 2, "rule": "eqeqeq", "line": 12, "column": 4, "message": "==="}]
        )
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/oxlint"):
            with patch("subprocess.run", return_value=_completed(payload)):
                results = acc.run_oxlint([Path("main.ts")])

        assert len(results) == 1
        assert results[0].file == "main.ts"
        assert results[0].rule == "eqeqeq"

    def test_invalid_json_raises_value_error(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/oxlint"):
            with patch("subprocess.run", return_value=_completed("not-json")):
                with pytest.raises(ValueError, match="invalid JSON"):
                    acc.run_oxlint([Path()])

    def test_non_array_json_raises_value_error(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/oxlint"):
            with patch("subprocess.run", return_value=_completed('{"key": "value"}')):
                with pytest.raises(ValueError, match="Expected JSON array"):
                    acc.run_oxlint([Path()])

    def test_passes_config_flag(self) -> None:
        acc = LintingAccelerator()
        calls: list[list[str]] = []

        def mock_run(cmd: list[str], **kwargs: object) -> MagicMock:
            calls.append(cmd)
            return _completed("[]")

        with patch("shutil.which", return_value="/bin/oxlint"):
            with patch("subprocess.run", side_effect=mock_run):
                acc.run_oxlint([Path("src/")], config=Path("my-oxlintrc.json"))

        assert "--config" in calls[0]
        assert "my-oxlintrc.json" in calls[0]

    def test_non_dict_items_are_skipped(self) -> None:
        payload = json.dumps(["not-a-dict", None, 42])
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/oxlint"):
            with patch("subprocess.run", return_value=_completed(payload)):
                results = acc.run_oxlint([Path()])
        assert results == []

    def test_default_severity_is_error(self) -> None:
        """When severity field is absent, default to error (code 2)."""
        payload = json.dumps(
            [
                {
                    "filePath": "a.ts",
                    "messages": [
                        {"ruleId": "some-rule", "line": 1, "column": 1, "message": "bad"},
                    ],
                }
            ]
        )
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/oxlint"):
            with patch("subprocess.run", return_value=_completed(payload)):
                results = acc.run_oxlint([Path("a.ts")])
        assert results[0].severity == "error"


# ---------------------------------------------------------------------------
# run_eslint
# ---------------------------------------------------------------------------


class TestRunEslint:
    def test_raises_when_not_available(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value=None):
            with pytest.raises(FileNotFoundError, match="eslint not found"):
                acc.run_eslint([Path("src/")])

    def test_empty_output_returns_empty_list(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/eslint"):
            with patch("subprocess.run", return_value=_completed("")):
                assert acc.run_eslint([Path()]) == []

    def test_parses_standard_eslint_json(self) -> None:
        payload = json.dumps(
            [
                {
                    "filePath": "web/index.js",
                    "messages": [
                        {"severity": 2, "ruleId": "no-unused-vars", "line": 3, "column": 7, "message": "unused"},
                    ],
                }
            ]
        )
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/eslint"):
            with patch("subprocess.run", return_value=_completed(payload)):
                results = acc.run_eslint([Path("web/")])

        assert len(results) == 1
        assert results[0].source == "eslint"
        assert results[0].file == "web/index.js"
        assert results[0].severity == "error"

    def test_null_rule_id_becomes_unknown(self) -> None:
        payload = json.dumps(
            [
                {
                    "filePath": "app.ts",
                    "messages": [
                        {"severity": 1, "ruleId": None, "line": 1, "column": 1, "message": "parse error"},
                    ],
                }
            ]
        )
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/eslint"):
            with patch("subprocess.run", return_value=_completed(payload)):
                results = acc.run_eslint([Path("app.ts")])

        assert results[0].rule == "unknown"
        assert results[0].severity == "warning"

    def test_invalid_json_raises_value_error(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/eslint"):
            with patch("subprocess.run", return_value=_completed("{bad")):
                with pytest.raises(ValueError, match="invalid JSON"):
                    acc.run_eslint([Path()])

    def test_non_array_json_raises_value_error(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/eslint"):
            with patch("subprocess.run", return_value=_completed('{"a": 1}')):
                with pytest.raises(ValueError, match="Expected JSON array"):
                    acc.run_eslint([Path()])


# ---------------------------------------------------------------------------
# run_ruff
# ---------------------------------------------------------------------------


class TestRunRuff:
    def test_raises_when_not_available(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value=None):
            with pytest.raises(FileNotFoundError, match="ruff not found"):
                acc.run_ruff([Path("src/")])

    def test_empty_output_returns_empty_list(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/ruff"):
            with patch("subprocess.run", return_value=_completed("")):
                assert acc.run_ruff([Path()]) == []

    def test_parses_ruff_json_unfixable_is_error(self) -> None:
        payload = json.dumps(
            [
                {
                    "filename": "src/foo.py",
                    "location": {"row": 10, "column": 5},
                    "end_location": {"row": 10, "column": 8},
                    "code": "E501",
                    "message": "Line too long",
                    "fix": None,
                }
            ]
        )
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/ruff"):
            with patch("subprocess.run", return_value=_completed(payload)):
                results = acc.run_ruff([Path("src/")])

        assert len(results) == 1
        assert results[0].source == "ruff"
        assert results[0].file == "src/foo.py"
        assert results[0].line == 10
        assert results[0].column == 5
        assert results[0].rule == "E501"
        assert results[0].severity == "error"

    def test_parses_ruff_json_fixable_is_warning(self) -> None:
        payload = json.dumps(
            [
                {
                    "filename": "src/bar.py",
                    "location": {"row": 3, "column": 1},
                    "end_location": {"row": 3, "column": 6},
                    "code": "F401",
                    "message": "unused import",
                    "fix": {"message": "Remove unused import", "edits": []},
                }
            ]
        )
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/ruff"):
            with patch("subprocess.run", return_value=_completed(payload)):
                results = acc.run_ruff([Path("src/")])

        assert results[0].severity == "warning"
        assert results[0].rule == "F401"

    def test_invalid_json_raises_value_error(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/ruff"):
            with patch("subprocess.run", return_value=_completed("garbage")):
                with pytest.raises(ValueError, match="invalid JSON"):
                    acc.run_ruff([Path()])

    def test_non_array_json_raises_value_error(self) -> None:
        acc = LintingAccelerator()
        with patch("shutil.which", return_value="/bin/ruff"):
            with patch("subprocess.run", return_value=_completed('{"a": 1}')):
                with pytest.raises(ValueError, match="Expected JSON array"):
                    acc.run_ruff([Path()])


# ---------------------------------------------------------------------------
# lint() -- unified entry point
# ---------------------------------------------------------------------------


class TestLintUnified:
    """Tests for the high-level lint() entry point."""

    def test_fast_mode_uses_oxlint_when_available(self) -> None:
        acc = LintingAccelerator()
        called: list[str] = []

        with patch.object(acc, "is_oxlint_available", return_value=True):
            with patch.object(acc, "run_oxlint", side_effect=lambda p, config=None: called.append("oxlint") or []):
                with patch.object(acc, "run_eslint", side_effect=lambda p, config=None: called.append("eslint") or []):
                    acc.lint([Path()], fast=True)

        assert called == ["oxlint"]

    def test_fast_mode_falls_back_to_eslint_when_oxlint_missing(self) -> None:
        acc = LintingAccelerator()
        called: list[str] = []

        with patch.object(acc, "is_oxlint_available", return_value=False):
            with patch.object(acc, "is_eslint_available", return_value=True):
                with patch.object(acc, "run_eslint", side_effect=lambda p, config=None: called.append("eslint") or []):
                    acc.lint([Path()], fast=True)

        assert called == ["eslint"]

    def test_no_fast_always_uses_eslint(self) -> None:
        acc = LintingAccelerator()
        called: list[str] = []

        with patch.object(acc, "is_oxlint_available", return_value=True):
            with patch.object(acc, "is_eslint_available", return_value=True):
                with patch.object(acc, "run_oxlint", side_effect=lambda p, config=None: called.append("oxlint") or []):
                    with patch.object(
                        acc, "run_eslint", side_effect=lambda p, config=None: called.append("eslint") or []
                    ):
                        acc.lint([Path()], fast=False)

        assert called == ["eslint"]

    def test_returns_empty_when_neither_available(self) -> None:
        acc = LintingAccelerator()
        with patch.object(acc, "is_oxlint_available", return_value=False):
            with patch.object(acc, "is_eslint_available", return_value=False):
                results = acc.lint([Path()], fast=True)
        assert results == []

    def test_passes_oxlint_config_through(self) -> None:
        acc = LintingAccelerator()
        captured: list[Path | None] = []

        def fake_oxlint(paths: list[Path], config: Path | None = None) -> list[LintResult]:
            captured.append(config)
            return []

        with patch.object(acc, "is_oxlint_available", return_value=True):
            with patch.object(acc, "run_oxlint", side_effect=fake_oxlint):
                acc.lint([Path()], fast=True, oxlint_config=Path("my.json"))

        assert captured == [Path("my.json")]

    def test_passes_eslint_config_through(self) -> None:
        acc = LintingAccelerator()
        captured: list[Path | None] = []

        def fake_eslint(paths: list[Path], config: Path | None = None) -> list[LintResult]:
            captured.append(config)
            return []

        with patch.object(acc, "is_oxlint_available", return_value=False):
            with patch.object(acc, "is_eslint_available", return_value=True):
                with patch.object(acc, "run_eslint", side_effect=fake_eslint):
                    acc.lint([Path()], fast=True, eslint_config=Path("eslint.config.js"))

        assert captured == [Path("eslint.config.js")]

    def test_lint_returns_results_from_oxlint(self) -> None:
        acc = LintingAccelerator()
        expected = [
            LintResult(file="a.ts", line=1, column=1, severity="error", rule="no-var", message="x", source="oxlint")
        ]

        with patch.object(acc, "is_oxlint_available", return_value=True):
            with patch.object(acc, "run_oxlint", return_value=expected):
                results = acc.lint([Path()], fast=True)

        assert results == expected

    def test_lint_no_fast_returns_empty_when_eslint_missing(self) -> None:
        acc = LintingAccelerator()
        with patch.object(acc, "is_oxlint_available", return_value=True):
            with patch.object(acc, "is_eslint_available", return_value=False):
                results = acc.lint([Path()], fast=False)
        assert results == []
