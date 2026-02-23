"""Tests for Compositor panel lifecycle hooks.

Covers:
- on_mount called when panel added                  (FR-UI-COMP-001)
- on_unmount called when panel removed              (FR-UI-COMP-002)
- Hook exceptions don't crash the compositor        (FR-UI-COMP-003)
- Hooks can be None (no-op)                         (FR-UI-COMP-004)
- Multiple panels with independent hooks            (FR-UI-COMP-005)
- Replacement of an existing panel fires both hooks (FR-UI-COMP-006)
- render() returns content in insertion order       (FR-UI-COMP-007)
- render() swallows content_fn errors               (FR-UI-COMP-008)
- Compositor membership and length helpers          (FR-UI-COMP-009)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from thegent.ui.compositor.compositor import Compositor, Panel

if TYPE_CHECKING:
    from collections.abc import Callable


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_panel(
    name: str = "panel-a",
    content: str = "content",
    on_mount: Callable[[Panel], None] | None = None,
    on_unmount: Callable[[Panel], None] | None = None,
) -> Panel:
    return Panel(
        name=name,
        content_fn=lambda: content,
        on_mount=on_mount,
        on_unmount=on_unmount,
    )


# ---------------------------------------------------------------------------
# 1. on_mount called when panel is added
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_on_mount_called_on_add_panel() -> None:
    """on_mount fires exactly once when add_panel is called.

    # @trace FR-UI-COMP-001
    """
    hook = MagicMock()
    comp = Compositor()
    panel = _make_panel(on_mount=hook)

    comp.add_panel(panel)

    hook.assert_called_once_with(panel)


@pytest.mark.unit
def test_on_mount_receives_panel_instance() -> None:
    """on_mount receives the exact Panel object that was added.

    # @trace FR-UI-COMP-001
    """
    received: list[Panel] = []
    comp = Compositor()
    panel = _make_panel(on_mount=received.append)

    comp.add_panel(panel)

    assert len(received) == 1
    assert received[0] is panel


@pytest.mark.unit
def test_on_mount_called_for_each_panel_added() -> None:
    """on_mount fires once per add_panel call across multiple panels.

    # @trace FR-UI-COMP-001
    """
    events: list[str] = []

    def capture_name(p: Panel) -> None:
        events.append(p.name)

    comp = Compositor()
    for name in ("a", "b", "c"):
        comp.add_panel(_make_panel(name=name, on_mount=capture_name))

    assert events == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# 2. on_unmount called when panel is removed
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_on_unmount_called_on_remove_panel() -> None:
    """on_unmount fires exactly once when remove_panel is called.

    # @trace FR-UI-COMP-002
    """
    hook = MagicMock()
    comp = Compositor()
    panel = _make_panel(on_unmount=hook)
    comp.add_panel(panel)

    comp.remove_panel(panel.name)

    hook.assert_called_once_with(panel)


@pytest.mark.unit
def test_on_unmount_receives_panel_instance() -> None:
    """on_unmount receives the correct Panel object.

    # @trace FR-UI-COMP-002
    """
    received: list[Panel] = []
    comp = Compositor()
    panel = _make_panel(on_unmount=received.append)
    comp.add_panel(panel)

    comp.remove_panel(panel.name)

    assert len(received) == 1
    assert received[0] is panel


@pytest.mark.unit
def test_on_unmount_not_called_for_missing_panel() -> None:
    """Removing a non-existent panel does not fire any hook.

    # @trace FR-UI-COMP-002
    """
    hook = MagicMock()
    comp = Compositor()

    result = comp.remove_panel("does-not-exist")

    hook.assert_not_called()
    assert result is False


@pytest.mark.unit
def test_remove_panel_returns_true_on_success() -> None:
    """remove_panel returns True when the panel existed.

    # @trace FR-UI-COMP-002
    """
    comp = Compositor()
    comp.add_panel(_make_panel())

    assert comp.remove_panel("panel-a") is True


@pytest.mark.unit
def test_panel_not_present_after_remove() -> None:
    """Panel is absent from the compositor after removal.

    # @trace FR-UI-COMP-002
    """
    comp = Compositor()
    comp.add_panel(_make_panel())
    comp.remove_panel("panel-a")

    assert "panel-a" not in comp


# ---------------------------------------------------------------------------
# 3. Hook exceptions don't crash the compositor
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_on_mount_exception_does_not_crash_compositor() -> None:
    """A raising on_mount hook is swallowed; compositor remains functional.

    # @trace FR-UI-COMP-003
    """

    def bad_mount(p: Panel) -> None:
        raise RuntimeError("mount exploded")

    comp = Compositor()
    panel = _make_panel(on_mount=bad_mount)

    # Should not raise
    comp.add_panel(panel)

    # Compositor is still usable
    assert "panel-a" in comp


@pytest.mark.unit
def test_on_unmount_exception_does_not_crash_compositor() -> None:
    """A raising on_unmount hook is swallowed; compositor remains functional.

    # @trace FR-UI-COMP-003
    """

    def bad_unmount(p: Panel) -> None:
        raise ValueError("unmount exploded")

    comp = Compositor()
    panel = _make_panel(on_unmount=bad_unmount)
    comp.add_panel(panel)

    # Should not raise
    comp.remove_panel("panel-a")

    # Compositor still accepts new panels
    comp.add_panel(_make_panel(name="new-panel"))
    assert "new-panel" in comp


@pytest.mark.unit
def test_mount_exception_logged(caplog: pytest.LogCaptureFixture) -> None:
    """on_mount exceptions are logged at ERROR level.

    # @trace FR-UI-COMP-003
    """

    def bad_mount(p: Panel) -> None:
        raise RuntimeError("boom")

    comp = Compositor()
    with caplog.at_level(logging.ERROR, logger="thegent.ui.compositor.compositor"):
        comp.add_panel(_make_panel(on_mount=bad_mount))

    assert any("on_mount" in record.message for record in caplog.records)


@pytest.mark.unit
def test_unmount_exception_logged(caplog: pytest.LogCaptureFixture) -> None:
    """on_unmount exceptions are logged at ERROR level.

    # @trace FR-UI-COMP-003
    """

    def bad_unmount(p: Panel) -> None:
        raise RuntimeError("boom")

    comp = Compositor()
    panel = _make_panel(on_unmount=bad_unmount)
    comp.add_panel(panel)

    with caplog.at_level(logging.ERROR, logger="thegent.ui.compositor.compositor"):
        comp.remove_panel("panel-a")

    assert any("on_unmount" in record.message for record in caplog.records)


# ---------------------------------------------------------------------------
# 4. Hooks can be None (no-op)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_none_on_mount_does_not_raise() -> None:
    """Panel with on_mount=None can be added without error.

    # @trace FR-UI-COMP-004
    """
    comp = Compositor()
    panel = _make_panel(on_mount=None)

    # Should not raise
    comp.add_panel(panel)

    assert "panel-a" in comp


@pytest.mark.unit
def test_none_on_unmount_does_not_raise() -> None:
    """Panel with on_unmount=None can be removed without error.

    # @trace FR-UI-COMP-004
    """
    comp = Compositor()
    panel = _make_panel(on_unmount=None)
    comp.add_panel(panel)

    # Should not raise
    comp.remove_panel("panel-a")

    assert "panel-a" not in comp


@pytest.mark.unit
def test_panel_with_both_hooks_none() -> None:
    """Panel with neither hook set works end-to-end without error.

    # @trace FR-UI-COMP-004
    """
    comp = Compositor()
    panel = Panel(name="bare", content_fn=lambda: "bare content")
    comp.add_panel(panel)
    comp.remove_panel("bare")

    assert "bare" not in comp


# ---------------------------------------------------------------------------
# 5. Multiple panels with different hooks
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_multiple_panels_independent_mount_hooks() -> None:
    """Each panel's on_mount fires independently and only for that panel.

    # @trace FR-UI-COMP-005
    """
    events: list[str] = []

    def on_mount(p: Panel) -> None:
        events.append(f"mount:{p.name}")

    comp = Compositor()
    comp.add_panel(_make_panel("x", on_mount=on_mount))
    comp.add_panel(_make_panel("y", on_mount=on_mount))
    comp.add_panel(_make_panel("z"))  # no hook

    assert events == ["mount:x", "mount:y"]


@pytest.mark.unit
def test_multiple_panels_independent_unmount_hooks() -> None:
    """Each panel's on_unmount fires independently when that panel is removed.

    # @trace FR-UI-COMP-005
    """
    events: list[str] = []

    def on_unmount(p: Panel) -> None:
        events.append(f"unmount:{p.name}")

    comp = Compositor()
    comp.add_panel(_make_panel("x", on_unmount=on_unmount))
    comp.add_panel(_make_panel("y", on_unmount=on_unmount))

    comp.remove_panel("x")
    assert events == ["unmount:x"]

    comp.remove_panel("y")
    assert events == ["unmount:x", "unmount:y"]


@pytest.mark.unit
def test_one_panel_bad_hook_does_not_affect_others() -> None:
    """A hook exception on one panel does not prevent other panels' hooks.

    # @trace FR-UI-COMP-005
    """
    events: list[str] = []

    def good_mount(name: str) -> Callable[[Panel], None]:
        def _hook(p: Panel) -> None:
            events.append(name)

        return _hook

    def bad_mount(p: Panel) -> None:
        raise RuntimeError("oops")

    comp = Compositor()
    comp.add_panel(_make_panel("good1", on_mount=good_mount("good1")))
    comp.add_panel(_make_panel("bad", on_mount=bad_mount))
    comp.add_panel(_make_panel("good2", on_mount=good_mount("good2")))

    # good1 and good2 hooks ran; bad hook swallowed
    assert "good1" in events
    assert "good2" in events


# ---------------------------------------------------------------------------
# 6. Replacement of an existing panel fires both hooks
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_replacing_panel_fires_old_unmount_then_new_mount() -> None:
    """When a panel is replaced, old on_unmount fires before new on_mount.

    # @trace FR-UI-COMP-006
    """
    events: list[str] = []

    old_panel = _make_panel(
        "shared",
        on_unmount=lambda p: events.append("old_unmount"),
    )
    new_panel = _make_panel(
        "shared",
        on_mount=lambda p: events.append("new_mount"),
    )

    comp = Compositor()
    comp.add_panel(old_panel)
    comp.add_panel(new_panel)  # replace

    assert events == ["old_unmount", "new_mount"]


@pytest.mark.unit
def test_replaced_panel_is_no_longer_retrievable_via_render() -> None:
    """After replacement only the new panel's content appears in render.

    # @trace FR-UI-COMP-006
    """
    comp = Compositor()
    comp.add_panel(_make_panel("p", content="old content"))
    comp.add_panel(_make_panel("p", content="new content"))

    rendered = comp.render()
    assert rendered == ["new content"]


# ---------------------------------------------------------------------------
# 7. render() returns content in insertion order
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_returns_content_in_insertion_order() -> None:
    """render() yields each panel's content in the order panels were added.

    # @trace FR-UI-COMP-007
    """
    comp = Compositor()
    comp.add_panel(_make_panel("first", content="AAA"))
    comp.add_panel(_make_panel("second", content="BBB"))
    comp.add_panel(_make_panel("third", content="CCC"))

    assert comp.render() == ["AAA", "BBB", "CCC"]


@pytest.mark.unit
def test_render_empty_compositor_returns_empty_list() -> None:
    """render() on a compositor with no panels returns an empty list.

    # @trace FR-UI-COMP-007
    """
    comp = Compositor()
    assert comp.render() == []


# ---------------------------------------------------------------------------
# 8. render() swallows content_fn errors
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_swallows_content_fn_exception() -> None:
    """A content_fn that raises produces an error placeholder, not a crash.

    # @trace FR-UI-COMP-008
    """

    def bad_content() -> str:
        raise RuntimeError("content broken")

    comp = Compositor()
    comp.add_panel(Panel(name="bad", content_fn=bad_content))

    result = comp.render()
    assert len(result) == 1
    # Panel error boundary inserts a fallback string
    assert result[0] != ""


@pytest.mark.unit
def test_render_continues_after_one_panel_error() -> None:
    """A failing panel does not prevent subsequent panels from rendering.

    # @trace FR-UI-COMP-008
    """

    def bad_content() -> str:
        raise ValueError("oops")

    comp = Compositor()
    comp.add_panel(Panel(name="ok_before", content_fn=lambda: "before"))
    comp.add_panel(Panel(name="bad", content_fn=bad_content))
    comp.add_panel(Panel(name="ok_after", content_fn=lambda: "after"))

    result = comp.render()
    assert result[0] == "before"
    assert result[2] == "after"
    # Middle panel produced some fallback (non-empty)
    assert result[1] != ""


# ---------------------------------------------------------------------------
# 9. Membership and length helpers
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_len_reflects_panel_count() -> None:
    """len(compositor) returns the number of registered panels.

    # @trace FR-UI-COMP-009
    """
    comp = Compositor()
    assert len(comp) == 0

    comp.add_panel(_make_panel("a"))
    assert len(comp) == 1

    comp.add_panel(_make_panel("b"))
    assert len(comp) == 2

    comp.remove_panel("a")
    assert len(comp) == 1


@pytest.mark.unit
def test_contains_returns_true_for_present_panel() -> None:
    """``in`` operator returns True for a panel that exists.

    # @trace FR-UI-COMP-009
    """
    comp = Compositor()
    comp.add_panel(_make_panel("present"))

    assert "present" in comp


@pytest.mark.unit
def test_contains_returns_false_for_absent_panel() -> None:
    """``in`` operator returns False for a panel that does not exist.

    # @trace FR-UI-COMP-009
    """
    comp = Compositor()

    assert "absent" not in comp


@pytest.mark.unit
def test_panel_names_returns_ordered_list() -> None:
    """panel_names returns panels in insertion order.

    # @trace FR-UI-COMP-009
    """
    comp = Compositor()
    comp.add_panel(_make_panel("z"))
    comp.add_panel(_make_panel("a"))
    comp.add_panel(_make_panel("m"))

    assert comp.panel_names == ["z", "a", "m"]
