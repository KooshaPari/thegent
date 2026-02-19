# cli_impl API Reference

> **Source**: `src/thegent/cli_impl.py`

Thegent implementation layer: functions that return dict/str instead of printing.

When _resolve_cwd returns None (ambiguous), the caller (e.g. MCP tools) should
elicit before returning error. See gofastmcp.com/servers/elicitation.

---

## DagDocument

Parsed DAG session document with structure preserved for round-trip.

---

## RunnerProxy

**Inherits from**: `AgentRunner`

### Methods

#### RunnerProxy.run

```python
run(self, prompt, cwd, mode, timeout)
```

---

## bg_impl

Start a background run. Returns dict with keys: session_id, log_path, owner.

---

## dag_list_impl

List DAG tasks. Returns {frontmatter, tasks} or error.

```python
dag_list_impl(cd)
```

---

## dag_raw_impl

Get raw DAG markdown content. Returns markdown string or error message.

```python
dag_raw_impl(cd)
```

---

## do_next_impl

Find next actionable work items from WORK_STREAM, PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue.

Returns:
    dict with keys: next_items (list), empty_reason (str, optional), error (str, optional), sources_checked (list), count (int)

```python
do_next_impl(cd, limit)
```

---

## escalate_add_impl

WP-3008: Add a blocked run to the escalation queue.

```python
escalate_add_impl(run_id, reason, sla_minutes, owner, agent, lane, priority)
```

---

## escalate_approve_impl

WP-3008: Approve an escalation, marking it as approved in the queue (G-GP-05).

```python
escalate_approve_impl(run_id)
```

---

## escalate_list_impl

WP-3008: List escalation queue items (blocked runs with SLA).

```python
escalate_list_impl(past_sla_only, limit)
```

---

## escalate_resolve_impl

WP-3008: Mark an escalation item as resolved.

```python
escalate_resolve_impl(run_id, resolution)
```

---

## events_impl

List raw telemetry events from the run registry.

```python
events_impl(run_id, limit)
```

---

## explain_run_impl

WP-4002: Multi-tier explanation framework for run decisions.

```python
explain_run_impl(run_id)
```

---

## get_data_protection_status_impl

Return status of data protection and privacy controls (WP-3006).

---

## get_server_meta_impl

Return server metadata dict for thegent://meta resource.

---

## history_impl

List execution history from the run registry.

```python
history_impl(limit)
```

---

## inspect_impl

Get status and logs for one or more sessions. Returns list of {session_id, status, logs}.

```python
inspect_impl(session_ids, owner, tail, stderr, include_contract)
```

---

## list_agents_impl

List available agents. Returns list of {name, backend}. name is label (cursor) for display.

---

## list_droids_impl

List available droids. Returns list of droid names.

```python
list_droids_impl(cd)
```

---

## list_models_impl

List available models.

By default returns {provider: [model_names]}.
If include_contract=True, returns structured contract metadata for route discovery.
If by_model=True, returns {model_id: [provider, ...]} (R4, R5).

```python
list_models_impl(provider, use_scraped, refresh, include_contract, by_model)
```

---

## list_session_contracts_impl

Return sessions with route-request/route-contract metadata and contract quality signal.

```python
list_session_contracts_impl(owner, all, strict)
```

---

## logs_impl

Get logs from a background session. Returns log text.

```python
logs_impl(session_id, tail, stderr)
```

---

## monitor_impl

Monitor sessions and plan progress. Returns monitoring data.

Args:
    watch: If True, continuously monitor (returns immediately if False)
    interval: Update interval in seconds when watching
    format: Output format (json, rich, md)
    include_plan: Include plan progress data
    include_sessions: Include session status data

Returns:
    dict with keys: sessions, plan_progress, timestamp

```python
monitor_impl(watch, interval, format, include_plan, include_sessions)
```

---

## observe_summary_impl

FR-X08: Unified observability summary aggregating KPIs, drift, escalation.

```python
observe_summary_impl(limit, drift_window, structural_budget_pct, semantic_budget_pct, provider, top_escalations, trend_samples)
```

---

## ps_impl

List background sessions. Returns list of session dicts.

```python
ps_impl(owner, all, include_contract)
```

---

## purge_impl

WP-3006: Tiered retention purge implementation (G-GP-07).

```python
purge_impl(dry_run)
```

---

## run

```python
run(self, prompt, cwd, mode, timeout)
```

---

## run_impl

Run an agent or droid with the given prompt.
Returns dict with keys: stdout, stderr, exit_code, timed_out.
Model-first: agent=None, model set; provider hint for routing.

```python
run_impl(agent, prompt, cd, mode, timeout, full, model, provider, run_id, owner, include_contract, route_contract, route_request, lane, confidence, override_reason, contract_version, domain, idempotency_token, correlation_id, speculative, live, arbitration)
```

---

## runner_factory

```python
runner_factory(agent_name)
```

---

## session_contract_audit_impl

Return session contract audit rows with optional filtering and summary.

```python
session_contract_audit_impl(owner, all, missing_only, summary_only, strict)
```

---

## session_contract_health_gate_impl

Evaluate routing contract health against a minimum healthy-ratio gate.

```python
session_contract_health_gate_impl(owner, all, strict, min_healthy_ratio, policy_profile, no_worse_than_baseline, regression_tolerance)
```

---

## session_contract_health_report_impl

Return health report with issue taxonomy and owner-level breakdown.

```python
session_contract_health_report_impl(owner, all, strict, top_blocked, policy_profile, no_worse_than_baseline, regression_tolerance)
```

---

## session_contract_health_trend_impl

Return recent health snapshots and deltas for a given policy/query scope.

```python
session_contract_health_trend_impl(payload_type, owner, all, strict, policy_profile, min_healthy_ratio, top_blocked, limit)
```

---

## session_contract_negotiate_impl

WP-7001: Implementation of contract negotiation logic.

```python
session_contract_negotiate_impl(contract_id, supported_versions)
```

---

## session_meta_impl

Get full session metadata. Returns meta dict or error.

```python
session_meta_impl(session_id)
```

---

## sitback_dashboard_impl

Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.
For FastMCP tool/resource: single call replaces cockpit + terminal list + ps.
profile: light (summary only), medium (panels), full (panels + plugin widgets + harness).

```python
sitback_dashboard_impl(profile)
```

---

## status_impl

Get status of a background session.

```python
status_impl(session_id, include_contract)
```

---

## stop_impl

Stop a background session.

```python
stop_impl(session_id, force)
```

---

## sweep_impl

WP-3005: Policy drift sweep - runs drift detection, budget check, past-SLA escalations.

```python
sweep_impl(drift_window, structural_budget, semantic_budget, include_audit)
```

---

## update_calibration_impl

G-GP-09: Recalculate and persist calibration factors for all agents.

---

## wait_impl

Wait for a background session to complete.

```python
wait_impl(session_id, timeout)
```

---

## wait_next_impl

Block until next actionable work exists.

Args:
    cd: Working directory
    poll_interval: Poll interval in seconds
    timeout: Max wait time (0=unbounded)
    sources: Sources to check (dag, do_next, escalation, inbox)

Returns:
    dict with keys: available (bool), items (list), waited_seconds (float), action (dict), prompt_suggestion (str), id (str), source (str), description (str), elapsed_s (float)

```python
wait_next_impl(cd, poll_interval, timeout, sources)
```

---

## wrapped_run

---

