# cli_legacy API Reference

> **Source**: `src/thegent/cli_legacy.py`

Thegent CLI commands.

---

## LazyConsole

Lazy-loaded rich console to speed up CLI startup.

### Methods

---

## RunRegistry

---

## ThegentSettings

---

## archive_cmd

```python
archive_cmd(days: Any, domain: Any, tier: Any)
```

Archive old sessions (WP-6005). WP-3006: tiered retention (hot 30d, cold 1yr).

---

## audit_verify_cmd

```python
audit_verify_cmd(format: Any)
```

Verify the integrity of the execution run registry.

---

## benchmark_cmd

Report orchestration performance metrics (WP-6001).

---

## bg_cmd

---

## cliproxy_login_cmd

```python
cliproxy_login_cmd(provider: str, force: bool)
```

Run login for provider. Unified flow: open URL + prompt for API key. Preflight checks existing credentials.

---

## closure_pack_cmd

```python
closure_pack_cmd(cd: Any)
```

Generate a formal closure pack for the current DAG session (WP-6002/6008/FR-024).

---

## cockpit_cmd

Show high-level operator cockpit summary.

---

## compliance_plugin_check_cmd

```python
compliance_plugin_check_cmd(plugin_id: str, signature: str)
```

Verify a plugin contract (WP-15003).

---

## compliance_redact_cmd

```python
compliance_redact_cmd(text: str)
```

Test PII/Secret redaction (WP-15005).

---

## compliance_report_cmd

```python
compliance_report_cmd(format: Any, output: Any)
```

Generate compliance evidence retention report (WP-3006).

---

## compliance_siem_test_cmd

```python
compliance_siem_test_cmd(message: str, severity: str)
```

Test SIEM event egress (WP-15001).

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

Show current concurrency limit and utilization.

---

## config_check_cmd

```python
config_check_cmd(format: Any)
```

Validate config and report issues (DX-010, ROB-013).

---

## contracts_conformance_cmd

```python
contracts_conformance_cmd(format: Any, check_drift: bool, drift_window: int)
```

Run provider adapter conformance tests.

---

## contracts_registry_cmd

```python
contracts_registry_cmd(format: Any)
```

Show the contract registry and compatibility matrix.

---

## cost_status_cmd

```python
cost_status_cmd(format: Any)
```

Show cost budget utilization and cost-aware routing status (WP-5003).

---

## cost_values_cmd

```python
cost_values_cmd(format: Any)
```

Show cost values ($/1k tokens) for all model-provider pairs.

Uses CLIProxyAPIPlus metrics when reachable; falls back to static values.

---

## dag_add_cmd

```python
dag_add_cmd(task_id: str, agent: str, prompt: str, cd: Any, depends_on: Any, contract_version: Any)
```

Add a task to the DAG. XA4: contract_version in task metadata.

---

## dag_cancel_cmd

```python
dag_cancel_cmd(task_id: str, cd: Any)
```

Cancel a task (set status to cancelled).

---

## dag_checkpoint_cmd

```python
dag_checkpoint_cmd(cd: Any, reason: str)
```

Create a point-in-time checkpoint of the DAG state.

---

## dag_checkpoints_cmd

```python
dag_checkpoints_cmd(limit: int)
```

List recent DAG checkpoints.

---

## dag_list_cmd

```python
dag_list_cmd(cd: Any, format: Any)
```

Parse and display DAG session from .factory/dag-session.md.

---

## dag_probe_cmd

```python
dag_probe_cmd(cd: Any, baseline_id: Any)
```

Compare current DAG state with a baseline checkpoint to detect regressions.

---

## dag_ready_cmd

```python
dag_ready_cmd(cd: Any, format: Any)
```

List task ids that are ready (pending with all deps done|cancelled|skipped).

---

## dag_reconcile_cmd

```python
dag_reconcile_cmd(cd: Any)
```

Reconcile DAG state with reality (clean up stuck 'running' tasks).

---

## dag_recover_cmd

```python
dag_recover_cmd(cd: Any, action: str)
```

Perform recovery playbook actions on the DAG.

---

## dag_remove_cmd

```python
dag_remove_cmd(task_id: str, cd: Any)
```

Remove a task from the DAG.

---

## dag_rollback_cmd

