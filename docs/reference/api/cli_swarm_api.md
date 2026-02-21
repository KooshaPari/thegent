# cli_swarm API Reference

> **Source**: `src/thegent/cli/commands/cli_swarm.py`

CLI commands for swarm management — per-owner usage tracking (swarm-usage-tracking).

---

## swarm_usage

```python
swarm_usage(session_dir: Any, owner: Any, format: str)
```

Show per-owner concurrency usage statistics.

Displays active slot counts, total runs, and average elapsed time for
each owner (agent/user/project) tracked by the ConcurrencyController.

---

