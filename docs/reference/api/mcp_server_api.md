# mcp_server API Reference

> **Source**: `src/thegent/mcp_server.py`

FastMCP server for thegent.

---

## BearerAuthMiddleware

G-FM-01: Bearer token authentication for MCP HTTP endpoints.

**Inherits from**: `BaseHTTPMiddleware`

---

## get_default_cwd

Inject cwd from request meta (meta.cwd). Client can send meta.cwd in request.

```python
get_default_cwd(ctx)
```

---

## get_default_owner

Inject owner from request meta (meta.owner). Client can send meta.owner in request.

```python
get_default_owner(ctx)
```

---

## http_app

Return ASGI app with EventStore (mountable in FastAPI/Starlette).
stateless_http=True allows per-request JSON-RPC without SSE session (for simple clients, CI, verification).

```python
http_app(stateless_http)
```

---

## resource_agents

List available agents. Returns JSON array of {name, backend}.

---

## resource_dag

Get DAG from .factory/dag-session.md as {frontmatter, tasks} JSON.

---

## resource_meta

Server metadata: version, capabilities, health payload schema.

---

## resource_models

List models, optionally filtered by provider.

```python
resource_models(provider, include_contract)
```

---

## resource_models_contract

Return model routing contract schema metadata.

---

## resource_modes

Multi-agent orchestration modes: sequential_delegation, parallel_consensus, review_loop.

```python
resource_modes(mode)
```

---

## resource_observe_summary

Observe summary payload for contract KPIs, drift status, and escalation backlog.

```python
resource_observe_summary(limit, drift_window, structural_budget_pct, semantic_budget_pct, provider, trend_samples, top_escalations)
```

---

## resource_operations

Universal operation taxonomy: orchestrate, govern, recover, observe, plan.

```python
resource_operations(operation)
```

---

## resource_session_contract_health_gate

Contract health gate for CI/automation and policy enforcement.
Returns schema-aware payload with `schema_version` and `payload_type`.

```python
resource_session_contract_health_gate(owner, all, strict, min_healthy_ratio, policy_profile, no_worse_than_baseline, regression_tolerance)
```

---

## resource_session_contract_health_report

Contract health report for issue/owner triage and observability.
Returns schema-aware payload with `schema_version` and `payload_type`.

```python
resource_session_contract_health_report(owner, all, strict, top_blocked, policy_profile, no_worse_than_baseline, regression_tolerance)
```

---

## resource_session_contract_health_trend

Contract health trend snapshots for a scoped report/gate policy context.

```python
resource_session_contract_health_trend(payload_type, owner, all, strict, policy_profile, min_healthy_ratio, top_blocked, limit)
```

---

## resource_session_contracts

Contract audit for sessions including completeness summary.

```python
resource_session_contracts(owner, all, missing_only, summary_only, strict)
```

---

## resource_session_logs

Get logs from a background session. Use ?stderr=true for stderr, ?tail=N for last N lines.

```python
resource_session_logs(id, stderr, tail)
```

---

## resource_session_meta

Get session metadata (status, pid, owner) by ID.

```python
resource_session_meta(id, include_contract)
```

---

## resource_sessions

List all background sessions. Returns JSON array of session metadata.

```python
resource_sessions(include_contract)
```

---

## resource_workflow_gardening

Gardening workflow: converge to empty backlog and complete green.

---

## resource_workflow_triggers

Workflow instructions: idea→research→spec, quality green, next item. Injected on UserPromptSubmit.

---

## resource_workstream

Get the canonical WORK_STREAM.md content.

---

## run

Start the FastMCP server with EventStore and optional Docket.

```python
run(host, port)
```

---

## thegent_bg_task

Generate a prompt to start an agent task in the background.
Use thegent_bg tool to execute.

```python
thegent_bg_task(agent, prompt, owner)
```

---

## thegent_continuity_snapshot

WP-1009: Create a continuity snapshot for shift handoff.

Args:
    owner: Current owner
    run_ids: Run IDs to include in snapshot
    state_summary: Optional state summary dict
    next_steps: Optional list of next steps

Returns: ToolResult with snapshot_id

```python
thegent_continuity_snapshot(owner, run_ids, state_summary, next_steps)
```

---

## thegent_create_wbs

Generate a prompt to create a Work Breakdown Structure (WBS) for a feature.
Use thegent_run with a planning agent (e.g. cursor, claude) to execute.

