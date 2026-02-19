# compositor API Reference

> **Source**: `src/thegent/ux/compositor.py`

Minimal TUI compositor for terminal panes.

Implements the research "Path B" MVP by hosting pane state in a Rich layout
and linking to external tmux sessions.

---

## TUICompositor

Collect tmux panes and compose a simple two-pane terminal dashboard.

### Methods

#### TUICompositor.__init__

```python
__init__(self, include_non_claude, config_path)
```

#### TUICompositor.collect_panes

```python
collect_panes(self)
```

#### TUICompositor.render

```python
render(self, layout_name)
```

---

## collect_panes

```python
collect_panes(self)
```

---

## render

```python
render(self, layout_name)
```

---

## run_compositor_tui

```python
run_compositor_tui(layout_name, include_non_claude, once, refresh_interval)
```

---

