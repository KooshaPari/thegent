# infra_resource_cmds API Reference

> **Source**: `src/thegent/cli/commands/infra_resource_cmds.py`

Thegent CLI resource management commands (concurrency, load, cost) - extracted from infra_cmds.py.

---

## concurrency_set_cmd

```python
concurrency_set_cmd(limit: int)
```

Set concurrency limit (updates .env file).

---

## concurrency_show_cmd

```python
concurrency_show_cmd(format: Any)
```

Show current concurrency limit and utilization (WP-5001).

---

## cost_status_cmd

```python
cost_status_cmd(format: Any)
```

Show cost budget utilization and cost-aware routing status (WP-5003).

---

## load_status_cmd

```python
load_status_cmd(format: Any)
```

Show load classification and safe-mode status (WP-5002).

---

## usage_cmd

```python
usage_cmd(format: Any, include_cost: bool)
```

Show plan usage: provider metrics from CLIProxyAPIPlus and cost status (WP-5003).

---

