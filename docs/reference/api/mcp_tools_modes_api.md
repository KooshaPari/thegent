# mcp_tools_modes API Reference

> **Source**: `src/thegent/mcp_tools_modes.py`

MCP tools for Plan, Delegate, Discussion, Research, Validation modes and protocols.

Supports structured agent work: plans, elicitation briefs, research reports,
validation checklists, and mode-aware team orchestration.

---

## register_modes

Register Plan, Delegate, Discussion, Research, Validation, and Protocol tools.

```python
register_modes(mcp)
```

---

## thegent_dag_ready

List DAG task IDs that are ready (pending with all deps Union[done, cancelled]|skipped).
Use before thegent_dag_run to see what can be spawned.

```python
thegent_dag_ready(cd)
```

---

## thegent_dag_recover

Perform recovery playbook actions on the DAG.
action: retry-Union[failed, clear]-Union[stuck, reset]-Union[retries, fallback].

```python
thegent_dag_recover(cd, action)
```

---

## thegent_dag_run

Spawn agents for ready DAG tasks. Use thegent_dag_ready first to see ready tasks.
dry_run: list what would run without spawning. task: run only this task id.
max_parallel: cap concurrent running tasks.

```python
thegent_dag_run(cd, dry_run, task, max_parallel, lane)
```

---

## thegent_dag_sync

Sync DAG task status from session exit (running -> done/failed).
auto_run_next: spawn next ready tasks after sync (auto-spawn loop).

```python
thegent_dag_sync(cd, auto_run_next)
```

---

## thegent_discussion_add_question

Add a question (and optional answer) to a discussion session.
Use after thegent_discussion_start. Call thegent_discussion_finalize to save the brief.

```python
thegent_discussion_add_question(session_id, question, answer)
```

---

## thegent_discussion_finalize

Save elicitation brief to docs/briefs/. Use after discussion/elicitation phase.

```python
thegent_discussion_finalize(brief_content, brief_id, cd)
```

---

## thegent_discussion_start

Start a discussion/elicitation session. Returns session_id for thegent_discussion_add_question.

```python
thegent_discussion_start(topic, cd)
```

---

## thegent_plan_approve

Mark plan as approved. Writes approval marker (e.g. .approved) for downstream automation.

```python
thegent_plan_approve(plan_id, cd)
```

---

## thegent_plan_create

Create a new plan file from a prompt. Writes a structured template to docs/plans/.
Optionally reference brief_path (e.g. docs/briefs/ELICIT_xxx.md) for context.

```python
thegent_plan_create(prompt, plan_id, brief_path, cd)
```

---

## thegent_plan_get

Get plan content by ID or path. If plan_id is a path, read it. Else find in docs/plans/.

```python
thegent_plan_get(plan_id, cd)
```

---

## thegent_plan_save

Save plan content to docs/plans/. plan_id becomes filename (e.g. PLAN_oauth2.md).

```python
thegent_plan_save(content, plan_id, cd)
```

---

## thegent_plan_status

Get current plan status: plan file path, approval state, last modified.
Use when agent needs to know if a plan exists or where it is.

```python
thegent_plan_status(cd)
```

---

## thegent_protocol_get

Get protocol content by mode (discussion, research, validation) or name.

```python
thegent_protocol_get(mode, name, cd)
```

---

## thegent_protocol_list

List available protocols from .thegent/protocols/.
Returns protocol names and modes (discussion, research, validation).

```python
thegent_protocol_list(cd)
```

---

## thegent_research_finalize

Save research report to docs/research/. Use after research phase.

```python
thegent_research_finalize(report_content, report_id, cd)
```

---

## thegent_team_create

Create a team record for orchestration. mode: normal, discussion, research, plan, delegate, validation.
Returns team_id. Use thegent_team_delegate to assign work to teammates.

```python
thegent_team_create(prompt, mode, teammates, cd)
```

---

## thegent_team_delegate

Delegate a task to a teammate. Uses TeammateManager. teammate_id from agents/*.md.

```python
thegent_team_delegate(teammate_id, prompt, parent_run_id)
```

---

## thegent_team_list

List teams and delegations. Returns active teams and TeammateManager delegations.

```python
thegent_team_list(cd)
```

---

## thegent_validation_report

Get validation report if one exists. Use after validation phase.
protocol: optional protocol name to load checklist from.

```python
thegent_validation_report(cd, protocol)
```

---

