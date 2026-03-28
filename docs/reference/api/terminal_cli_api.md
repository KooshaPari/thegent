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

## inspect_terminal_alias

```python
inspect_terminal_alias(pane_id: str)
```

Alias for terminal inspect.

---

## list_terminals

```python
list_terminals(all: bool)
```

List active terminal panes (tmux).

---

## list_terminals_alias

```python
list_terminals_alias(all: bool)
```

Alias for terminal list.

---

## send_to_terminal

```python
send_to_terminal(pane_id: str, text: str)
```

Send a command to a terminal pane.

---

## send_to_terminal_alias

```python
send_to_terminal_alias(pane_id: str, text: str)
```

Alias for terminal send.

---