```python
thegent_create_wbs(feature, scope)
```

---

## thegent_dag_status

For each DAG task with session_id, return id, status, session_id, session_status.
Equivalent to: thegent dag status

```python
thegent_dag_status(cd)
```

---

## thegent_ddg_search

Search DuckDuckGo for heavy web research.

Args:
    query: Search query string
    num_results: Max results to return (min: 1, max: 20, default: 5)

```python
thegent_ddg_search(query, num_results)
```

---

## thegent_do_next

Find the next actionable work items from PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue.

Use when user says "what next", "find the next thing to do", "pick next task".
Returns next_items with id, description, source, prompt_suggestion. Use prompt_suggestion with thegent_run or thegent_bg to execute.

Args:
    cd: Optional working directory (default: cwd)
    limit: Max items to return (min: 1, max: 50, default: 5)

```python
thegent_do_next(cd, limit)
```

---

## thegent_escalate_add

Add a blocked run to the escalation queue. Equivalent to: thegent govern escalate add

```python
thegent_escalate_add(run_id, reason, sla_minutes, owner, agent, lane, priority)
```

---

## thegent_escalate_approve

Approve an escalation (policy override). Equivalent to: thegent govern escalate approve

```python
thegent_escalate_approve(run_id)
```

---

## thegent_escalate_list

List escalation queue items (blocked runs). Equivalent to: thegent govern escalate list

```python
thegent_escalate_list(past_sla_only, limit)
```

---

## thegent_escalate_resolve

Mark an escalation item as resolved. Equivalent to: thegent govern escalate resolve

```python
thegent_escalate_resolve(run_id, resolution)
```

---

## thegent_handoff

Create a handoff snapshot for shift handoff (WP-4006). Transfers active runs to snapshot.
Equivalent to: thegent orchestrate handoff <owner>

```python
thegent_handoff(owner, cd)
```

---

## thegent_handoff_confirm

Incoming owner confirms handoff completeness. Equivalent to: thegent orchestrate handoff-confirm

```python
thegent_handoff_confirm(snapshot_id, incoming_owner, confidence)
```

---

## thegent_handoff_list

List pending handoff snapshots. Equivalent to: thegent orchestrate handoff-list

```python
thegent_handoff_list(limit)
```

---

## thegent_handoff_show

Show full handoff summary for a snapshot. Equivalent to: thegent orchestrate handoff-show

```python
thegent_handoff_show(snapshot_id)
```

---

## thegent_history

List execution history (recent runs). Equivalent to: thegent history --limit N

```python
thegent_history(limit)
```

---

## thegent_inbox_list

List unified inbox events (run registry + escalation) with optional filters.

Args:
    owner: Filter by owner
    agent: Filter by agent
    event_type: start|finish|feedback|pause|resume|escalation
    status: running|completed|failed
    sources: Comma-separated: registry,escalation (default: registry,escalation)
    limit: Max events to return (default: 50)

Returns: List of inbox events

```python
thegent_inbox_list(owner, agent, event_type, status, sources, limit)
```

---

## thegent_inbox_wait

Wait for next inbox event matching filters. Blocks until new event or timeout.

Args:
    owner: Filter by owner
    agent: Filter by agent
    event_type: start|finish|feedback|pause|resume|escalation
    status: running|completed|failed
    sources: Comma-separated: registry,escalation (default: registry,escalation)
    poll_interval: Poll interval in seconds (default: 2.0)
    timeout: Max wait seconds (default: 60, 0=unbounded)

Returns: New events that arrived, or empty list on timeout

```python
thegent_inbox_wait(owner, agent, event_type, status, sources, poll_interval, timeout)
```

---

## thegent_inspect

Multi-session status + logs.

Args:
    session_ids: Session ID(s) to inspect. Omit when using owner.
    owner: Inspect all sessions for this owner (alternative to session_ids)
    tail: Log lines per session (default: 50)
    stderr: Show stderr instead of stdout (default: False)

Returns: ToolResult with list of {session_id, status, logs}

```python
thegent_inspect(session_ids, owner, tail, stderr, include_contract)
```

---

## thegent_list_agents

List available agents for routing.

Returns: JSON string with list of {name, backend}

---

## thegent_list_droids

List available droids.

Args:
    cd: Optional working directory (or use meta.cwd in request)
    Returns: JSON string with list of droid names

