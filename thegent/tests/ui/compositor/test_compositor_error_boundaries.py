"""Tests for Compositor panel error boundaries.

Covers:
- Panel exception does not propagate to compositor
- Default fallback string format on error
- Custom string error_fallback
- Custom callable error_fallback called with exception
- last_error is set correctly on failure and cleared on success
- recover() clears error state and enables retry
- Multiple panels — one failing does not affect others
- Compositor.render() / render_all() / render_panel()
- Compositor.errored_panels() / recover_panel() / recover_all()
- Edge cases: fallback callable raises, panel not found, etc.
"""

from __future__ import annotations

from thegent.ui.compositor.compositor import Compositor, Panel

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok_panel(name: str = "ok", content: str = "hello") -> Panel:
    """Create a panel whose content_fn always succeeds."""
    return Panel(name=name, content_fn=lambda: content)


def _failing_panel(name: str = "bad", exc: Exception | None = None) -> Panel:
    """Create a panel whose content_fn always raises."""
    _exc = exc or RuntimeError("boom")

    def _raise() -> str:
        raise _exc

    return Panel(name=name, content_fn=_raise)


# ---------------------------------------------------------------------------
# Panel.render — error boundary isolation
# ---------------------------------------------------------------------------


class TestPanelRenderIsolation:
    """FR: A panel exception must not propagate beyond Panel.render()."""

    def test_render_does_not_raise_on_content_fn_exception(self) -> None:
        """Panel.render() returns a string even when content_fn raises."""
        panel = _failing_panel()
        result = panel.render()  # Must not raise
        assert isinstance(result, str)

    def test_render_returns_default_fallback_on_exception(self) -> None:
        """Default fallback contains panel name and exception type."""
        panel = _failing_panel(name="widget-x")
        result = panel.render()
        assert "widget-x" in result
        assert "RuntimeError" in result

    def test_render_default_fallback_format(self) -> None:
        """Default fallback matches '[Panel error: {name} — {ExcType}]'."""
        panel = _failing_panel(name="my-panel", exc=ValueError("bad"))
        result = panel.render()
        assert result == "[Panel error: my-panel — ValueError]"

    def test_render_success_returns_content(self) -> None:
        """Successful render returns the content_fn string."""
        panel = _ok_panel(content="dashboard data")
        assert panel.render() == "dashboard data"

    def test_render_catches_arbitrary_exception_types(self) -> None:
        """Error boundary catches any exception subclass."""

        def _raise_key_error() -> str:
            raise KeyError("missing")

        panel = Panel(name="p", content_fn=_raise_key_error)
        result = panel.render()
        assert "KeyError" in result

    def test_render_catches_custom_exception_subclass(self) -> None:
        """Error boundary handles any user-defined Exception subclass."""

        class CustomError(Exception):
            pass

        def _raise_custom() -> str:
            raise CustomError("oops")

        panel = Panel(name="p", content_fn=_raise_custom)
        result = panel.render()
        assert "CustomError" in result


# ---------------------------------------------------------------------------
# Panel.error_fallback — string
# ---------------------------------------------------------------------------


class TestPanelStringFallback:
    """FR: A plain-string error_fallback is returned verbatim on error."""

    def test_string_fallback_is_returned_on_error(self) -> None:
        """error_fallback string is returned when content_fn raises."""

        def _raise() -> str:
            raise ValueError("x")

        panel = Panel(name="p", content_fn=_raise, error_fallback="CUSTOM FALLBACK")
        result = panel.render()
        assert result == "CUSTOM FALLBACK"

    def test_string_fallback_not_used_on_success(self) -> None:
        """error_fallback string is NOT returned when content_fn succeeds."""
        panel = Panel(
            name="p",
            content_fn=lambda: "good content",
            error_fallback="SHOULD NOT APPEAR",
        )
        assert panel.render() == "good content"

    def test_empty_string_fallback(self) -> None:
        """Empty string is a valid fallback."""

        def _raise() -> str:
            raise RuntimeError()

        panel = Panel(name="p", content_fn=_raise, error_fallback="")
        assert panel.render() == ""


# ---------------------------------------------------------------------------
# Panel.error_fallback — callable
# ---------------------------------------------------------------------------


