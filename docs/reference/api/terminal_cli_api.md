# terminal_cli API Reference

> **Source**: `src/thegent/terminal_cli.py`

CLI implementation for terminal management.

---

## attach_terminal

```python
attach_terminal(pane_id: Any)
```

Attach to a terminal session.

---

## inspect_terminal

```python
inspect_terminal(pane_id: str)
```

View the last few lines of a terminal pane.

---

## list_terminals

```python
list_terminals(all: bool)
```

List active terminal panes (tmux).

---

## send_to_terminal

```python
send_to_terminal(pane_id: str, text: str)
```

Send a command to a terminal pane.

---