```python
thegent_list_droids(cd, default_cwd)
```

---

## thegent_list_models

List available models (optionally filtered by provider).

Args:
    provider: Optional provider filter (minimax, glm, cursor, claude, codex; gemini/copilot via Codex proxy)
    include_contract: If true, return route metadata payload instead of provider/model map.
    by_model: If true, return {model_id: [provider, ...]} for routing (R5).

Returns: JSON string with {provider: [model_names]}, {model_id: [providers]}, or contract payload.

```python
thegent_list_models(provider, include_contract, by_model)
```

---

## thegent_list_modes

List multi-agent orchestration modes (G-KD-04).

Args:
    mode: Optional filter (sequential_delegation | parallel_consensus | review_loop)

Returns: JSON with modes, phases, use_case, risk_profile, selection_hint.

```python
thegent_list_modes(mode)
```

---

## thegent_list_operations

List universal operation taxonomy: orchestrate, govern, recover, observe, plan.

Args:
    operation: Optional filter (orchestrate | govern | recover | observe | plan)

Returns: JSON with operations and their commands/mcp_tools.

```python
thegent_list_operations(operation)
```

---

## thegent_logs

Read session log output with optional tail limit.

Args:
    session_id: Session ID to query
    tail: Number of lines to return from end (optional, default: all)
    stderr: Include stderr instead of stdout (default: False)

Returns: Log text

```python
thegent_logs(session_id, tail, stderr)
```

---

## thegent_observe_summary

Get unified observability summary for KPIs, drift budget, and escalations.

```python
thegent_observe_summary(limit, drift_window, structural_budget_pct, semantic_budget_pct, provider, trend_samples, top_escalations)
```

---

## thegent_pause

WP-1009: Pause a background session (register pause event in registry).

Args:
    session_id: Session ID to pause
    reason: Reason for pause (default: Manual pause)

Returns: ToolResult with status

```python
thegent_pause(session_id, reason)
```

---

## thegent_plan_analyze

Run planning simulation overlays (XD1–XD3): PERT, resource contention, continuity risk.
Equivalent to: thegent plan analyze
If no flags set, runs all three overlays.

```python
thegent_plan_analyze(cd, pert, resources, continuity)
```

---

## thegent_plan_get_next

Get first work item prompt for scripting. Use with thegent_run or thegent_bg.
Equivalent to: thegent plan get-next

```python
thegent_plan_get_next(cd)
```

---

## thegent_plan_incorporate

Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md BACKLOG.
Equivalent to: thegent plan incorporate

```python
thegent_plan_incorporate(cd, dry_run)
```

---

## thegent_plan_progress

Show recent runs (work-package progress). Alias for thegent_history with smaller default.
Equivalent to: thegent plan progress --limit N

```python
thegent_plan_progress(limit)
```

---

## thegent_plan_wait_next

Block until next actionable work exists (DAG ready, do_next, escalation, inbox).
Equivalent to: thegent plan wait-next

```python
thegent_plan_wait_next(cd, poll, timeout, sources)
```

---

## thegent_ps

List background sessions for discovery.

Args:
    owner: Filter by owner tag (optional)
    all: Include completed/stopped sessions (default: False)
    include_contract: Include resolved route contract/request metadata (optional)

Returns: JSON string with list of sessions

```python
thegent_ps(owner, all, include_contract)
```

---

## thegent_resolve_model_route

Resolve a model to a concrete routing target.

Args:
    model: Model identifier (alias or canonical)
    provider: Optional provider hint
    policy: Routing policy: prefer_direct, prefer_proxy, failover

Returns: JSON contract payload with resolved route if available.

```python
thegent_resolve_model_route(model, provider, policy)
```

---

## thegent_resume

WP-1009: Resume a paused session (register resume event in registry).

Args:
    session_id: Session ID to resume

Returns: ToolResult with status

```python
thegent_resume(session_id)
```

---

## thegent_retry

Retry a failed run by run_id. Looks up prompt/agent from registry and re-runs.
Equivalent to: thegent retry <run_id>

```python
thegent_retry(run_id, agent_override, failover, cd, override_reason)
```

---

## thegent_run_agent

Generate a prompt to run an agent synchronously.
Use thegent_run tool to execute.

```python
thegent_run_agent(agent, prompt, cd, mode)
```

---