```python
dag_rollback_cmd(checkpoint_id: Any, cd: Any)
```

Rollback DAG state to a specific checkpoint.

---

## dag_run_cmd

```python
dag_run_cmd(cd: Any, dry_run: bool, task: Any, max_parallel: Any, lane: Any, check_drift: bool, contract_version: Any)
```

Spawn thegent bg for each ready task; update status=running and session_id.

---

## dag_status_cmd

```python
dag_status_cmd(cd: Any, format: Any)
```

For each task with session_id show id, status, session_id, session_status (running/exited:rc).

---

## dag_sync_cmd

```python
dag_sync_cmd(cd: Any, auto_run_next: bool)
```

For tasks with session_id and status=running, if pid not running set status=done or failed from rc.

If --auto-run-next, spawn next ready tasks after sync.

---

## dag_update_cmd

```python
dag_update_cmd(task_id: str, cd: Any, status: Any, session_id: Any, prompt: Any, agent: Any, depends_on: Any, contract_version: Any)
```

Update a task in the DAG. XA4: contract_version in task metadata.

---

## dag_validate_cmd

```python
dag_validate_cmd(cd: Any)
```

Validate DAG session from .factory/dag-session.md. Exit 2 on validation errors.

---

## data_protection_cmd

```python
data_protection_cmd(format: Any)
```

Show status of data protection and privacy controls.

---

## deep_research_cmd

```python
deep_research_cmd(query: str, subreddits: str, output: Path)
```

Perform deep research using the Deep Research Protocol (DRP).

---

## deferral_list_cmd

List all currently deferred tasks (WP-5004).

---

## deferral_resume_cmd

```python
deferral_resume_cmd(run_id: str)
```

Manually resume a deferred task (WP-5004).

---

## discovery_parse_cmd

```python
discovery_parse_cmd(text: str, register: bool, ppid: int)
```

Parse CLI output for session information and register them.

---

## discovery_register_cmd

```python
discovery_register_cmd(agent: str, pid: int, ppid: int, cwd: str, command: Any, args: Any, session_id: Any, token_usage_json: Any, mcp_errors: Any)
```

Register or update a discovered external agent (WP-4008).

---

## discovery_scan_cmd

```python
discovery_scan_cmd(format: Any)
```

Scan process tree for agent CLI sessions and auto-register them.

Detects running cursor-agent, Claude Code, and Codex processes,
extracts session IDs from --resume= when present, and registers them
for introspection via thegent ps, terminal takeover, and inbox.

---

## dlq_list_cmd

```python
dlq_list_cmd(status: Any, format: Any)
```

List items in the Dead-Letter Queue (WP-Y2/WP-2008).

---

## drift_cmd

```python
drift_cmd(window: int, format: Any, structural_budget: float, semantic_budget: float)
```

Detect significant drift in contract performance and check alert budgets (G-RV-07).

---

## drift_monitor_cmd

```python
drift_monitor_cmd(prompt: str, agents: list[str])
```

Monitor drift across multiple providers for the same prompt (WP-3001).

---

## escalate_add_cmd

```python
escalate_add_cmd(run_id: str, reason: str, sla_minutes: int, owner: Any, lane: str, priority: int)
```

Add a blocked run to the escalation queue (WP-3008).

---

## escalate_approve_cmd

```python
escalate_approve_cmd(run_id: Any)
```

Approve an escalation, recording an override for the owner (G-GP-05).

---

## escalate_list_cmd

```python
escalate_list_cmd(past_sla_only: bool, limit: int, format: Any)
```

List governance escalation queue (WP-3008).

---

## escalate_resolve_cmd

```python
escalate_resolve_cmd(run_id: Any, resolution: str)
```

Mark an escalation item as resolved (WP-3008).

---

## events_cmd

```python
events_cmd(run_id: Any, limit: int, format: Any)
```

List raw telemetry events.

---

## explain_cmd

```python
explain_cmd(run_id: Any)
```

Show detailed explanation for an agent run (WP-4002).

---

## explorer_cmd

Launch the terminal explorer TUI.

---

## fallbacks_cmd

```python
fallbacks_cmd(run_id: Any)
```

Show safe fallback options for a failed or blocked run (WP-4003).

---

## feedback_cmd

