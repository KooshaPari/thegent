# cli_tooling API Reference

> **Source**: `src/thegent/cli/commands/cli_tooling.py`

WL-136 B90-W2-D2: Tooling-surface CLI commands.

Commands extracted from cli.py that belong to the tooling surface
(dev utilities, research, benchmarking, drift monitoring, roadmap generation)
per the WL-136 two-surface split: core runtime vs tooling/test/research.

These commands are NOT part of the core production runtime path. They serve
development, research, and QA workflows. Importing this module from the core
runtime path is forbidden per the WL-136 surface boundary contract.

# @trace WL-136 B90-W2-D2

---

## audit_verify_cmd

```python
audit_verify_cmd(format: Any)
```

Verify the integrity of the execution run registry.

Tooling surface: QA/dev audit utility.
Not part of production runtime path.

---

## benchmark_cmd

Report orchestration performance metrics (WP-6001).

Tooling surface: dev utility for assessing run latency and SLO compliance.
Not part of production runtime path.

---

## deep_research_cmd

```python
deep_research_cmd(query: str, subreddits: Any, output: Any)
```

Perform deep research using the Deep Research Protocol (DRP).

Tooling surface: research utility. Not part of production runtime path.

---

## drift_monitor_cmd

```python
drift_monitor_cmd(prompt: str, agents: list[str])
```

Monitor drift across multiple providers for the same prompt (WP-3001).

Tooling surface: dev QA utility for detecting provider divergence.
Not part of production runtime path.

---

## roadmap_cmd

Successor roadmap generation (WP-6004).

Tooling surface: dev/PM utility for gap analysis and next-phase planning.
Not part of production runtime path.

---

