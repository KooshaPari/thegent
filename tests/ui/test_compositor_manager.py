"""Tests for CompositorManager: layout management with multiple Compositor instances.

Covers:
- Empty manager returns empty string                             (FR-UI-CM-001)
- add_compositor stores slot                                     (FR-UI-CM-002)
- remove_compositor removes slot                                 (FR-UI-CM-003)
- get_compositor returns correct Compositor                      (FR-UI-CM-004)
- focus/get_focused focus management                            (FR-UI-CM-005)
- switch_layout changes layout                                   (FR-UI-CM-006)
- render_all SINGLE layout                                       (FR-UI-CM-007)
- render_all SPLIT_H layout                                      (FR-UI-CM-008)
- render_all SPLIT_V layout                                      (FR-UI-CM-009)
- render_all GRID_2X2 layout                                     (FR-UI-CM-010)
- Box drawing borders appear in output                          (FR-UI-CM-011)
- Focused slot shows [*] indicator                              (FR-UI-CM-012)
- Width distribution proportional to weights                    (FR-UI-CM-013)
- CompositorSlot weight validation                              (FR-UI-CM-014)
- Auto-focus first slot on add                                  (FR-UI-CM-015)
- Focus follows removal of focused slot                         (FR-UI-CM-016)
- focus() raises KeyError for missing slot                      (FR-UI-CM-017)
- len() and __contains__ helpers                                (FR-UI-CM-018)
- slot_ids returns ordered list                                 (FR-UI-CM-019)
- render_all with erroring panel produces fallback               (FR-UI-CM-020)
- GRID_2X2 with overflow slots                                  (FR-UI-CM-021)
- Replace existing slot                                         (FR-UI-CM-022)
"""

from __future__ import annotations

import pytest
from thegent.ui.compositor.compositor import Compositor, Panel
from thegent.ui.compositor_manager import CompositorManager, CompositorSlot, Layout

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _compositor(content: str = "hello") -> Compositor:
    """Return a Compositor with a single panel rendering *content*."""
    comp = Compositor()
    comp.add_panel(Panel(name="p", content_fn=lambda: content))
    return comp


def _manager_with(*args: tuple[str, str]) -> CompositorManager:
    """Build a manager with slots.  args = (slot_id, content) pairs."""
    mgr = CompositorManager()
    for slot_id, content in args:
        mgr.add_compositor(_compositor(content), slot_id)
    return mgr


# ---------------------------------------------------------------------------
# FR-UI-CM-001: Empty manager
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_all_empty_manager_returns_empty_string() -> None:
    """render_all() on a manager with no slots returns an empty string.

    # @trace FR-UI-CM-001
    """
    mgr = CompositorManager()
    assert mgr.render_all() == ""


@pytest.mark.unit
def test_empty_manager_len_is_zero() -> None:
    """len() of an empty manager is 0.

    # @trace FR-UI-CM-001
    """
    mgr = CompositorManager()
    assert len(mgr) == 0


# ---------------------------------------------------------------------------
# FR-UI-CM-002: add_compositor
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_add_compositor_increases_len() -> None:
    """Adding a compositor increases len() by 1.

    # @trace FR-UI-CM-002
    """
    mgr = CompositorManager()
    mgr.add_compositor(_compositor(), "a")
    assert len(mgr) == 1


@pytest.mark.unit
def test_add_compositor_slot_present_in_manager() -> None:
    """After add_compositor the slot_id appears in contains check.

    # @trace FR-UI-CM-002
    """
    mgr = CompositorManager()
    mgr.add_compositor(_compositor(), "my-slot")
    assert "my-slot" in mgr


@pytest.mark.unit
def test_add_compositor_multiple_slots() -> None:
    """Multiple add_compositor calls register multiple slots.

    # @trace FR-UI-CM-002
    """
    mgr = _manager_with(("a", "A"), ("b", "B"), ("c", "C"))
    assert len(mgr) == 3


