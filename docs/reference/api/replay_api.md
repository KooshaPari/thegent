# replay API Reference

> **Source**: `src/thegent/commands/replay.py`

CLI command: thegent replay [list | run | diff]

Sub-commands for the SimulationReplayEngine:
  list  — list available session files.
  run   — replay a session, printing events to stdout.
  diff  — compare two sessions and print a structured diff.

---

## replay_diff

```python
replay_diff(session_a: Annotated[(str, Any)], session_b: Annotated[(str, Any)], sessions_root: Annotated[(Any, Any)], output_json: Annotated[(bool, Any)])
```

Compare two sessions and print a structured diff.

Example::

    thegent replay diff <session_a_id> <session_b_id>
    thegent replay diff <id_a> <id_b> --json

---

## replay_list

```python
replay_list(sessions_root: Annotated[(Any, Any)], output_json: Annotated[(bool, Any)])
```

List all available session files.

Example::

    thegent replay list
    thegent replay list --json
    thegent replay list --sessions-root /custom/path

---

## replay_run

```python
replay_run(session_id: Annotated[(str, Any)], speed: Annotated[(float, Any)], sessions_root: Annotated[(Any, Any)], output_json: Annotated[(bool, Any)], from_event: Annotated[(int, Any)])
```

Replay a session, printing each event to stdout.

SESSION_ID may be a bare session ID (matched by prefix), a path to the
.json meta file, or a partial session stem.

Example::

    thegent replay run 20260219T231757Z-copilot-p21250-1f588a47
    thegent replay run ./path/to/session.json --json
    thegent replay run <id> --from 5 --speed 0

---

