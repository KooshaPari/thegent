# run_cmds_advanced API Reference

> **Source**: `src/thegent/cli/commands/run/run_cmds_advanced.py`

Thegent CLI run commands domain - extracted from cli.py (WL-124).

---

## deep_research_cmd

```python
deep_research_cmd(query: str, subreddits: str, output: Path)
```

Perform deep research using the Deep Research Protocol (DRP).

---

## replay_cmd

```python
replay_cmd(run_id: str, what_if_env: Any)
```

Decision replay and rationale snapshots (WP-4007).

---

## run_diff_cmd

```python
run_diff_cmd(run_a: str, run_b: str)
```

Compare two execution runs (WP-16001).

---

## takeover_cmd

```python
takeover_cmd(session_id: str)
```

Take over an active terminal session via tmux (WP-4008).

---

## terminal_route_cmd

```python
terminal_route_cmd(prompt: str, cd: Any)
```

Automatically route a prompt to an active terminal session if matching.

---

## trace_replay_cmd

```python
trace_replay_cmd(run_id: str)
```

WP-16001: Replay an execution trace in sandbox mode.

---