# ---------------------------------------------------------------------------
# FR-UI-CM-003: remove_compositor
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_remove_compositor_returns_true_on_success() -> None:
    """remove_compositor returns True when the slot existed.

    # @trace FR-UI-CM-003
    """
    mgr = _manager_with(("x", "X"))
    assert mgr.remove_compositor("x") is True


@pytest.mark.unit
def test_remove_compositor_returns_false_for_missing() -> None:
    """remove_compositor returns False when the slot does not exist.

    # @trace FR-UI-CM-003
    """
    mgr = CompositorManager()
    assert mgr.remove_compositor("does-not-exist") is False


@pytest.mark.unit
def test_remove_compositor_slot_absent_after_removal() -> None:
    """Slot is not present after remove_compositor.

    # @trace FR-UI-CM-003
    """
    mgr = _manager_with(("a", "A"))
    mgr.remove_compositor("a")
    assert "a" not in mgr


# ---------------------------------------------------------------------------
# FR-UI-CM-004: get_compositor
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_compositor_returns_compositor_instance() -> None:
    """get_compositor returns the exact Compositor that was added.

    # @trace FR-UI-CM-004
    """
    comp = _compositor("unique-content")
    mgr = CompositorManager()
    mgr.add_compositor(comp, "slot-a")
    assert mgr.get_compositor("slot-a") is comp


@pytest.mark.unit
def test_get_compositor_returns_none_for_missing_slot() -> None:
    """get_compositor returns None when the slot does not exist.

    # @trace FR-UI-CM-004
    """
    mgr = CompositorManager()
    assert mgr.get_compositor("missing") is None


# ---------------------------------------------------------------------------
# FR-UI-CM-005: focus / get_focused
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_focused_returns_none_on_empty_manager() -> None:
    """get_focused returns None when no slots are registered.

    # @trace FR-UI-CM-005
    """
    mgr = CompositorManager()
    assert mgr.get_focused() is None


@pytest.mark.unit
def test_focus_sets_focused_slot() -> None:
    """focus() updates the focused slot to the specified ID.

    # @trace FR-UI-CM-005
    """
    mgr = _manager_with(("a", "A"), ("b", "B"))
    mgr.focus("b")
    focused = mgr.get_focused()
    assert focused is not None
    assert focused.id == "b"


@pytest.mark.unit
def test_first_slot_auto_focused() -> None:
    """The first slot added is automatically focused.

    # @trace FR-UI-CM-005
    """
    mgr = CompositorManager()
    mgr.add_compositor(_compositor(), "first")
    focused = mgr.get_focused()
    assert focused is not None
    assert focused.id == "first"


# ---------------------------------------------------------------------------
# FR-UI-CM-006: switch_layout
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_switch_layout_changes_layout() -> None:
    """switch_layout updates the layout property.

    # @trace FR-UI-CM-006
    """
    mgr = CompositorManager(Layout.SINGLE)
    mgr.switch_layout(Layout.SPLIT_H)
    assert mgr.layout == Layout.SPLIT_H


@pytest.mark.unit
def test_default_layout_is_single() -> None:
    """Default layout is SINGLE.

    # @trace FR-UI-CM-006
    """
    mgr = CompositorManager()
    assert mgr.layout == Layout.SINGLE


# ---------------------------------------------------------------------------
# FR-UI-CM-007: render_all SINGLE
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_all_single_contains_content() -> None:
    """render_all(SINGLE) includes panel content in output.

    # @trace FR-UI-CM-007
    """
    mgr = CompositorManager(Layout.SINGLE)
    mgr.add_compositor(_compositor("hello-world"), "main")
    output = mgr.render_all(width=40)
    assert "hello-world" in output