```python
feedback_cmd(run_id: Any, score: float, note: Any)
```

Provide operator feedback for a specific run.

---

## forensics_snapshot_cmd

```python
forensics_snapshot_cmd(run_id: Any, phase: Any)
```

Take a forensics snapshot of an agent run (WP-3002).

---

## get_exit_message

---

## govern_configure_cmd

```python
govern_configure_cmd(cd: Any, force: bool)
```

Bootstrap governance: create contracts/health-targets.json if missing.

---

## govern_cost_cmd

```python
govern_cost_cmd(owner: Any, days: int, format: Any)
```

Show daily cost aggregation (FR-GOV-002).

---

## govern_go_cycle_cmd

```python
govern_go_cycle_cmd(cd: Any, force: bool, format: Any)
```

Run a single governance cycle.

---

## govern_go_health_cmd

```python
govern_go_health_cmd(cd: Any, format: Any)
```

Show current health score (composite 0-100, band, per-dimension breakdown).

---

## govern_go_status_cmd

```python
govern_go_status_cmd(cd: Any)
```

Show current governance status (state, cycle_id, shutdown_requested).

---

## govern_go_watch_cmd

```python
govern_go_watch_cmd(cd: Any, interval: int, max_cycles: Any)
```

Run continuous governance mode.

---

## guardrails_check_cmd

```python
guardrails_check_cmd(prompt: str, agent: Any, model: Any)
```

Check a prompt against active guardrails (FR-GOV-003..006).

---

## guardrails_show_cmd

Show active guardrail configuration (FR-GOV-007).

---

## handoff_cmd

```python
handoff_cmd(owner: str)
```

Create a continuity snapshot for a shift handoff (WP-4006, WP-3008).

---

## handoff_confirm_cmd

```python
handoff_confirm_cmd(snapshot_id: str, incoming_owner: str, confidence: float)
```

Incoming owner confirms handoff completeness (WP-3008, WP-4006).

---

## handoff_list_cmd

```python
handoff_list_cmd(limit: int, format: Any)
```

List pending handoff snapshots (WP-4006).

---

## handoff_show_cmd

```python
handoff_show_cmd(snapshot_id: str, format: Any)
```

Show full handoff summary (state, evidence, next steps) for a snapshot (WP-4006).

---

## history_cmd

```python
history_cmd(limit: int, format: Any)
```

List execution run history (sync and background).

---

## inbox_list_cmd

```python
inbox_list_cmd(owner: Any, agent: Any, event_type: Any, status: Any, sources: Any, limit: int, format: Any)
```

List unified inbox events (run registry + escalation) with optional filters.

---

## inbox_wait_cmd

```python
inbox_wait_cmd(owner: Any, agent: Any, event_type: Any, status: Any, sources: Any, poll: float, timeout: float, notify: bool, format: Any)
```

Wait for next inbox event matching filters. Blocks until new event or timeout.

---

## inspect_cmd

```python
inspect_cmd(session_ids: Any, owner: Any, tail: int, stderr: bool, format: Any, include_contract: bool)
```

Show status and logs for one or more sessions. No shell loop needed.

---

## interruption_list_cmd

```python
interruption_list_cmd(limit: int, format: Any)
```

List recent interruptions (WP-4004).

---

## interruption_snooze_cmd

```python
interruption_snooze_cmd(alert_id: str, minutes: int, itype: str)
```

Snooze an alert; expires → auto-escalation (WP-4004).

---

## list_agents_cmd

List available agents.

---

## list_droids_cmd

```python
list_droids_cmd(cd: Any)
```

List available droids.

---

## list_model_contract_schema_cmd

Print the route contract schema metadata used by contract views.

---

## list_models_cmd

```python
list_models_cmd(provider: Any, by_model: bool, refresh: bool, include_contract: bool)
```

List available models (scraped from CLIs/config).

---

## load_status_cmd

```python
load_status_cmd(format: Any)
```

Show load classification and safe-mode status (WP-5002).

---

## logs_cmd

```python
logs_cmd(session_id: Any, follow: bool, stderr: bool, tail: int, timeout: int, harness: bool) -> None
```

---

## loop_cmd

```python
loop_cmd(prompt: str, todo_spec: str, agent: Any, checker: str, loop_mode: str, cd: Any)
```

