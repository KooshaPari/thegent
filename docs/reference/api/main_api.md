# main API Reference

> **Source**: `src/thegent/main.py`

Thegent CLI entry point (subcommand-only).

---

## agents_list

List available providers. Alias for thegent list-agents.

---

## agents_retry

Retry a failed run. With no run_id, list recent failed runs. Alias for thegent retry.

```python
agents_retry(run_id, agent, failover, cd, override)
```

---

## archive

Archive old sessions (WP-6005). WP-3006: tiered retention (hot 30d, cold 1yr).

```python
archive(days, domain, tier)
```

---

## benchmark

Report orchestration performance metrics (WP-6001).

---

## bg

Start a background run and register a session.

```python
bg(prompt, agent, cd, mode, timeout, full, owner, model, provider, routing, failover, format, include_contract, continuation, continuation_stderr, run_id, lane, idempotency_token, confidence, arbitration, override, contract_version, domain, speculative, debug)
```

---

## cliproxy_ensure_config

Ensure proxy config exists (port, auth-dir). Add provider blocks manually. Restart proxy to apply.

---

## cliproxy_login

Run login for provider. Unified flow: open URL + prompt for API key. Preflight checks existing credentials.

```python
cliproxy_login(provider, force)
```

---

## cliproxy_restart

Ensure config, stop proxy, then start. Use after config changes.

---

## cliproxy_service

Manage proxy as launchd service (macOS). Runs at login, restarts on crash.

```python
cliproxy_service(action)
```

---

## cliproxy_start

Start proxy if not running. Uses ensure-config + CLIProxyAPIPlus binary.

---

## cliproxy_stop

Stop proxy (kill process on cliproxy port).

---

## closure_pack

Generate a formal closure pack for the current DAG session (WP-6002/6008/FR-024).

```python
closure_pack(cd)
```

---

## cockpit

Show high-level operator cockpit summary.

---

## code

Feature implementation and coding tasks.

```python
code(prompt, cd, bg, model, timeout)
```

---

## compliance_export

Export evidence bundle for SOC2, ISO27001, or EU-AI-ACT.

```python
compliance_export(framework, output)
```

---

## compliance_plugin_check

Verify a plugin contract (WP-15003).

```python
compliance_plugin_check(plugin_id, signature)
```

---

## compliance_redact

Test PII/Secret redaction (WP-15005).

```python
compliance_redact(text)
```

---

## compliance_siem_test

Test SIEM event egress (WP-15001).

```python
compliance_siem_test(message, severity)
```

---

## config_check

Validate config; fail-fast on misconfig (DX-010, ROB-013).

```python
config_check(format)
```

---

## dag_add

Add a task to the DAG.

```python
dag_add(task_id, agent, prompt, cd, depends_on, contract_version)
```

---

## dag_cancel

Set task status to cancelled.

```python
dag_cancel(task_id, cd)
```

---

## dag_checkpoint

Create a point-in-time checkpoint of the DAG state.

```python
dag_checkpoint(cd, reason)
```

---

## dag_checkpoints

List recent DAG checkpoints.

```python
dag_checkpoints(limit)
```

---

## dag_list

Parse and display DAG session from .factory/dag-session.md.

```python
dag_list(cd, format)
```

---

## dag_probe

Compare current DAG state with a baseline checkpoint to detect regressions.

```python
dag_probe(baseline_id, cd)
```

---

## dag_ready

List task IDs with satisfied dependencies (ready to run).

```python
dag_ready(cd, format)
```

---

## dag_reconcile

Reconcile DAG state with reality (clean up stuck 'running' tasks).

```python
dag_reconcile(cd)
```

---

## dag_recover

Perform recovery playbook actions on the DAG.

```python
dag_recover(action, cd)
```

---

## dag_remove

Remove a task from the DAG.

```python
dag_remove(task_id, cd)
```

---

## dag_rollback

Rollback DAG state to a specific checkpoint.

```python
dag_rollback(checkpoint_id, cd)
```

---

## dag_run

Spawn thegent bg for each ready task; update status=running and session_id.

```python
dag_run(cd, dry_run, task, max_parallel, lane, check_drift, contract_version)
```

---

## dag_status

Show task + linked session status (running/exited:rc).

```python
dag_status(cd, format)
```

---

## dag_sync

Update task status from session exit (running -> done/failed).

```python
dag_sync(cd, watch, interval, auto_run_next, no_auto_run_next)
```