@pytest.mark.unit
def test_render_all_single_only_renders_first_slot() -> None:
    """render_all(SINGLE) renders only the first slot.

    # @trace FR-UI-CM-007
    """
    mgr = CompositorManager(Layout.SINGLE)
    mgr.add_compositor(_compositor("first"), "a")
    mgr.add_compositor(_compositor("second"), "b")
    output = mgr.render_all(width=40)
    assert "first" in output
    assert "second" not in output


# ---------------------------------------------------------------------------
# FR-UI-CM-008: render_all SPLIT_H
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_all_split_h_contains_both_contents() -> None:
    """render_all(SPLIT_H) contains content from all slots.

    # @trace FR-UI-CM-008
    """
    mgr = CompositorManager(Layout.SPLIT_H)
    mgr.add_compositor(_compositor("left"), "l")
    mgr.add_compositor(_compositor("right"), "r")
    output = mgr.render_all(width=80)
    assert "left" in output
    assert "right" in output


@pytest.mark.unit
def test_render_all_split_h_columns_on_same_line() -> None:
    """render_all(SPLIT_H) places columns side by side (same lines).

    # @trace FR-UI-CM-008
    """
    mgr = CompositorManager(Layout.SPLIT_H)
    mgr.add_compositor(_compositor("LEFT"), "l")
    mgr.add_compositor(_compositor("RGHT"), "r")
    output = mgr.render_all(width=80)
    lines = output.splitlines()
    found = any("LEFT" in line and "RGHT" in line for line in lines)
    assert found


# ---------------------------------------------------------------------------
# FR-UI-CM-009: render_all SPLIT_V
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_all_split_v_contains_all_content() -> None:
    """render_all(SPLIT_V) contains content from all slots.

    # @trace FR-UI-CM-009
    """
    mgr = CompositorManager(Layout.SPLIT_V)
    mgr.add_compositor(_compositor("top-content"), "t")
    mgr.add_compositor(_compositor("bot-content"), "b")
    output = mgr.render_all(width=40)
    assert "top-content" in output
    assert "bot-content" in output


@pytest.mark.unit
def test_render_all_split_v_slots_on_separate_lines() -> None:
    """render_all(SPLIT_V) stacks slots vertically — content on different lines.

    # @trace FR-UI-CM-009
    """
    mgr = CompositorManager(Layout.SPLIT_V)
    mgr.add_compositor(_compositor("ALPHA"), "a")
    mgr.add_compositor(_compositor("BETA"), "b")
    output = mgr.render_all(width=40)
    lines = output.splitlines()
    same_line = any("ALPHA" in ln and "BETA" in ln for ln in lines)
    assert not same_line


# ---------------------------------------------------------------------------
# FR-UI-CM-010: render_all GRID_2X2
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_all_grid_2x2_four_slots() -> None:
    """render_all(GRID_2X2) renders all four grid slots.

    # @trace FR-UI-CM-010
    """
    mgr = CompositorManager(Layout.GRID_2X2)
    for label in ("TL", "TR", "BL", "BR"):
        mgr.add_compositor(_compositor(label), label)
    output = mgr.render_all(width=80)
    for label in ("TL", "TR", "BL", "BR"):
        assert label in output


@pytest.mark.unit
def test_render_all_grid_2x2_single_slot() -> None:
    """render_all(GRID_2X2) with one slot renders that slot at full width.

    # @trace FR-UI-CM-010
    """
    mgr = CompositorManager(Layout.GRID_2X2)
    mgr.add_compositor(_compositor("solo"), "s")
    output = mgr.render_all(width=40)
    assert "solo" in output


# ---------------------------------------------------------------------------
# FR-UI-CM-011: Box drawing borders
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_all_output_contains_box_corners() -> None:
    """Render output contains box-drawing corner characters.

    # @trace FR-UI-CM-011
    """
    mgr = _manager_with(("x", "content"))
    output = mgr.render_all(width=30)
    assert "\u250c" in output  # ┌
    assert "\u2518" in output  # ┘


