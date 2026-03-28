# mcp API Reference

> **Source**: `src/thegent/cli/apps/mcp.py`

Top-level MCP command namespace.

This module exposes MCP lifecycle and migration commands directly under `thegent mcp`.
It mirrors the existing `thegent sys mcp` behavior while adding first-class subcommands
that are expected across tests/docs (install/up/down/prune/service/migrate etc.).

---

## mcp_down_cmd

---

## mcp_fix

```python
mcp_fix(client: Any) -> None
```

---

## mcp_hmr_cmd

```python
mcp_hmr_cmd(project_root: Path, debounce_s: float) -> None
```

---

## mcp_install

```python
mcp_install(target: str, url: Any, workspace: Any) -> None
```

---

## mcp_introspect

---

## mcp_migrate_unimount

```python
mcp_migrate_unimount(client: str, url: Any, workspace: Any) -> None
```

---

## mcp_prune_cmd

```python
mcp_prune_cmd(force: bool, dry_run: bool, parent_pid: Any, shadow_age_hours: int, log_age_days: int) -> None
```

---

## mcp_prune_periodic

```python
mcp_prune_periodic(action: str) -> None
```

---

## mcp_reload_cmd

---

## mcp_restart_cmd

---

## mcp_service

```python
mcp_service(action: str) -> None
```

---

## mcp_spotlight_exclude

---

## mcp_status

---

## mcp_stdio

---

## mcp_up_cmd

---