---

## dag_update

Update a task in the DAG.

```python
dag_update(task_id, cd, status, prompt, agent, depends_on, contract_version)
```

---

## dag_validate

Validate DAG: cycles, orphans, agent names. Exit 2 on failure.

```python
dag_validate(cd)
```

---

## dag_wait_next

Block until DAG has next actionable work (sync + ready tasks). Does not return until ready tasks exist.

```python
dag_wait_next(cd, poll, timeout, format)
```

---

## deferral_list

List all currently deferred tasks.

---

## deferral_resume

Manually resume a deferred task.

```python
deferral_resume(run_id)
```

---

## explain

Clarification and educational explanation of complex concepts.

```python
explain(prompt, cd, bg, model, timeout)
```

---

## explain_run

Show detailed explanation for an agent run (WP-4002).

```python
explain_run(run_id)
```

---

## federation_list

List all federated namespaces (WP-13005).

---

## federation_status

Show detailed federation health and drift status (WP-13005).

---

## feedback

Provide operator feedback for a specific run.

```python
feedback(run_id, score, note)
```

---

## finance_dashboard

Show financial safety dashboard (WP-Y1).

---

## fix

Bug identification and resolution.

```python
fix(prompt, cd, bg, model, timeout)
```

---

## forensics_snapshot

Capture a forensic snapshot of the current environment.

```python
forensics_snapshot(run_id, phase)
```

---

## free

Base free tier: Copilot gpt-5-mini. Alias for thegent run "<prompt>" free.

```python
free(prompt, cd, mode, timeout, do_next, repeat, live, bg, diff)
```

---

## go_cycle

Run a single governance cycle.

```python
go_cycle(cd, force, format)
```

---

## go_health

Show current health score (composite 0-100, band, per-dimension breakdown).

```python
go_health(cd, format)
```

---

## go_status

Show current governance status (state, cycle_id, shutdown_requested).

```python
go_status(cd)
```

---

## go_watch

Run continuous governance mode.

```python
go_watch(cd, interval, max_cycles)
```

---

## govern_calibrate

Recalculate trust score calibration factors for all agents (G-GP-09).

---

## govern_compliance_report

Generate compliance evidence retention report (WP-3006).

```python
govern_compliance_report(format, output)
```

---

## govern_configure

Bootstrap governance: create contracts/health-targets.json if missing.

```python
govern_configure(cd, force)
```

---

## govern_conformance

Run provider adapter conformance tests.

```python
govern_conformance(format, check_drift, drift_window)
```

---

## govern_contracts

Show the contract registry and compatibility matrix.

```python
govern_contracts(format)
```

---

## govern_cost

Show daily cost aggregation (FR-GOV-002).

```python
govern_cost(owner, days, format)
```

---

## govern_data_protection

Show data protection and privacy controls status (WP-3006).

```python
govern_data_protection(format)
```

---

## govern_escalate_add

Add a blocked run to the escalation queue (WP-3008).

```python
govern_escalate_add(run_id, reason, sla_minutes, owner, lane, priority)
```

---

## govern_escalate_approve

Approve an escalation, recording an override for the owner (G-GP-05).

```python
govern_escalate_approve(run_id)
```

---

## govern_escalate_list

List governance escalation queue.

```python
govern_escalate_list(past_sla_only, limit, format)
```

---

## govern_escalate_resolve

Mark an escalation item as resolved.

```python
govern_escalate_resolve(run_id, resolution)
```

---

## govern_guardrails_check

Check a prompt against active guardrails (FR-GOV-003..006).

```python
govern_guardrails_check(prompt, agent, model)
```

---

## govern_guardrails_show

Show active guardrail configuration (FR-GOV-007).

---

## govern_hook_watcher

P8: Start hook cache watcher daemon — pre-warms caches on file changes.

```python
govern_hook_watcher(project_dir, interval, foreground)
```

---

## govern_interruption_list

List recent interruptions with taxonomy and fatigue score.

```python
govern_interruption_list(limit, format)
```

---

## govern_interruption_snooze

Snooze an alert; auto-escalates when expired.

```python
govern_interruption_snooze(alert_id, minutes, type)
```

---

## govern_migration

Evaluate migration status for a contract version.

```python
govern_migration(contract_id, version, format)
```

---

## govern_negotiate

Negotiate a contract version (WP-7001).

```python
govern_negotiate(contract_id, supported, format)
```

---

## govern_purge

