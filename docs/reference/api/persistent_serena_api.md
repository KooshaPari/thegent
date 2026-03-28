# persistent_serena API Reference

> **Source**: `src/thegent/lsp/persistent_serena.py`

Persistent Serena LSP daemon (MTSP-04).

Consolidates code intelligence into a single persistent Serena daemon
to reduce the overhead of spawning separate LSP servers per agent session.

---

## PersistentSerenaDaemon

Persistent Serena LSP daemon (MTSP-04).

### Methods

#### PersistentSerenaDaemon.__init__

```python
__init__(self: Any, port: int, host: str)
```

---

#### PersistentSerenaDaemon.get_mcp_config

```python
get_mcp_config(self: Any)
```

Get the MCP configuration to connect to this persistent daemon.

---

#### PersistentSerenaDaemon.is_running

```python
is_running(self: Any)
```

Check if the Serena daemon is running.

---

---

## get_mcp_config

```python
get_mcp_config(self: Any)
```

Get the MCP configuration to connect to this persistent daemon.

---

## is_running

```python
is_running(self: Any)
```

Check if the Serena daemon is running.

---

