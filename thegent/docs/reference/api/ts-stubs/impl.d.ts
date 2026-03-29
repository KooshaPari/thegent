// Auto-generated TypeScript declarations for impl
// Source: generate-api-docs.py

export declare class DagDocument {
}

export declare class RunnerProxy extends AgentRunner {
  run(prompt: string, cwd: any, mode: string, timeout: number): void;
}

export declare function bg_impl(): void;
export declare function concurrency_set_impl(limit: number, load_based: boolean): void;
export declare function concurrency_show_impl(): void;
export declare function continuity_snapshot_impl(owner: string, run_ids: Array<string>, state_summary: any, next_steps: any): void;
export declare function dag_list_impl(cd: any): void;
export declare function dag_raw_impl(cd: any): void;
export declare function dag_ready_impl(cd: any): void;
export declare function dag_run_impl(cd: any, dry_run: boolean, task: any, max_parallel: any, lane: any, check_drift: boolean, contract_version: any): void;
export declare function dag_status_impl(cd: any): void;
export declare function dag_sync_impl(cd: any, auto_run_next: boolean): void;
export declare function do_next_impl(cd: any, limit: number): void;
export declare function escalate_add_impl(run_id: string, reason: string, sla_minutes: number, owner: any, agent: any, lane: string, priority: number): void;
export declare function escalate_approve_impl(run_id: string): void;
export declare function escalate_list_impl(past_sla_only: boolean, limit: number): void;
export declare function escalate_resolve_impl(run_id: string, resolution: string): void;
export declare function events_impl(run_id: any, limit: number): void;
export declare function explain_run_impl(run_id: string): void;
export declare function generate_monitor_layout(): Layout;
export declare function get_data_protection_status_impl(): void;
export declare function get_server_meta_impl(): void;
export declare function history_impl(limit: number): void;
export declare function inbox_list_impl(owner: any, agent: any, event_type: any, status: any, sources: [(str, Ellipsis)], limit: number): void;
export declare function inbox_wait_impl(timeout: any): void;
export declare function incorporate_impl(cd: any, dry_run: boolean): void;
export declare function inspect_impl(session_ids: Array<string>, owner: any, tail: number, stderr: boolean, include_contract: boolean): void;
export declare function isolation_check_impl(mode: string): void;
export declare function list_agents_impl(): void;
export declare function list_droids_impl(cd: any): void;
export declare function list_models_impl(provider: any, use_scraped: boolean, refresh: boolean, include_contract: boolean, by_model: boolean): void;
export declare function list_session_contracts_impl(owner: any, all: boolean, strict: boolean): void;
export declare function lock_resource_impl(resource_path: string, agent_id: string, ttl: number, cd: any): void;
export declare function logs_impl(session_id: string, tail: any, stderr: boolean, follow: boolean): void;
export declare function loop_impl(agent: string, prompt: string, todo_spec: string, checker: string, mode: string, cd: any, on_worker_output: any, on_progress: any, max_iterations: number): void;
export declare function metrics_impl(): void;
export declare function monitor_impl(interval: number): void;
export declare function observe_summary_impl(limit: number, drift_window: number, structural_budget_pct: number, semantic_budget_pct: number, provider: any, top_escalations: number, trend_samples: any): void;
export declare function plan_analyze_impl(cd: any, pert: boolean, resources: boolean, continuity: boolean): void;
export declare function prune_sessions_impl(days: any): void;
export declare function ps_impl(owner: any, all: boolean, agent: any, status: any, limit: number, scan_ide: boolean, include_contract: boolean): void;
export declare function purge_impl(dry_run: boolean): void;
export declare function retry_impl(run_id: string, agent_override: any, failover: boolean, cd: any, override_reason: any): void;
export declare function rules_sync_impl(cd: any, force: boolean, check: boolean): void;
export declare function run(prompt: string, cwd: any, mode: string, timeout: number): RunResult;
export declare function run_impl(agent: any, prompt: string, cd: any, mode: string, timeout: any, full: boolean, live: boolean, model: any, provider: any, run_id: any, owner: any, include_contract: boolean, route_contract: any, route_request: any, lane: string, confidence: any, override_reason: any, contract_version: any, domain: any, idempotency_token: any, correlation_id: any, speculative: boolean, arbitration: any, routing: any, enable_search: boolean, debug: boolean, task_id: any, shadow: boolean, lock: any, remote: any, config_provider: ConfigProvider | None, tenant_id: any): void;
export declare function runner_factory(agent_name: string): any;
export declare function session_contract_audit_impl(owner: any, all: boolean, missing_only: boolean, summary_only: boolean, strict: boolean): void;
export declare function session_contract_health_gate_impl(owner: any, all: boolean, strict: boolean, min_healthy_ratio: number, policy_profile: any, no_worse_than_baseline: boolean, regression_tolerance: number): void;
export declare function session_contract_health_report_impl(owner: any, all: boolean, strict: boolean, top_blocked: number, policy_profile: any, no_worse_than_baseline: boolean, regression_tolerance: number): void;
export declare function session_contract_health_trend_impl(payload_type: string, owner: any, all: boolean, strict: boolean, policy_profile: any, min_healthy_ratio: number, top_blocked: number, limit: number): void;
export declare function session_contract_negotiate_impl(contract_id: string, supported_versions: Array<string>): void;
export declare function session_meta_impl(session_id: string): void;
export declare function session_send_impl(session_id: string, message: string, msg_type: string): void;
export declare function sitback_dashboard_impl(profile: string): void;
export declare function spawn_next_impl(cd: any, limit: number, agent: string, timeout: any, lane: string, override_reason: string, claim: boolean): void;
export declare function status_impl(session_id: string, include_contract: boolean): void;
export declare function stop_impl(session_id: string, force: boolean): void;
export declare function sweep_impl(drift_window: number, structural_budget: number, semantic_budget: number, include_audit: boolean): void;
export declare function unlock_resource_impl(resource_path: string, agent_id: string, token: string, cd: any): void;
export declare function update_calibration_impl(): void;
export declare function verify_context_impl(files: Array<string>, cd: any): void;
export declare function wait_impl(session_id: string, timeout: any): void;
export declare function wait_next_impl(cd: any, poll_interval: number, timeout: number, sources: [(str, Ellipsis)]): void;
export declare function work_stream_claim_impl(item_id: string, agent_id: string, cd: any): void;
export declare function work_stream_complete_impl(item_id: string, agent_id: string, cd: any): void;
export declare function wrapped_run(): RunResult;