WP-3006: Tiered retention purge (G-GP-07).

```python
govern_purge(dry_run)
```

---

## govern_release_pack

Automated release documentation packaging (WP-12009).

```python
govern_release_pack(version)
```

---

## govern_roadmap

Successor roadmap generation (WP-6004).

---

## govern_self_heal_tests

Self-healing test suite: automated fix recommendations (WP-6006).

```python
govern_self_heal_tests(test_output)
```

---

## govern_signatures_list

List signed MAIF artifacts (WP-3002).

```python
govern_signatures_list(limit, format)
```

---

## govern_signatures_verify

Verify a signed MAIF artifact (WP-3002).

```python
govern_signatures_verify(run_id)
```

---

## govern_sweep

WP-3005: Policy drift sweep - drift detection, budget check, past-SLA escalations (cron-ready).

```python
govern_sweep(drift_window, include_audit, format)
```

---

## govern_trend_analysis

Detailed contract trend analysis (WP-7009/7010).

---

## govern_trust_status

Show last environment and trust boundary status (WP-3007).

```python
govern_trust_status(format)
```

---

## history_audit_verify

Verify the integrity of the execution run registry.

```python
history_audit_verify(format)
```

---

## history_events

List raw telemetry events.

```python
history_events(limit, run_id, format)
```

---

## history_legacy

List execution run history (sync and background).

```python
history_legacy(limit, format, events, run_id)
```

---

## history_list

List execution run history (sync and background).

```python
history_list(limit, format)
```

---

## history_root

Default `history` behavior: list runs when no subcommand is provided.

```python
history_root(ctx, limit, format)
```

---

## inbox_list

List unified inbox events with optional filters.

```python
inbox_list(owner, agent, event_type, status, sources, limit, format)
```

---

## inbox_root

Default: list recent inbox events. Use 'inbox wait' to block until new event.

```python
inbox_root(ctx, owner, agent, event_type, status, sources, limit, format)
```

---

## inbox_wait

Wait for next inbox event matching filters. Blocks until new event or timeout.

```python
inbox_wait(owner, agent, event_type, status, sources, poll, timeout, notify, format)
```

---

## init_cmd

Initialize thegent: configure MCP clients and background services.

```python
init_cmd(url, cli)
```

---

## inspect

Show status and logs for one or more sessions. No shell loop needed.

```python
inspect(session_ids, owner, tail, stderr, format, include_contract)
```

---

## install_cmd

Managed installation of thegent components and MCP configuration.

```python
install_cmd(target, editable, force, undo, interactive, wizard, service, dry_run, verbose, url, bundle, bundle_manifest, list_bundles, validate_bundles, bundle_conflict_policy)
```

---

## install_shims_cmd

MTSP-10: Install optimized accelerators (shims) for common tools.
Accelerates git (multi-tenant), grep (rg), find (fd), jq (jaq).

```python
install_shims_cmd(bin_dir, force, all_tools)
```

---

## learning_list

List all candidate models in the learning registry.

---

## learning_promote

Promote a candidate model to 'promoted' status (WP-14003).

```python
learning_promote(model_id, approver)
```

---

## learning_rollback

Rollback a promoted or candidate model (WP-14003).

```python
learning_rollback(model_id)
```

---

## ledger_verify

Verify the integrity of the immutable incident ledger (WP-15002).

---

## list_agents

List available providers.

---

## list_droids

List available droids.

```python
list_droids(cd)
```

---

## list_models

List known models (optionally filtered by provider).

```python
list_models(provider, by_model, refresh, include_contract)
```

---

## login

Run login for provider. Alias for `thegent cliproxy login`. Unified: open URL + prompt for key.

```python
login(provider, force)
```

---

## logs

Print session logs.

```python
logs(session_id, follow, stderr, tail, timeout)
```

---

## loop

Run a Lifecycle loop with Checker oversight.

```python
loop(prompt, todo_spec, agent, checker, mode, cd)
```

---

## loop_send

Send prompt to a running loop. Human or agent can use this to inject the next instruction.

```python
loop_send(session_id, prompt)
```

---

## loop_stop

Send STOP signal to a running Lifecycle loop.

```python
loop_stop(session_id)
```

---

## mcp_down_cmd

Stop MCP + proxy (process-compose).

---

## mcp_fix

Remove failing MCP servers (codex_apps, playwright) that cause 'MCP startup incomplete'.
Use thegent's bundled mounts instead. Run 'thegent mcp up' before using.