class TestPanelCallableFallback:
    """FR: A callable error_fallback is invoked with the exception."""

    def test_callable_fallback_receives_exception(self) -> None:
        """The callable receives the exact exception instance."""
        received: list[Exception] = []

        def _fb(exc: Exception) -> str:
            received.append(exc)
            return "handled"

        exc = ValueError("specific error")

        def _raise() -> str:
            raise exc

        panel = Panel(name="p", content_fn=_raise, error_fallback=_fb)
        result = panel.render()
        assert result == "handled"
        assert len(received) == 1
        assert received[0] is exc

    def test_callable_fallback_return_value_is_used(self) -> None:
        """The string returned by the callable is the render output."""

        def _raise() -> str:
            raise RuntimeError("err")

        panel = Panel(
            name="p",
            content_fn=_raise,
            error_fallback=lambda exc: f"caught: {exc}",
        )
        assert panel.render() == "caught: err"

    def test_callable_fallback_exception_falls_back_to_safe_default(self) -> None:
        """If the callable itself raises, a safe default is returned."""

        def _bad_fb(exc: Exception) -> str:
            raise TypeError("fallback exploded")

        def _raise() -> str:
            raise RuntimeError("x")

        panel = Panel(
            name="broken-fb-panel",
            content_fn=_raise,
            error_fallback=_bad_fb,
        )
        result = panel.render()
        # Safe default includes panel name, original exc type, and note
        assert "broken-fb-panel" in result
        assert "RuntimeError" in result
        assert "fallback also failed" in result

    def test_callable_fallback_not_called_on_success(self) -> None:
        """Callable is NOT invoked when content_fn succeeds."""
        calls: list[int] = []

        def _fb(exc: Exception) -> str:
            calls.append(1)
            return "x"

        panel = Panel(name="p", content_fn=lambda: "ok", error_fallback=_fb)
        panel.render()
        assert calls == []


# ---------------------------------------------------------------------------
# Panel.last_error
# ---------------------------------------------------------------------------


class TestPanelLastError:
    """FR: last_error tracks the most recent exception (or None)."""

    def test_last_error_is_none_initially(self) -> None:
        """Freshly created panel has last_error = None."""
        panel = _ok_panel()
        assert panel.last_error is None

    def test_last_error_set_after_failed_render(self) -> None:
        """last_error holds the raised exception after a failure."""
        exc = RuntimeError("kaboom")
        panel = _failing_panel(exc=exc)
        panel.render()
        assert panel.last_error is exc

    def test_last_error_cleared_after_successful_render(self) -> None:
        """last_error is reset to None when content_fn succeeds."""
        call_count = [0]

        def _sometimes_fails() -> str:
            call_count[0] += 1
            if call_count[0] == 1:
                raise ValueError("first call fails")
            return "ok"

        panel = Panel(name="p", content_fn=_sometimes_fails)
        panel.render()  # fails
        assert panel.last_error is not None
        panel.render()  # succeeds
        assert panel.last_error is None

    def test_last_error_is_most_recent_exception(self) -> None:
        """last_error reflects the most recent failure."""
        exc1 = ValueError("first")
        exc2 = RuntimeError("second")
        errors = [exc1, exc2]
        idx = [0]

        def _rotating_fail() -> str:
            raise errors[idx[0] % len(errors)]

        idx[0] = 0
        panel = Panel(name="p", content_fn=_rotating_fail)
        panel.render()
        assert isinstance(panel.last_error, ValueError)
        idx[0] = 1
        panel.render()
        assert isinstance(panel.last_error, RuntimeError)

    def test_has_error_property_reflects_last_error(self) -> None:
        """has_error is True iff last_error is not None."""
        panel = _failing_panel()
        assert panel.has_error is False
        panel.render()
        assert panel.has_error is True


# ---------------------------------------------------------------------------
# Panel.recover()
# ---------------------------------------------------------------------------


class TestPanelRecover:
    """FR: recover() clears error state and allows retry."""

    def test_recover_clears_last_error(self) -> None:
        """After recover(), last_error is None."""
        panel = _failing_panel()
        panel.render()
        assert panel.last_error is not None
        panel.recover()
        assert panel.last_error is None

    def test_recover_on_healthy_panel_is_noop(self) -> None:
        """recover() on a panel with no error is safe."""
        panel = _ok_panel()
        panel.recover()
        assert panel.last_error is None

    def test_render_retries_after_recover(self) -> None:
        """After recover(), the next render calls content_fn again."""
        call_count = [0]

        def _always_fails() -> str:
            call_count[0] += 1
            raise RuntimeError("fail")

        panel = Panel(name="p", content_fn=_always_fails)
        panel.render()  # fails, call_count=1
        panel.recover()
        panel.render()  # fails again, call_count=2
        assert call_count[0] == 2

    def test_recover_then_success_clears_has_error(self) -> None:
        """After recover and successful render, has_error is False."""
        call_count = [0]

        def _fails_once() -> str:
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("once")
            return "ok"

        panel = Panel(name="p", content_fn=_fails_once)
        panel.render()
        assert panel.has_error
        panel.recover()
        panel.render()
        assert not panel.has_error

    def test_has_error_false_after_recover(self) -> None:
        """has_error is False immediately after recover(), before next render."""
        panel = _failing_panel()
        panel.render()
        assert panel.has_error
        panel.recover()
        assert panel.has_error is False


# ---------------------------------------------------------------------------
# Multiple panels — isolation
# ---------------------------------------------------------------------------


