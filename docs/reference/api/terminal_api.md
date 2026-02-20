# terminal API Reference

> **Source**: `src/thegent/tools/terminal.py`

## TmuxPane

---

## capture_tmux_pane

```python
capture_tmux_pane(pane_id: str, last_lines: int)
```

Capture pane content.

---

## heliosShield_status

Get status from heliosShield.

---

## is_claude_code_pane

```python
is_claude_code_pane(pane: TmuxPane)
```

Detect if a pane is likely running Claude Code.

---

## list_tmux_panes

List all tmux panes with detailed info.

---

## send_to_tmux_pane

```python
send_to_tmux_pane(pane_id: str, text: str, enter: bool)
```

Send keys to pane.

---