```python
mcp_fix(client, workspace)
```

---

## mcp_install

Add thegent to MCP config for Cursor, Claude Code, Codex, or Claude Desktop. Bundles browser tools (playwright) by default.

```python
mcp_install(client, url, workspace, replace_playwright, uni_mount, http)
```

---

## mcp_migrate_unimount

Migrate to uni-mount: replace ALL MCP entries with thegent only. Fixes codex_apps/playwright handshake errors.
Thegent mounts playwright, serena, octocode — one URL, all tools. Run 'thegent mcp up' before using.

```python
mcp_migrate_unimount(client, url, workspace)
```

---

## mcp_prune

Kill redundant agent-related Node.js processes (LSPs, MCP servers, cc-status).
Use this when memory usage is high (>10GB) and many orphan processes are detected.
For automatic pruning on Stop, set THGENT_AUTO_PRUNE=1.

```python
mcp_prune(force, dry_run)
```

---

## mcp_prune_periodic

Install periodic prune daemon (launchd on macOS, systemd on Linux).
Runs thegent mcp prune --force every 15 min. Catches orphans when Stop doesn't fire (headless, Codex).

```python
mcp_prune_periodic(action)
```

---

## mcp_restart_cmd

Hot reload: restart MCP + proxy (down then up).

---

## mcp_service

Manage thegent MCP HTTP server as launchd service (macOS). Start server before clients connect.

```python
mcp_service(action)
```

---

## mcp_spotlight_exclude

Exclude heavy development and thegent metadata directories from Spotlight indexing (macOS).
Helps reduce mds_stores memory usage and CPU spikes during high-IO agent runs.

```python
mcp_spotlight_exclude(force)
```

---

## mcp_stdio

Start the MCP server in stdio mode (for Claude Code).

---

## mcp_up_cmd

Start MCP + proxy via process-compose (bundled mode).

```python
mcp_up_cmd(reload)
```

---

## memory_add_cmd

MTSP-17: Manually record a memory fragment.

```python
memory_add_cmd(content, cat, scope)
```

---

## memory_garden_cmd

MEM-AUD-02: Run the Gardener agent to prune memory into documentation.

---

## memory_issue

Shortcut for memory add --category issue.

```python
memory_issue(content)
```

---

## memory_remember

Shortcut for memory add --category note.

```python
memory_remember(content)
```

---

## memory_rule

Shortcut for memory add --category lesson_positive/negative.

```python
memory_rule(content, negative)
```

---

## memory_scrape_cmd

MTSP-18: Scrape session history and record prompts to audit log.

---

## memory_synthesize_cmd

MTSP-17: Generate a synthesis report from the audit log.

---

## mgmt_ensure_proxy

Ensure MCP + proxy are running. Starts via process-compose if needed. Agent self-service.

```python
mgmt_ensure_proxy(timeout)
```

---

## mgmt_verify_codex_cliproxy

Verify Codex works with CLIProxy adapter. Agent self-service: no user intervention needed.

```python
mgmt_verify_codex_cliproxy(model, prompt, timeout)
```

---

## models_contract

Show route contract metadata for model catalog consumers.

---

## models_cost_values

Show cost values ($/1k tokens) for all model-provider pairs. Uses proxy metrics when reachable.

```python
models_cost_values(format)
```

---

## models_metrics

Show cost, speed, and quality for all model-provider pairs (unified view).

```python
models_metrics(format, no_cache, limit)
```

---

## models_quality_index

Show quality index (0-1) for all models. Uses benchmarks.json (TB2.0, SWE-Bench, AIME).

```python
models_quality_index(format, no_cache)
```

---

## models_refresh

Invalidate models, speed-index, and quality-index caches. Next lookup will re-fetch.

---

## models_speed_index

Show speed index (0-1) for all model-provider pairs. Uses proxy metrics when reachable.

```python
models_speed_index(format, no_cache)
```

---

## modes

List multi-agent orchestration modes (G-KD-04).

```python
modes(format, mode)
```

---

## observe_cost_status

Show cost budget utilization and cost-aware routing status (WP-5003).

```python
observe_cost_status(format)
```

---

## observe_dlq

List items in the Dead-Letter Queue (WP-Y2/WP-2008).

```python
observe_dlq(status, format)
```

---

## observe_drift

Detect significant drift in contract performance and check alert budgets (G-RV-07).

```python
observe_drift(window, structural_budget, semantic_budget, format)
```