class TestMultiplePanelIsolation:
    """FR: One failing panel must not affect other panels."""

    def test_failing_panel_does_not_affect_sibling_panels(self) -> None:
        """Compositor.render() returns correct content for healthy panels."""
        comp = Compositor()
        comp.add_panel(_ok_panel(name="a", content="alpha"))
        comp.add_panel(_failing_panel(name="b"))
        comp.add_panel(_ok_panel(name="c", content="gamma"))

        results = comp.render()
        assert results[0] == "alpha"
        assert "b" in results[1]  # fallback for failing panel
        assert results[2] == "gamma"

    def test_only_failing_panel_has_error_state(self) -> None:
        """only the failing panel records last_error."""
        comp = Compositor()
        comp.add_panel(_ok_panel(name="a"))
        comp.add_panel(_failing_panel(name="b"))
        comp.add_panel(_ok_panel(name="c"))

        comp.render()

        panel_a = comp.get_panel("a")
        panel_b = comp.get_panel("b")
        panel_c = comp.get_panel("c")
        assert panel_a is not None
        assert panel_b is not None
        assert panel_c is not None
        assert panel_a.last_error is None
        assert panel_b.last_error is not None
        assert panel_c.last_error is None

    def test_multiple_failing_panels_each_track_own_error(self) -> None:
        """Each failing panel records its own distinct exception."""
        exc_b = ValueError("from b")
        exc_d = KeyError("from d")

        comp = Compositor()
        comp.add_panel(_ok_panel(name="a"))
        comp.add_panel(_failing_panel(name="b", exc=exc_b))
        comp.add_panel(_ok_panel(name="c"))
        comp.add_panel(_failing_panel(name="d", exc=exc_d))

        comp.render()

        panel_b = comp.get_panel("b")
        panel_d = comp.get_panel("d")
        assert panel_b is not None
        assert panel_d is not None
        assert panel_b.last_error is exc_b
        assert panel_d.last_error is exc_d

    def test_render_all_returns_all_panel_results(self) -> None:
        """render_all() includes an entry for every panel."""
        comp = Compositor()
        comp.add_panel(_ok_panel(name="x", content="X"))
        comp.add_panel(_failing_panel(name="y"))
        comp.add_panel(_ok_panel(name="z", content="Z"))

        mapping = comp.render_all()
        assert mapping["x"] == "X"
        assert "y" in mapping["y"]  # fallback includes panel name
        assert mapping["z"] == "Z"

    def test_render_count_equals_panel_count(self) -> None:
        """render() always returns exactly one entry per registered panel."""
        comp = Compositor()
        for i in range(5):
            comp.add_panel(Panel(name=f"p{i}", content_fn=lambda i=i: f"content-{i}"))
        results = comp.render()
        assert len(results) == 5


# ---------------------------------------------------------------------------
# Compositor error-state helpers
# ---------------------------------------------------------------------------


class TestCompositorErrorHelpers:
    """FR: Compositor provides helpers to query and recover panel error states."""

    def test_errored_panels_empty_when_all_healthy(self) -> None:
        """errored_panels() returns [] when no panels have failed."""
        comp = Compositor()
        comp.add_panel(_ok_panel(name="a"))
        comp.add_panel(_ok_panel(name="b"))
        comp.render()
        assert comp.errored_panels() == []

    def test_errored_panels_lists_failed_panels(self) -> None:
        """errored_panels() returns names of panels that have last_error set."""
        comp = Compositor()
        comp.add_panel(_ok_panel(name="a"))
        comp.add_panel(_failing_panel(name="b"))
        comp.add_panel(_failing_panel(name="c"))
        comp.render()
        assert sorted(comp.errored_panels()) == ["b", "c"]

    def test_recover_panel_clears_single_panel_error(self) -> None:
        """recover_panel() clears only the specified panel."""
        comp = Compositor()
        comp.add_panel(_failing_panel(name="b"))
        comp.add_panel(_failing_panel(name="c"))
        comp.render()
        assert sorted(comp.errored_panels()) == ["b", "c"]
        comp.recover_panel("b")
        assert comp.errored_panels() == ["c"]

    def test_recover_panel_returns_true_on_success(self) -> None:
        """recover_panel() returns True when panel exists."""
        comp = Compositor()
        comp.add_panel(_failing_panel(name="p"))
        comp.render()
        assert comp.recover_panel("p") is True

    def test_recover_panel_returns_false_for_missing_panel(self) -> None:
        """recover_panel() returns False when panel does not exist."""
        comp = Compositor()
        assert comp.recover_panel("nonexistent") is False

    def test_recover_all_clears_all_error_states(self) -> None:
        """recover_all() removes all error states from all panels."""
        comp = Compositor()
        comp.add_panel(_failing_panel(name="a"))
        comp.add_panel(_failing_panel(name="b"))
        comp.render()
        assert len(comp.errored_panels()) == 2
        comp.recover_all()
        assert comp.errored_panels() == []

    def test_render_panel_returns_fallback_for_failing_panel(self) -> None:
        """render_panel() returns fallback string for a single failing panel."""
        comp = Compositor()
        comp.add_panel(_failing_panel(name="p", exc=RuntimeError("fail")))
        result = comp.render_panel("p")
        assert result is not None
        assert "p" in result
        assert "RuntimeError" in result

    def test_render_panel_returns_none_for_missing_panel(self) -> None:
        """render_panel() returns None when panel name does not exist."""
        comp = Compositor()
        assert comp.render_panel("ghost") is None

    def test_get_panel_returns_none_for_missing_name(self) -> None:
        """get_panel() returns None for unregistered panel."""
        comp = Compositor()
        assert comp.get_panel("nope") is None