@pytest.mark.unit
def test_render_all_output_contains_horizontal_border() -> None:
    """Render output contains horizontal box-drawing line.

    # @trace FR-UI-CM-011
    """
    mgr = _manager_with(("x", "content"))
    output = mgr.render_all(width=30)
    assert "\u2500" in output  # ─


# ---------------------------------------------------------------------------
# FR-UI-CM-012: Focused slot [*] indicator
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_focused_slot_shows_star_indicator() -> None:
    """Focused slot title contains [*] in render output.

    # @trace FR-UI-CM-012
    """
    mgr = CompositorManager(Layout.SPLIT_V)
    mgr.add_compositor(_compositor("A"), "slot-a")
    mgr.add_compositor(_compositor("B"), "slot-b")
    mgr.focus("slot-a")
    output = mgr.render_all(width=40)
    assert "[*]" in output


@pytest.mark.unit
def test_unfocused_slot_does_not_show_star() -> None:
    """Unfocused slot title does NOT contain [*].

    # @trace FR-UI-CM-012
    """
    mgr = CompositorManager(Layout.SPLIT_V)
    mgr.add_compositor(_compositor("A"), "alpha")
    mgr.add_compositor(_compositor("B"), "beta")
    mgr.focus("alpha")
    output = mgr.render_all(width=40)
    assert output.count("[*]") == 1


# ---------------------------------------------------------------------------
# FR-UI-CM-013: Width distribution
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_distribute_widths_equal_weights() -> None:
    """_distribute_widths distributes equally for equal weights.

    # @trace FR-UI-CM-013
    """
    slots = [
        CompositorSlot("a", _compositor(), weight=1.0),
        CompositorSlot("b", _compositor(), weight=1.0),
    ]
    widths = CompositorManager._distribute_widths(slots, 2.0, 100)
    assert sum(widths) == 100
    assert widths[0] == 50
    assert widths[1] == 50


@pytest.mark.unit
def test_distribute_widths_unequal_weights() -> None:
    """_distribute_widths allocates more space to heavier slot.

    # @trace FR-UI-CM-013
    """
    slots = [
        CompositorSlot("a", _compositor(), weight=2.0),
        CompositorSlot("b", _compositor(), weight=1.0),
    ]
    widths = CompositorManager._distribute_widths(slots, 3.0, 90)
    assert sum(widths) == 90
    assert widths[0] > widths[1]


@pytest.mark.unit
def test_distribute_widths_empty_slots() -> None:
    """_distribute_widths returns empty list for no slots.

    # @trace FR-UI-CM-013
    """
    widths = CompositorManager._distribute_widths([], 0.0, 80)
    assert widths == []


# ---------------------------------------------------------------------------
# FR-UI-CM-014: CompositorSlot weight validation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_compositor_slot_zero_weight_raises() -> None:
    """CompositorSlot with weight=0 raises ValueError.

    # @trace FR-UI-CM-014
    """
    with pytest.raises(ValueError, match="weight must be > 0"):
        CompositorSlot(id="bad", compositor=_compositor(), weight=0.0)


@pytest.mark.unit
def test_compositor_slot_negative_weight_raises() -> None:
    """CompositorSlot with negative weight raises ValueError.

    # @trace FR-UI-CM-014
    """
    with pytest.raises(ValueError, match="weight must be > 0"):
        CompositorSlot(id="bad", compositor=_compositor(), weight=-1.0)


# ---------------------------------------------------------------------------
# FR-UI-CM-015: Auto-focus first slot
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_auto_focus_first_slot_on_first_add() -> None:
    """First slot added is automatically focused.

    # @trace FR-UI-CM-015
    """
    mgr = CompositorManager()
    mgr.add_compositor(_compositor(), "first")
    mgr.add_compositor(_compositor(), "second")
    focused = mgr.get_focused()
    assert focused is not None
    assert focused.id == "first"