---

## observe_drift_monitor

Cross-provider drift monitoring (WP-6002).

```python
observe_drift_monitor(prompt, agents)
```

---

## observe_kpis

Show fallback KPIs for dashboard/alerting (G-CA-02 B3).

```python
observe_kpis(limit, format)
```

---

## observe_load_status

Show load classification and safe-mode status (WP-5002).

```python
observe_load_status(format)
```

---

## observe_summary

FR-X08: Unified observability summary (KPIs, drift, escalation).

```python
observe_summary(limit, drift_window, structural_budget, semantic_budget, provider, trend_samples, top_escalations, format)
```

---

## observe_traffic

TRAFFIC KPI Dashboard (WP-Y7).

---

## observe_trend

Read health trend snapshots for a report/gate policy scope.

```python
observe_trend(payload_type, all_sessions, owner, strict, limit, format)
```

---

## observe_usage

Show plan usage: provider metrics from CLIProxyAPIPlus and cost status.

```python
observe_usage(format, no_cost)
```

---

## operations

List universal operation taxonomy (orchestrate, govern, recover, observe, plan).

```python
operations(format, operation)
```

---

## orchestrate_fallbacks

Show safe fallback options for a failed run (WP-4003).

```python
orchestrate_fallbacks(run_id)
```

---

## orchestrate_handoff

Create a continuity snapshot for a shift handoff (WP-4006, WP-3008).

```python
orchestrate_handoff(owner)
```

---

## orchestrate_handoff_confirm

Incoming owner confirms handoff completeness (WP-3008, WP-4006).

```python
orchestrate_handoff_confirm(snapshot_id, incoming_owner, confidence)
```

---

## orchestrate_handoff_list

List pending handoff snapshots (WP-4006).

```python
orchestrate_handoff_list(limit, format)
```

---

## orchestrate_handoff_show

Show full handoff summary: state, evidence, next steps (WP-4006).

```python
orchestrate_handoff_show(snapshot_id, format)
```

---

## orchestrate_replay

Decision replay and rationale snapshots (WP-4007).

```python
orchestrate_replay(run_id, what_if_env)
```

---

## orchestrate_watchdog

Scan for stale sessions and recommend handoffs (WP-5005).

```python
orchestrate_watchdog(max_idle)
```

---

## pause

Mark a session as PAUSED in the registry (HITL).

```python
pause(session_id)
```

---

## plan_analyze

Run planning simulation overlays (XD1–XD3): PERT, resources, continuity risk.

```python
plan_analyze(cd, pert, resources, continuity, format)
```

---

## plan_claim

Claim an item in the unified work stream.

```python
plan_claim(item_id, agent_id, cd)
```

---

## plan_complete

Mark an item as complete in the unified work stream.

```python
plan_complete(item_id, agent_id, cd)
```

---

## plan_do_next

Find next actionable work items from PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue.

```python
plan_do_next(cd, limit, format)
```

---

## plan_get_next

Get first work item prompt for scripting. Use: PROMPT=$(thegent plan get-next)

```python
plan_get_next(cd, format)
```

---

## plan_incorporate

Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md. Preserves CLAIMED and COMPLETED.

```python
plan_incorporate(cd, dry_run)
```

---

## plan_loop

Loop: get next item -> run bg -> repeat until no items or --max reached. If --wait, blocks until work available.

```python
plan_loop(cd, max_iterations, sleep_seconds, agent, dry_run, wait_for_work)
```

---

## plan_progress

Show recent runs (work-package progress). Alias for history --limit N.

```python
plan_progress(limit, format)
```

---

## plan_wait_next

Block until next actionable work exists (DAG ready, do_next, escalation, inbox).

```python
plan_wait_next(cd, poll, timeout, sources, format)
```

---

## policy_check

Evaluate a hypothetical run against governance policies (WP-3001).

```python
policy_check(agent, model, lane, confidence)
```

---

## policy_purge

Purge expired history based on tiered retention (WP-3006).

```python
policy_purge(dry_run)
```

---

## policy_show

Show active governance policies and thresholds.

---

## project_list

List all registered projects.

---

## project_register

Register a project in the global registry.

```python
project_register(path, name)
```

---

## ps

List registered background sessions.

```python
ps(all_sessions, owner, format, include_contract)
```

---

## queue_list

List pending prompts in the queue.

```python
queue_list(watch)
```

---

## recover_status

