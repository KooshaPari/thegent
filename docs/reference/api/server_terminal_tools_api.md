# server_terminal_tools API Reference

> **Source**: `src/thegent/mcp/server_terminal_tools.py`

Terminal/workstream/LSP MCP tool registration helpers.

---

## register_terminal_tools

Register terminal/workstream/LSP MCP tools.

---

## thegent_lsp_diagnostics

```python
thegent_lsp_diagnostics(file_path: str)
```

WL-109: return normalized LSP diagnostics for a file.

---

## thegent_lsp_hover

```python
thegent_lsp_hover(file_path: str, line: int, character: int)
```

WL-109: return hover information for a source position.

---

## thegent_lsp_symbol_lookup

```python
thegent_lsp_symbol_lookup(symbol_name: str, file_path: Any)
```

WL-109: lookup a symbol through the LSP adapter.

---

## thegent_terminal_attach

```python
thegent_terminal_attach(pane_id: str)
```

Get instructions to attach to a terminal session.

---

## thegent_terminal_inspect

```python
thegent_terminal_inspect(pane_id: str, last_lines: int)
```

Capture the content of a terminal pane.

---

## thegent_terminal_list

```python
thegent_terminal_list(all: bool)
```

List active terminal panes (tmux).

**Parameters**:

- `all`: Show all panes, not just Claude Code (default: False)

---

## thegent_terminal_send

```python
thegent_terminal_send(pane_id: str, text: str, enter: bool)
```

Send text/keys to a terminal pane.

---

## thegent_workstream_claim

```python
thegent_workstream_claim(item_id: str, agent_id: str)
```

Claim an item in the unified work stream.

---

## thegent_workstream_complete

```python
thegent_workstream_complete(item_id: str, agent_id: str)
```

Mark an item as complete in the unified work stream.

---