Run a Lifecycle loop with Checker oversight.

---

## loop_send_cmd

```python
loop_send_cmd(session_id: Any, prompt: str)
```

Send a prompt to a running Lifecycle loop (human or agent takeover).

---

## loop_stop_cmd

```python
loop_stop_cmd(session_id: Any)
```

Send STOP signal to a running Lifecycle loop.

---

## metrics_cmd

```python
metrics_cmd(format: Any, no_cache: bool, limit: int)
```

Show cost, speed, and quality indices for all model-provider pairs (unified view).

---

## migration_cmd

```python
migration_cmd(contract_id: str, version: str, format: Any)
```

Evaluate migration status for a contract version.

---

## modes_cmd

```python
modes_cmd(format: Any, mode: Any)
```

List multi-agent orchestration modes (sequential_delegation, parallel_consensus, review_loop).

---

## monitor_cmd

```python
monitor_cmd(interval: float)
```

Monitor sessions and plan progress in real-time (WP-8001).

---

## observe_summary_cmd

```python
observe_summary_cmd(limit: int, drift_window: int, structural_budget: float, semantic_budget: float, format: Any, provider: Any, trend_samples: int, top_escalations: int)
```

FR-X08: Unified observability summary (KPIs, drift, escalation).

---

## on_progress

```python
on_progress(iteration: int, total: int, message: str) -> None
```

---

## on_worker_output

```python
on_worker_output(text: str) -> None
```

---

## operations_cmd

```python
operations_cmd(format: Any, operation: Any)
```

List universal operation taxonomy (orchestrate, govern, recover, observe, plan).

---

## pause_cmd

```python
pause_cmd(session_id: Any)
```

Pause a background session (register pause event).

---

## plan_analyze_cmd

```python
plan_analyze_cmd(cd: Any, pert: bool, resources: bool, continuity: bool, format: Any)
```

Run planning simulation overlays (XD1–XD3): PERT, resource contention, continuity risk.

---

## plan_claim_cmd

```python
plan_claim_cmd(item_id: str, agent_id: Any, cd: Any)
```

Claim an item in the unified work stream.

---

## plan_complete_cmd

```python
plan_complete_cmd(item_id: str, agent_id: Any, cd: Any)
```

Mark an item as complete in the unified work stream.

---

## plan_do_next_cmd

```python
plan_do_next_cmd(cd: Any, limit: int, format: Any)
```

Find next actionable work items from WORK_STREAM, PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue.

---

## plan_get_next_cmd

```python
plan_get_next_cmd(cd: Any, format: Any)
```

Get first work item prompt for scripting. Use: PROMPT=$(thegent plan get-next)

---

## plan_incorporate_cmd

```python
plan_incorporate_cmd(cd: Any, dry_run: bool)
```

Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md. Preserves CLAIMED and COMPLETED.

---

## plan_loop_cmd

```python
plan_loop_cmd(cd: Any, max_iterations: int, sleep_seconds: float, agent: str, dry_run: bool)
```

Loop: get next item -> run bg -> repeat until no items or --max reached.

---

## plan_progress_cmd

```python
plan_progress_cmd(limit: int, format: Any)
```

Show recent runs (work-package progress). Alias for history --limit N.

---

## plan_wait_next_cmd

```python
plan_wait_next_cmd(cd: Any, poll: float, timeout: float, sources: Any, format: Any)
```

Block until next actionable work exists (DAG ready, do_next, escalation, inbox).

---

## policy_check_cmd

```python
policy_check_cmd(agent: str, model: Any, lane: str, confidence: float)
```

Evaluate a hypothetical run against governance policies (WP-3001).

---

## policy_purge_cmd

```python
policy_purge_cmd(dry_run: bool)
```

Purge expired history based on tiered retention (WP-3006).

---

## policy_show_cmd

Show active governance policies and thresholds.

---

## project_list_cmd

List all registered projects (WP-4008).

---

## project_register_cmd

```python
project_register_cmd(path: Path, name: Any)
```

Register a new project (WP-4008).

---

## prompt_key

```python
prompt_key(msg: str) -> str
```

---

## ps_cmd

```python
ps_cmd(all_sessions: bool, owner: Any, format: Any, include_contract: bool) -> None
```

