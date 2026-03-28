# tools_prompt_and_handoff API Reference

> **Source**: `src/thegent/mcp/server/tools_prompt_and_handoff.py`

Prompt and handoff/governance wrapper registrations for MCP server.

---

## register_prompt_and_handoff_wrappers

---

## thegent_bg_task

```python
thegent_bg_task(agent: str, prompt: str, owner: Any)
```

Generate a prompt to start an agent task in the background.

Use thegent_bg tool to execute.

---

## thegent_create_wbs

```python
thegent_create_wbs(feature: str, scope: Any)
```

Generate a prompt to create a Work Breakdown Structure (WBS) for a feature.

Use thegent_run with a planning agent (e.g. cursor, claude) to execute.

---

## thegent_govern_vet

```python
thegent_govern_vet(run_id: str, policy: str, session: Any, dry_run: bool, org: Any, project: Any, environment: Any, policy_id: Any)
```

Vet a recorded run using Vetter policy checks (WL-098).

Equivalent to: thegent govern vet <run_id> [--policy <name>] [--session <path>] [--dry-run]

---

## thegent_handoff

```python
thegent_handoff(owner: str, cd: Any)
```

Create a handoff snapshot for shift handoff (WP-4006). Transfers active runs to snapshot.

Equivalent to: thegent orchestrate handoff <owner>

---

## thegent_run_agent

```python
thegent_run_agent(agent: str, prompt: str, cd: Any, mode: str)
```

Generate a prompt to run an agent synchronously.

Use thegent_run tool to execute.

---