# ---------------------------------------------------------------------------
# FR-UI-CM-016: Focus follows removal
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_focus_moves_to_next_slot_after_focused_removed() -> None:
    """Removing the focused slot moves focus to the next available slot.

    # @trace FR-UI-CM-016
    """
    mgr = _manager_with(("a", "A"), ("b", "B"))
    mgr.focus("a")
    mgr.remove_compositor("a")
    focused = mgr.get_focused()
    assert focused is not None
    assert focused.id == "b"


@pytest.mark.unit
def test_focus_is_none_after_last_slot_removed() -> None:
    """Removing the only slot leaves focus as None.

    # @trace FR-UI-CM-016
    """
    mgr = _manager_with(("a", "A"))
    mgr.remove_compositor("a")
    assert mgr.get_focused() is None


# ---------------------------------------------------------------------------
# FR-UI-CM-017: focus() raises KeyError for missing slot
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_focus_raises_key_error_for_missing_slot() -> None:
    """focus() raises KeyError when the slot does not exist.

    # @trace FR-UI-CM-017
    """
    mgr = CompositorManager()
    with pytest.raises(KeyError, match="no-such-slot"):
        mgr.focus("no-such-slot")


# ---------------------------------------------------------------------------
# FR-UI-CM-018: len() and __contains__
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_len_and_contains_after_add_remove() -> None:
    """len() and 'in' operator reflect add/remove state correctly.

    # @trace FR-UI-CM-018
    """
    mgr = CompositorManager()
    assert len(mgr) == 0
    assert "x" not in mgr
    mgr.add_compositor(_compositor(), "x")
    assert len(mgr) == 1
    assert "x" in mgr
    mgr.remove_compositor("x")
    assert len(mgr) == 0
    assert "x" not in mgr


# ---------------------------------------------------------------------------
# FR-UI-CM-019: slot_ids ordered list
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_slot_ids_returns_insertion_order() -> None:
    """slot_ids returns slot IDs in insertion order.

    # @trace FR-UI-CM-019
    """
    mgr = _manager_with(("z", "Z"), ("a", "A"), ("m", "M"))
    assert mgr.slot_ids == ["z", "a", "m"]


# ---------------------------------------------------------------------------
# FR-UI-CM-020: render_all with erroring panel produces fallback
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_all_with_erroring_panel_does_not_raise() -> None:
    """render_all does not raise when a compositor panel errors.

    # @trace FR-UI-CM-020
    """

    def bad_content() -> str:
        raise RuntimeError("panel broke")

    comp = Compositor()
    comp.add_panel(Panel(name="bad", content_fn=bad_content))
    mgr = CompositorManager()
    mgr.add_compositor(comp, "err-slot")

    output = mgr.render_all(width=40)
    assert isinstance(output, str)
    assert len(output) > 0


# ---------------------------------------------------------------------------
# FR-UI-CM-021: GRID_2X2 with overflow slots
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_all_grid_2x2_overflow_slots_included() -> None:
    """render_all(GRID_2X2) includes overflow (5th+) slots in output.

    # @trace FR-UI-CM-021
    """
    mgr = CompositorManager(Layout.GRID_2X2)
    for label in ("TL", "TR", "BL", "BR", "OV"):
        mgr.add_compositor(_compositor(label), label)
    output = mgr.render_all(width=80)
    assert "OV" in output


# ---------------------------------------------------------------------------
# FR-UI-CM-022: Replace existing slot
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_replace_existing_slot_updates_compositor() -> None:
    """Adding a slot with an existing ID replaces the compositor.

    # @trace FR-UI-CM-022
    """
    mgr = CompositorManager()
    mgr.add_compositor(_compositor("original"), "slot")
    mgr.add_compositor(_compositor("replacement"), "slot")
    assert len(mgr) == 1
    comp = mgr.get_compositor("slot")
    assert comp is not None
    output = "\n".join(comp.render())
    assert "replacement" in output
    assert "original" not in output