Show recovery stability and suggested playbooks.

---

## research

Deep dive research and comprehensive information gathering.

```python
research(prompt, cd, bg, model, timeout)
```

---

## resolve_model_route

Resolve a model to a concrete provider+alias route.

```python
resolve_model_route(model, provider, policy, quality_floor, lane)
```

---

## resume

Mark a paused session as RUNNING in the registry (HITL).

```python
resume(session_id)
```

---

## retry

Retry a failed run. With no run_id, list recent failed runs.

```python
retry(run_id, agent, failover, cd, override)
```

---

## review

Critical analysis and quality checks for code or documentation.

```python
review(prompt, cd, bg, model, timeout)
```

---

## route_probe

Dry-run route resolution: show which provider would be selected (DX-004). Alias for resolve-model-route.

```python
route_probe(model, provider, policy, quality_floor, lane)
```

---

## rules_sync

Sync CLAUDE.md to other platform-specific rule files (AGENTS.md, Cursor, Codex).

```python
rules_sync(force, check, cd)
```

---

## run

Run a foreground agent invocation. Use -M <model> without agent for model-first routing.

```python
run(prompt, agent, cd, retry_run, mode, timeout, full, live, model, provider, failover, routing, include_contract, run_id, lane, idempotency_token, confidence, arbitration, override, contract_version, domain, speculative, search, debug)
```

---

## run_diff

Compare two execution runs (trace comparison).

```python
run_diff(run_a, run_b)
```

---

## serve

Start the MCP server. Defaults to HTTP. Delegates to launchd/Homebrew service when available.

```python
serve(host, port, force, http, reload)
```

---

## session_contract_health_gate

Fail if routing contract health is below threshold.

```python
session_contract_health_gate(all_sessions, owner, format, strict, min_healthy_ratio, policy_profile, no_worse_than_baseline, regression_tolerance, output, export_format, overwrite)
```

---

## session_contract_health_report

Create a policy-friendly session contract health report with issue and owner breakdown.

```python
session_contract_health_report(all_sessions, owner, format, strict, top_blocked, policy_profile, no_worse_than_baseline, regression_tolerance, output, export_format, overwrite)
```

---

## session_contract_health_trend

Read health trend snapshots for a report/gate policy scope.

```python
session_contract_health_trend(payload_type, all_sessions, owner, strict, policy_profile, min_healthy_ratio, top_blocked, limit, format, output, export_format, overwrite)
```

---

## session_contracts

Audit session routing contract metadata coverage and completeness.

```python
session_contracts(all_sessions, owner, format, missing_only, summary_only, strict)
```

---

## sitback_dashboard

Unified sitback dashboard: sessions, cockpit, terminals. CLI mirror of MCP tool.

```python
sitback_dashboard(refresh, format, profile)
```

---

## status

Show one session status.

```python
status(session_id, format, include_contract)
```

---

## stop

Stop a running session.

```python
stop(session_id, force, wind_down, grace)
```

---

## summarize

Summarize content with brevity and key takeaways.

```python
summarize(prompt, cd, bg, model, timeout)
```

---

## takeover

Attach to an interactive tmux session (takeover).

```python
takeover(session_id)
```

---

## team_create

Create a new multi-agent team.

```python
team_create(name, leader, teammates)
```

---

## team_task_add

Add a task to a team's backlog.

```python
team_task_add(team_id, title, description)
```

---

## team_task_list

List all tasks for a team.

```python
team_task_list(team_id)
```

---

## teammates_delegate

Delegate a sub-task to a specialized teammate (WP-16002).

```python
teammates_delegate(teammate_id, prompt, parent_run_id)
```

---

## teammates_list

List all discovered specialized agents available for delegation (WP-16001).

---

## teammates_status

Monitor the status of the teammate swarm (WP-16002).

```python
teammates_status(run_id)
```

---

## terminal_explorer

Launch the terminal explorer TUI.

---

## terminal_route

Route task to an active terminal session if available.

```python
terminal_route(prompt, cd)
```

---

## trace_replay

Replay an execution trace in simulation mode (WP-16001).

```python
trace_replay(run_id)
```

---

## wait

Wait for session completion and return session exit code.

```python
wait(session_id, timeout)
```

---

## wait_next

Block until next actionable work exists. Does not return until DAG ready, work item, escalation, or inbox event.

```python
wait_next(cd, poll, timeout, sources, format)
```

---

## write

```python
write(name, script)
```

---

