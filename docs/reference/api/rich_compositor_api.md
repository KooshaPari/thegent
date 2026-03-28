# rich_compositor API Reference

> **Source**: `src/thegent/ui/compositor/rich_compositor.py`

Rich-based TUI compositor for terminal pane management (MVP).

Implements the research "Path B" MVP by hosting pane state in a Rich layout
and linking to external tmux sessions.

---

## TUICompositor

Collect tmux panes and compose a simple two-pane terminal dashboard.

### Methods

#### TUICompositor.__init__

```python
__init__(self: Any, include_non_claude: bool, config_path: Any)
```

---

#### TUICompositor.collect_panes

```python
collect_panes(self: Any)
```

---

#### TUICompositor.render

```python
render(self: Any, layout_name: str)
```

---

---

## collect_panes

```python
collect_panes(self: Any) -> list[Any]
```

---

## render

```python
render(self: Any, layout_name: str) -> Layout
```

---

## run_compositor_tui

```python
run_compositor_tui(layout_name: str, include_non_claude: bool, once: bool, refresh_interval: float) -> None
```

---