---

## purge_cmd

```python
purge_cmd(dry_run: bool)
```

WP-3006: Tiered retention purge (G-GP-07).

---

## quality_index_cmd

```python
quality_index_cmd(format: Any, no_cache: bool)
```

Show quality index (0-1) for all models.

Uses benchmarks.json (Terminal Bench 2.0, SWE-Bench, AIME) when available;
falls back to Route.accuracy_score.

---

## queue_list_cmd

```python
queue_list_cmd(watch: bool)
```

WP-7002: List pending prompts in the queue.

---

## recover_status_cmd

Show current recovery status (WP-7001).

---

## release_pack_cmd

```python
release_pack_cmd(version: str)
```

Automated release documentation packaging (WP-12009).

---

## replay_cmd

```python
replay_cmd(run_id: str, what_if_env: Any)
```

Decision replay and rationale snapshots (WP-4007).

---

## resolve_model_route_cmd

```python
resolve_model_route_cmd(model: str, provider: Any, policy: str, quality_floor: float, lane: Any)
```

Resolve a model to a preferred route and emit contract-style output.

---

## resume_cmd

```python
resume_cmd(session_id: Any)
```

Resume a background session (register resume event).

---

## retry_cmd

```python
retry_cmd(run_id: Any, agent: Any, failover: bool, cd: Any, override_reason: Any)
```

Retry a failed run. With no run_id, list recent failed runs.

---

## roadmap_cmd

Successor roadmap generation (WP-6004).

---

## rules_sync_cmd

```python
rules_sync_cmd(force: bool, check: bool, cd: Any)
```

Sync CLAUDE.md to other platform-specific rule files (AGENTS.md, Cursor, Codex).

---

## run_cmd

```python
run_cmd(agent: Any, prompt: str, cd: Any, mode: str, timeout: int, full: bool, live: bool, model: Any, provider: Any, failover: bool, routing: Any, include_contract: bool, run_id: Any, lane: str, idempotency_token: Any, confidence: Any, arbitration: Any, override_reason: Any, contract_version: Any, domain: Any, speculative: bool, search: bool, debug: bool, task_id: Any, shadow: bool, lock: Any, remote: Any)
```

Run an agent or droid with the given prompt. Model-first: agent=None, model set.

---

## run_diff_cmd

```python
run_diff_cmd(run_a: str, run_b: str)
```

Compare two execution runs (WP-16001).

---

## self_heal_tests_cmd

```python
self_heal_tests_cmd(test_output: Any)
```

Self-healing test suite: automated fix recommendations (WP-6006).

---

## session_cmd

```python
session_cmd(session_id: Any, watch: bool, action: Any)
```

Rich TUI for session management with subagent monitoring (WP-8002).

---

## session_contract_health_gate_cmd

```python
session_contract_health_gate_cmd(all_sessions: bool, owner: Any, strict: bool, format: Any, min_healthy_ratio: float, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float, output: Any, export_format: Any, overwrite: bool) -> None
```

---

## session_contract_health_report_cmd

```python
session_contract_health_report_cmd(all_sessions: bool, owner: Any, strict: bool, top_blocked: int, policy_profile: Any, no_worse_than_baseline: bool, regression_tolerance: float, format: Any, output: Any, export_format: Any, overwrite: bool) -> None
```

---

## session_contract_health_trend_cmd

```python
session_contract_health_trend_cmd(payload_type: str, all_sessions: bool, owner: Any, strict: bool, policy_profile: Any, min_healthy_ratio: float, top_blocked: int, limit: int, format: Any, output: Any, export_format: Any, overwrite: bool) -> None
```

---

## session_contract_negotiate_cmd

```python
session_contract_negotiate_cmd(contract_id: str, supported_versions: str, format: Any)
```

Negotiate a contract version (WP-7001).

---

## session_contract_trend_analysis_cmd

Detailed contract trend analysis (WP-7009/7010).

---

## session_contracts_cmd

```python
session_contracts_cmd(all_sessions: bool, owner: Any, format: Any, missing_only: bool, summary_only: bool, strict: bool) -> None
```

---

## set_env

```python
set_env(key: str, value: str)
```

---

## setup_cmd

