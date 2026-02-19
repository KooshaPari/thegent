# terminal_cli API Reference

> **Source**: `src/thegent/terminal_cli.py`

CLI implementation for terminal management.

---

## attach_terminal

Attach to a terminal session.

```python
attach_terminal(pane_id)
```

---

## inspect_terminal

View the last few lines of a terminal pane.

```python
inspect_terminal(pane_id)
```

---

## list_terminals

List active terminal panes (tmux).

```python
list_terminals(all)
```

---

## send_to_terminal

Send a command to a terminal pane.

```python
send_to_terminal(pane_id, text)
```

---

