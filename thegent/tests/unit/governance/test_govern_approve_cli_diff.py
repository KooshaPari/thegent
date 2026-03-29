"""Tests for WL-100 govern approve diff preview UX."""

from __future__ import annotations

from typer.testing import CliRunner

from thegent.cli.apps.govern import app

runner = CliRunner()


def test_govern_approve_displays_diff_before_approval(monkeypatch) -> None:
    """WL-100: govern approve prints diff summary and diff content."""
    calls: dict[str, str | None] = {}

    def _pending(*, run_id: str, session: str | None = None):
        assert run_id == "run_001"
        return {
            "run_id": run_id,
            "unified_diff": "--- a/foo.py\n+++ b/foo.py\n@@ -1 +1 @@\n-old\n+new\n",
        }

    def _approve(*, run_id: str, reason: str | None = None):
        calls["run_id"] = run_id
        calls["reason"] = reason
        return {"run_id": run_id}

    monkeypatch.setattr("thegent.cli.services.governance.govern_get_pending_approval_impl", _pending)
    monkeypatch.setattr("thegent.cli.commands.impl.govern_approve_impl", _approve)

    result = runner.invoke(app, ["approve", "run_001", "--reason", "approved"])

    assert result.exit_code == 0
    assert "Review Diff:" in result.stdout
    assert "+1 -1 lines" in result.stdout
    assert "+++ b/foo.py" in result.stdout
    assert "Approved: run_001" in result.stdout
    assert calls == {"run_id": "run_001", "reason": "approved"}


def test_govern_approve_handles_missing_diff(monkeypatch) -> None:
    """WL-100: govern approve still works when no diff is present."""

    def _pending(*, run_id: str, session: str | None = None):
        return {"run_id": run_id, "unified_diff": ""}

    def _approve(*, run_id: str, reason: str | None = None):
        return {"run_id": run_id}

    monkeypatch.setattr("thegent.cli.services.governance.govern_get_pending_approval_impl", _pending)
    monkeypatch.setattr("thegent.cli.commands.impl.govern_approve_impl", _approve)

    result = runner.invoke(app, ["approve", "run_002", "--reason", "ok"])

    assert result.exit_code == 0
    assert "No unified diff available for this approval request." in result.stdout
    assert "Approved: run_002" in result.stdout