## thegent_session_contract_health_gate

Evaluate session contract health against a minimum ratio gate.

Returns a unified health payload with `schema_version`, `payload_type`,
`pass`, `status`, `total_sessions`, `healthy_sessions`, `unhealthy_sessions`,
`blocked_sessions_count`, `blocked_ratio`, and `blocked_sessions`.

```python
thegent_session_contract_health_gate(owner, all, strict, min_healthy_ratio, policy_profile, no_worse_than_baseline, regression_tolerance)
```

---

## thegent_session_contract_health_report

Get contract health report with issue taxonomy and owner-level breakdown.

Returns a unified health payload with `schema_version`, `payload_type`,
`status`, `total_sessions`, `healthy_sessions`, `unhealthy_sessions`,
`blocked_sessions_count`, `blocked_ratio`, `issue_breakdown`, and `owner_breakdown`.

```python
thegent_session_contract_health_report(owner, all, strict, top_blocked, policy_profile, no_worse_than_baseline, regression_tolerance)
```

---

## thegent_session_contract_health_trend

Get trend snapshots and deltas for session contract health scopes.

```python
thegent_session_contract_health_trend(payload_type, owner, all, strict, policy_profile, min_healthy_ratio, top_blocked, limit)
```

---

## thegent_session_contracts

List session routing contract metadata and report completeness.

```python
thegent_session_contracts(owner, all, missing_only, summary_only, strict)
```

---

## thegent_sharecli_status

Get status from sharecli harness.

---

## thegent_status

Get session status for quick health check.

Args:
    session_id: Session ID to query

Returns: ToolResult with session status and metadata

```python
thegent_status(session_id, include_contract)
```

---

## thegent_stop

Stop a background session.

Args:
    session_id: Session ID to stop
    force: Use SIGKILL instead of SIGTERM (default: False)

Returns: ToolResult with status

```python
thegent_stop(session_id, force)
```

---

## thegent_suggest_mode

WP-Y1: Suggest multi-agent mode based on risk, urgency, confidence (FR-032).

Args:
    risk: risk_profile (low | medium | high)
    urgency: urgency tier (normal | high | critical)
    confidence: confidence score 0.0-1.0

Returns: JSON with mode, reason, phases, and selection inputs.

```python
thegent_suggest_mode(risk, urgency, confidence)
```

---

## thegent_terminal_attach

Get instructions to attach to a terminal session.

```python
thegent_terminal_attach(pane_id)
```

---

## thegent_terminal_inspect

Capture the content of a terminal pane.

```python
thegent_terminal_inspect(pane_id, last_lines)
```

---

## thegent_terminal_list

List active terminal panes (tmux).

Args:
    all: Show all panes, not just Claude Code (default: False)

```python
thegent_terminal_list(all)
```

---

## thegent_terminal_route

Route a prompt to an active terminal session if matching. Falls back to thegent_run if none found.
Equivalent to: thegent route <prompt>

```python
thegent_terminal_route(prompt, cd)
```

---

## thegent_terminal_send

Send text/keys to a terminal pane.

```python
thegent_terminal_send(pane_id, text, enter)
```

---

## thegent_wait

Block until session completes or timeout.

Args:
    session_id: Session ID to wait for
    timeout: Timeout in seconds (optional)

Returns: ToolResult with final status and exit code

```python
thegent_wait(session_id, timeout)
```

---

## thegent_workflow_gardening

Instructions for gardening: check gov traceability, tests, plan items; dispatch; converge to empty backlog and complete green.
Use when user says "garden", "converge", "empty backlog", "complete green".

---

## thegent_workflow_idea

Instructions for idea/task prompts: dump research, create specs, add work items.
Use when user gives research/explore/build/implement/design/create/feature prompts.

```python
thegent_workflow_idea(idea)
```

---

## thegent_workflow_next_item

Instructions to find and execute the next work item from the unified stream.
Use when user says "find the next thing to do", "what next", "pick next".

---

## thegent_workflow_quality_green

Instructions to run full quality pipeline until green.
Use when user says "get task quality green", "quality green", "make quality pass".

---

## thegent_workstream_claim

Claim an item in the unified work stream.

```python
thegent_workstream_claim(item_id, agent_id)
```

---

## thegent_workstream_complete

Mark an item as complete in the unified work stream.

```python
thegent_workstream_complete(item_id, agent_id)
```

---

