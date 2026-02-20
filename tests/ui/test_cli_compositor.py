"""Tests for CliCompositor — CLI progress bars + status panels.

Covers (FR-UI-CLICOMP-*):
- ProgressPanel: advance, complete, render              (FR-UI-CLICOMP-001..003)
- StatusPanel: render, error boundary                   (FR-UI-CLICOMP-004..005)
- CliCompositor.add_progress: creates + replaces panels (FR-UI-CLICOMP-006)
- CliCompositor.update_progress: advances, new desc     (FR-UI-CLICOMP-007)
- CliCompositor.complete_progress: marks done           (FR-UI-CLICOMP-008)
- CliCompositor.remove_progress: removes panel          (FR-UI-CLICOMP-009)
- CliCompositor.add_status_line: adds + replaces        (FR-UI-CLICOMP-010)
- CliCompositor.remove_status_line: removes panel       (FR-UI-CLICOMP-011)
- CliCompositor.render: returns Table                   (FR-UI-CLICOMP-012)
- CliCompositor.__contains__: membership check          (FR-UI-CLICOMP-013)
- CliCompositor.__len__: counts all panels              (FR-UI-CLICOMP-014)
- CliCompositor.progress_panel_names                    (FR-UI-CLICOMP-015)
- CliCompositor.status_panel_names                      (FR-UI-CLICOMP-016)
- CliCompositor context manager                         (FR-UI-CLICOMP-017)
- update_progress KeyError on missing name              (FR-UI-CLICOMP-018)
- complete_progress KeyError on missing name            (FR-UI-CLICOMP-019)
- make_cli_compositor factory                           (FR-UI-CLICOMP-020)
- Compositor lifecycle hooks wired to progress panels   (FR-UI-CLICOMP-021)
- StatusPanel error boundary does not propagate         (FR-UI-CLICOMP-022)
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from thegent.ui.cli_compositor import (
    CliCompositor,
    ProgressPanel,
    StatusPanel,
    make_cli_compositor,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _headless_compositor(**kwargs: object) -> CliCompositor:
    """Create a CliCompositor that uses a no-markup console (safe for tests)."""
    console = Console(no_color=True, highlight=False, markup=False)
    return CliCompositor(console=console, **kwargs)


# ---------------------------------------------------------------------------
# ProgressPanel tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_progress_panel_advance_increments_progress() -> None:
    """advance() updates the rich task by the given amount.

    # @trace FR-UI-CLICOMP-001
    """
    progress = Progress()
    progress.start()
    task_id = progress.add_task("doing stuff", total=10)
    pp = ProgressPanel(name="pp", task_id=task_id, progress=progress)

    pp.advance(3)

    task = progress.tasks[task_id]
    assert task.completed == 3
    progress.stop()


@pytest.mark.unit
def test_progress_panel_advance_updates_description() -> None:
    """advance() with description changes the displayed description.

    # @trace FR-UI-CLICOMP-001
    """
    progress = Progress()
    progress.start()
    task_id = progress.add_task("original", total=10)
    pp = ProgressPanel(name="pp", task_id=task_id, progress=progress)

    pp.advance(1, description="updated desc")

    task = progress.tasks[task_id]
    assert task.description == "updated desc"
    progress.stop()


@pytest.mark.unit
def test_progress_panel_complete_fills_to_total() -> None:
    """complete() advances the task to 100% and stops it.

    # @trace FR-UI-CLICOMP-002
    """
    progress = Progress()
    progress.start()
    task_id = progress.add_task("work", total=50)
    pp = ProgressPanel(name="pp", task_id=task_id, progress=progress)

    pp.advance(10)
    pp.complete()

    task = progress.tasks[task_id]
    assert task.completed == 50
    assert task.finished
    progress.stop()


@pytest.mark.unit
def test_progress_panel_render_returns_string() -> None:
    """render() returns a non-empty string with key info.

    # @trace FR-UI-CLICOMP-003
    """
    progress = Progress()
    progress.start()
    task_id = progress.add_task("my task", total=20)
    pp = ProgressPanel(name="mypanel", task_id=task_id, progress=progress)

    pp.advance(5)
    rendered = pp.render()

    assert isinstance(rendered, str)
    assert "mypanel" in rendered
    assert "my task" in rendered
    progress.stop()


# ---------------------------------------------------------------------------
# StatusPanel tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_status_panel_render_calls_content_fn() -> None:
    """render() delegates to content_fn and returns its result.

    # @trace FR-UI-CLICOMP-004
    """
    content_fn = MagicMock(return_value="all good")
    sp = StatusPanel(name="health", content_fn=content_fn)

    result = sp.render()

    assert result == "all good"
    content_fn.assert_called_once()


@pytest.mark.unit
def test_status_panel_render_error_boundary() -> None:
    """render() catches content_fn exceptions and returns a fallback string.

    # @trace FR-UI-CLICOMP-005
    """

    def broken() -> str:
        raise RuntimeError("boom")

    sp = StatusPanel(name="broken_panel", content_fn=broken)

    result = sp.render()

    assert "broken_panel" in result
    assert "RuntimeError" in result


# ---------------------------------------------------------------------------
# CliCompositor.add_progress tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_add_progress_creates_panel() -> None:
    """add_progress() adds a ProgressPanel accessible by name.

    # @trace FR-UI-CLICOMP-006
    """
    comp = _headless_compositor()

    pp = comp.add_progress("download", total=100, description="Downloading")

    assert isinstance(pp, ProgressPanel)
    assert "download" in comp
    assert comp.progress_panel_names == ["download"]


@pytest.mark.unit
def test_add_progress_replaces_existing_panel() -> None:
    """add_progress() with same name replaces the old panel.

    # @trace FR-UI-CLICOMP-006
    """
    comp = _headless_compositor()

    comp.add_progress("step", total=10, description="step 1")
    pp2 = comp.add_progress("step", total=20, description="step 2")

    assert len(comp.progress_panel_names) == 1
    assert comp.progress_panel_names == ["step"]
    assert pp2.name == "step"


@pytest.mark.unit
def test_add_progress_wires_compositor_panel() -> None:
    """add_progress() registers a Panel with the underlying Compositor.

    # @trace FR-UI-CLICOMP-021
    """
    comp = _headless_compositor()

    comp.add_progress("alpha", total=5)

    assert "alpha" in comp._compositor


# ---------------------------------------------------------------------------
# CliCompositor.update_progress tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_update_progress_advances_panel() -> None:
    """update_progress() advances the named panel by the given amount.

    # @trace FR-UI-CLICOMP-007
    """
    comp = _headless_compositor()
    comp.add_progress("upload", total=100)

    comp.update_progress("upload", advance=42)

    task = comp._progress.tasks[comp._progress_panels["upload"].task_id]
    assert task.completed == 42


@pytest.mark.unit
def test_update_progress_changes_description() -> None:
    """update_progress() can update the description in the same call.

    # @trace FR-UI-CLICOMP-007
    """
    comp = _headless_compositor()
    comp.add_progress("upload", total=100, description="phase A")

    comp.update_progress("upload", advance=1, description="phase B")

    task = comp._progress.tasks[comp._progress_panels["upload"].task_id]
    assert task.description == "phase B"


@pytest.mark.unit
def test_update_progress_raises_on_missing_name() -> None:
    """update_progress() raises KeyError for an unknown panel name.

    # @trace FR-UI-CLICOMP-018
    """
    comp = _headless_compositor()

    with pytest.raises(KeyError, match="ghost"):
        comp.update_progress("ghost", advance=1)


# ---------------------------------------------------------------------------
# CliCompositor.complete_progress tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_complete_progress_fills_task() -> None:
    """complete_progress() advances the task to 100%.

    # @trace FR-UI-CLICOMP-008
    """
    comp = _headless_compositor()
    comp.add_progress("sync", total=50)
    comp.update_progress("sync", advance=10)

    comp.complete_progress("sync")

    task = comp._progress.tasks[comp._progress_panels["sync"].task_id]
    assert task.completed == 50


@pytest.mark.unit
def test_complete_progress_raises_on_missing_name() -> None:
    """complete_progress() raises KeyError for an unknown panel name.

    # @trace FR-UI-CLICOMP-019
    """
    comp = _headless_compositor()

    with pytest.raises(KeyError, match="nobody"):
        comp.complete_progress("nobody")


# ---------------------------------------------------------------------------
# CliCompositor.remove_progress tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_remove_progress_returns_true_on_success() -> None:
    """remove_progress() returns True when the panel exists.

    # @trace FR-UI-CLICOMP-009
    """
    comp = _headless_compositor()
    comp.add_progress("item", total=10)

    result = comp.remove_progress("item")

    assert result is True
    assert "item" not in comp


@pytest.mark.unit
def test_remove_progress_returns_false_when_absent() -> None:
    """remove_progress() returns False when the panel does not exist.

    # @trace FR-UI-CLICOMP-009
    """
    comp = _headless_compositor()

    result = comp.remove_progress("nonexistent")

    assert result is False


# ---------------------------------------------------------------------------
# CliCompositor.add_status_line tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_add_status_line_adds_panel() -> None:
    """add_status_line() adds a StatusPanel accessible by name.

    # @trace FR-UI-CLICOMP-010
    """
    comp = _headless_compositor()

    comp.add_status_line("info", lambda: "status text")

    assert "info" in comp
    assert comp.status_panel_names == ["info"]


@pytest.mark.unit
def test_add_status_line_replaces_existing() -> None:
    """add_status_line() with same name replaces the old status panel.

    # @trace FR-UI-CLICOMP-010
    """
    comp = _headless_compositor()

    comp.add_status_line("env", lambda: "v1")
    comp.add_status_line("env", lambda: "v2")

    assert len(comp.status_panel_names) == 1
    # Verify the NEW function is used
    sp = comp._status_panels["env"]
    assert sp.render() == "v2"


# ---------------------------------------------------------------------------
# CliCompositor.remove_status_line tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_remove_status_line_returns_true_on_success() -> None:
    """remove_status_line() returns True when found.

    # @trace FR-UI-CLICOMP-011
    """
    comp = _headless_compositor()
    comp.add_status_line("tmp", lambda: "x")

    result = comp.remove_status_line("tmp")

    assert result is True
    assert "tmp" not in comp


@pytest.mark.unit
def test_remove_status_line_returns_false_when_absent() -> None:
    """remove_status_line() returns False when not found.

    # @trace FR-UI-CLICOMP-011
    """
    comp = _headless_compositor()

    result = comp.remove_status_line("missing")

    assert result is False


# ---------------------------------------------------------------------------
# CliCompositor.render tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_returns_table() -> None:
    """render() returns a rich Table instance.

    # @trace FR-UI-CLICOMP-012
    """
    comp = _headless_compositor()
    comp.add_progress("a", total=10)
    comp.add_status_line("b", lambda: "ok")

    result = comp.render()

    assert isinstance(result, Table)


# ---------------------------------------------------------------------------
# CliCompositor introspection tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_contains_returns_true_for_progress_panel() -> None:
    """__contains__ returns True for a registered progress panel.

    # @trace FR-UI-CLICOMP-013
    """
    comp = _headless_compositor()
    comp.add_progress("p1", total=5)

    assert "p1" in comp


@pytest.mark.unit
def test_contains_returns_true_for_status_panel() -> None:
    """__contains__ returns True for a registered status panel.

    # @trace FR-UI-CLICOMP-013
    """
    comp = _headless_compositor()
    comp.add_status_line("s1", lambda: "x")

    assert "s1" in comp


@pytest.mark.unit
def test_contains_returns_false_when_absent() -> None:
    """__contains__ returns False for an unregistered name.

    # @trace FR-UI-CLICOMP-013
    """
    comp = _headless_compositor()

    assert "ghost" not in comp


@pytest.mark.unit
def test_len_counts_all_panels() -> None:
    """__len__ returns the sum of progress + status panels.

    # @trace FR-UI-CLICOMP-014
    """
    comp = _headless_compositor()
    comp.add_progress("p1", total=5)
    comp.add_progress("p2", total=10)
    comp.add_status_line("s1", lambda: "x")

    assert len(comp) == 3


@pytest.mark.unit
def test_progress_panel_names_order() -> None:
    """progress_panel_names returns names in insertion order.

    # @trace FR-UI-CLICOMP-015
    """
    comp = _headless_compositor()
    comp.add_progress("alpha", total=1)
    comp.add_progress("beta", total=1)
    comp.add_progress("gamma", total=1)

    assert comp.progress_panel_names == ["alpha", "beta", "gamma"]


@pytest.mark.unit
def test_status_panel_names_order() -> None:
    """status_panel_names returns names in insertion order.

    # @trace FR-UI-CLICOMP-016
    """
    comp = _headless_compositor()
    comp.add_status_line("x", lambda: "1")
    comp.add_status_line("y", lambda: "2")

    assert comp.status_panel_names == ["x", "y"]


# ---------------------------------------------------------------------------
# CliCompositor context manager tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_context_manager_starts_and_stops() -> None:
    """CliCompositor works correctly as a context manager.

    # @trace FR-UI-CLICOMP-017
    """
    console = Console(no_color=True, highlight=False, markup=False)
    comp = CliCompositor(console=console, transient=True)

    with comp as c:
        assert c is comp
        c.add_progress("step", total=5)
        c.update_progress("step", advance=2)
        c.complete_progress("step")

    # After exit the live display should have stopped
    assert comp._live is None


# ---------------------------------------------------------------------------
# make_cli_compositor factory test
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_make_cli_compositor_returns_instance() -> None:
    """make_cli_compositor() returns a CliCompositor with correct defaults.

    # @trace FR-UI-CLICOMP-020
    """
    comp = make_cli_compositor(refresh_per_second=2.0, transient=True)

    assert isinstance(comp, CliCompositor)
    assert comp._refresh_per_second == 2.0
    assert comp._transient is True