```python
setup_cmd(api_key: str, model: str, openrouter_key: str, kilo_key: str, zai_key: str, minimax_key: str, wizard: bool, links: bool, hooks: bool, skills: bool, full: bool, agents: str)
```

Unified setup: configure providers (same flow as cliproxy login) and install shortcuts.

**Examples**:

```python
thegent setup                    # Interactive wizard
thegent setup --full             # Full setup: install, shims, services
thegent setup --agents claude,codex  # Configure only Claude and Codex
thegent setup --hooks --skills   # Project: git hooks + skills
```

---

## signatures_list_cmd

```python
signatures_list_cmd(limit: int, format: Any)
```

List signed MAIF artifacts (WP-3002).

---

## signatures_verify_cmd

```python
signatures_verify_cmd(run_id: str)
```

Verify a signed MAIF artifact (WP-3002).

---

## sitback_dashboard_cmd

```python
sitback_dashboard_cmd(refresh: Any, format: Any, profile: str)
```

Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.

CLI mirror of thegent_sitback_dashboard MCP tool.
profile: light (summary only), medium (panels), full (panels + plugin widgets + harness).

---

## speed_index_cmd

```python
speed_index_cmd(format: Any, no_cache: bool)
```

Show speed index (0-1, higher=faster) for all model-provider pairs.

Uses CLIProxyAPIPlus metrics (tps_1m, latency_p50_ms, success_rate) when reachable;
falls back to Route.latency_ms.

---

## status_cmd

```python
status_cmd(session_id: Any, format: Any, include_contract: bool) -> None
```

---

## stop_cmd

```python
stop_cmd(session_id: Any, force: bool, wind_down: bool, grace: int) -> None
```

---

## summary_cmd

```python
summary_cmd(period: str, project: Any, summarize: bool, agent: str, full: bool, format: Any)
```

FR-X09: Unified summary and audit log across runs, chats, and commits.

---

## sweep_cmd

```python
sweep_cmd(drift_window: int, include_audit: bool, format: Any)
```

WP-3005: Policy drift sweep - runs drift detection, budget check, past-SLA escalations.

---

## takeover_cmd

```python
takeover_cmd(session_id: str)
```

Take over an active terminal session via tmux (WP-4008).

---

## team_create_cmd

```python
team_create_cmd(name: str, leader: Any, teammates: Any)
```

WP-6008: Create a new multi-agent team.

---

## team_task_add_cmd

```python
team_task_add_cmd(team_id: str, title: str, description: str)
```

WP-6008: Add a task to a team's backlog.

---

## team_task_list_cmd

```python
team_task_list_cmd(team_id: str)
```

WP-6008: List all tasks for a team.

---

## teammates_delegate_cmd

```python
teammates_delegate_cmd(teammate_id: str, prompt: str, parent_run_id: str)
```

WP-16002: Delegate a sub-task to a specialized teammate.

---

## teammates_list_cmd

WP-16001: List all discovered specialized agents available for delegation.

---

## teammates_status_cmd

```python
teammates_status_cmd(run_id: str)
```

WP-16002: Monitor the status of the teammate swarm.

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

## traffic_cmd

TRAFFIC KPI Dashboard (WP-Y7).

---

## trust_status_cmd

```python
trust_status_cmd(format: Any)
```

Show last environment and trust boundary status (WP-3007).

---

## usage_cmd

```python
usage_cmd(format: Any, include_cost: bool)
```

Show plan usage: provider metrics from CLIProxyAPIPlus and cost status (WP-5003).

For cross-provider session parsing (OpenCode, Claude Code, Codex, Gemini, Cursor, etc.),
use: bunx tokscale@latest

---

## wait_cmd

```python
wait_cmd(session_id: Any, timeout: int) -> None
```

---

## watchdog_cmd

```python
watchdog_cmd(max_idle_s: int)
```

Scan for stale sessions and recommend handoffs (WP-5005).

---

## workstream_dashboard_cmd

Launch workstream dashboard TUI.

---

## workstream_dependencies_cmd

Show the workstream dependency graph.

---

## workstream_launch_cmd

Launch the auto-launch system in the background.

---

## workstream_query_cmd

```python
workstream_query_cmd(query: str)
```

Execute SQL query on workstream database.

---

## workstream_stats_cmd

Get workstream statistics.

---

## wrapper

---
