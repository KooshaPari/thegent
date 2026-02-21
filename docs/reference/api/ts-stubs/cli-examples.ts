// Auto-generated usage examples for cli
// Source: generate-api-docs.py

import { LazyConsole, RunRegistry, ThegentSettings, archive_cmd, audit_verify_cmd, benchmark_cmd, bg_cmd, cliproxy_login_cmd, closure_pack_cmd, cockpit_cmd, compliance_plugin_check_cmd, compliance_redact_cmd, compliance_report_cmd, compliance_siem_test_cmd, concurrency_set_cmd, concurrency_show_cmd, config_check_cmd, context_history_cmd, contracts_conformance_cmd, contracts_registry_cmd, cost_status_cmd, cost_values_cmd, dag_add_cmd, dag_cancel_cmd, dag_checkpoint_cmd, dag_checkpoints_cmd, dag_list_cmd, dag_probe_cmd, dag_ready_cmd, dag_reconcile_cmd, dag_recover_cmd, dag_remove_cmd, dag_rollback_cmd, dag_run_cmd, dag_status_cmd, dag_sync_cmd, dag_update_cmd, dag_validate_cmd, data_protection_cmd, deep_research_cmd, deferral_list_cmd, deferral_resume_cmd, discovery_parse_cmd, discovery_register_cmd, discovery_scan_cmd, dlq_list_cmd, drift_cmd, drift_monitor_cmd, escalate_add_cmd, escalate_approve_cmd, escalate_list_cmd, escalate_resolve_cmd, events_cmd, explain_cmd, explorer_cmd, fallbacks_cmd, feedback_cmd, forensics_snapshot_cmd, get_exit_message, govern_configure_cmd, govern_cost_cmd, govern_go_cycle_cmd, govern_go_health_cmd, govern_go_status_cmd, govern_go_watch_cmd, guardrails_check_cmd, guardrails_show_cmd, handoff_cmd, handoff_confirm_cmd, handoff_list_cmd, handoff_show_cmd, history_cmd, inbox_list_cmd, inbox_wait_cmd, inspect_cmd, interruption_list_cmd, interruption_snooze_cmd, list_agents_cmd, list_droids_cmd, list_model_contract_schema_cmd, list_models_cmd, load_status_cmd, logs_cmd, loop_cmd, loop_send_cmd, loop_stop_cmd, metrics_cmd, migration_cmd, modes_cmd, monitor_cmd, observe_summary_cmd, on_progress, on_worker_output, operations_cmd, pause_cmd, plan_analyze_cmd, plan_claim_cmd, plan_complete_cmd, plan_do_next_cmd, plan_get_next_cmd, plan_incorporate_cmd, plan_loop_cmd, plan_progress_cmd, plan_wait_next_cmd, policy_check_cmd, policy_purge_cmd, policy_show_cmd, project_list_cmd, project_register_cmd, prompt_key, ps_cmd, purge_cmd, quality_index_cmd, queue_list_cmd, recover_status_cmd, release_pack_cmd, replay_cmd, resolve_model_route_cmd, resume_cmd, retry_cmd, roadmap_cmd, rules_sync_cmd, run_cmd, run_diff_cmd, scratchpad_cmd, self_heal_tests_cmd, session_cmd, session_contract_health_gate_cmd, session_contract_health_report_cmd, session_contract_health_trend_cmd, session_contract_negotiate_cmd, session_contract_trend_analysis_cmd, session_contracts_cmd, set_env, setup_cmd, signatures_list_cmd, signatures_verify_cmd, sitback_dashboard_cmd, speed_index_cmd, status_cmd, stop_cmd, summary_cmd, sweep_cmd, takeover_cmd, team_create_cmd, team_task_add_cmd, team_task_list_cmd, teammates_delegate_cmd, teammates_list_cmd, teammates_status_cmd, terminal_route_cmd, trace_replay_cmd, traffic_cmd, trust_status_cmd, usage_cmd, wait_cmd, watchdog_cmd, workstream_dashboard_cmd, workstream_dependencies_cmd, workstream_launch_cmd, workstream_query_cmd, workstream_stats_cmd, wrapper } from "./cli";

// Create a LazyConsole instance
const lazyconsole = new LazyConsole();

// Call RunRegistry
RunRegistry();
// Call ThegentSettings
ThegentSettings();
// Call archive_cmd
archive_cmd(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call audit_verify_cmd
audit_verify_cmd(undefined as unknown as any);
// Call benchmark_cmd
benchmark_cmd();
// Call bg_cmd
bg_cmd();
// Call cliproxy_login_cmd
cliproxy_login_cmd("example_provider", false);
// Call closure_pack_cmd
closure_pack_cmd(undefined as unknown as any);
// Call cockpit_cmd
cockpit_cmd();
// Call compliance_plugin_check_cmd
compliance_plugin_check_cmd("example_plugin_id", "example_signature");
// Call compliance_redact_cmd
compliance_redact_cmd("example_text");
// Call compliance_report_cmd
compliance_report_cmd(undefined as unknown as any, undefined as unknown as any);
// Call compliance_siem_test_cmd
compliance_siem_test_cmd("example_message", "example_severity");
// Call concurrency_set_cmd
concurrency_set_cmd(0);
// Call concurrency_show_cmd
concurrency_show_cmd(undefined as unknown as any);
// Call config_check_cmd
config_check_cmd(undefined as unknown as any);
// Call context_history_cmd
context_history_cmd(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, 0);
// Call contracts_conformance_cmd
contracts_conformance_cmd(undefined as unknown as any, false, 0);
// Call contracts_registry_cmd
contracts_registry_cmd(undefined as unknown as any);
// Call cost_status_cmd
cost_status_cmd(undefined as unknown as any);
// Call cost_values_cmd
cost_values_cmd(undefined as unknown as any);
// Call dag_add_cmd
dag_add_cmd("example_task_id", "example_agent", "example_prompt", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call dag_cancel_cmd
dag_cancel_cmd("example_task_id", undefined as unknown as any);
// Call dag_checkpoint_cmd
dag_checkpoint_cmd(undefined as unknown as any, "example_reason");
// Call dag_checkpoints_cmd
dag_checkpoints_cmd(0);
// Call dag_list_cmd
dag_list_cmd(undefined as unknown as any, undefined as unknown as any);
// Call dag_probe_cmd
dag_probe_cmd(undefined as unknown as any, undefined as unknown as any);
// Call dag_ready_cmd
dag_ready_cmd(undefined as unknown as any, undefined as unknown as any);
// Call dag_reconcile_cmd
dag_reconcile_cmd(undefined as unknown as any);
// Call dag_recover_cmd
dag_recover_cmd(undefined as unknown as any, "example_action");
// Call dag_remove_cmd
dag_remove_cmd("example_task_id", undefined as unknown as any);
// Call dag_rollback_cmd
dag_rollback_cmd(undefined as unknown as any, undefined as unknown as any);
// Call dag_run_cmd
dag_run_cmd(undefined as unknown as any, false, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, false, undefined as unknown as any);
// Call dag_status_cmd
dag_status_cmd(undefined as unknown as any, undefined as unknown as any);
// Call dag_sync_cmd
dag_sync_cmd(undefined as unknown as any, false);
// Call dag_update_cmd
dag_update_cmd("example_task_id", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call dag_validate_cmd
dag_validate_cmd(undefined as unknown as any);
// Call data_protection_cmd
data_protection_cmd(undefined as unknown as any);
// Call deep_research_cmd
deep_research_cmd("example_query", "example_subreddits", "example_output");
// Call deferral_list_cmd
deferral_list_cmd();
// Call deferral_resume_cmd
deferral_resume_cmd("example_run_id");
// Call discovery_parse_cmd
discovery_parse_cmd("example_text", false, 0);
// Call discovery_register_cmd
discovery_register_cmd("example_agent", 0, 0, "example_cwd", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call discovery_scan_cmd
discovery_scan_cmd(undefined as unknown as any);
// Call dlq_list_cmd
dlq_list_cmd(undefined as unknown as any, undefined as unknown as any);
// Call drift_cmd
drift_cmd(0, undefined as unknown as any, 0, 0);
// Call drift_monitor_cmd
drift_monitor_cmd("example_prompt", undefined as unknown as Array<string>);
// Call escalate_add_cmd
escalate_add_cmd("example_run_id", "example_reason", 0, undefined as unknown as any, "example_lane", 0);
// Call escalate_approve_cmd
escalate_approve_cmd(undefined as unknown as any);
// Call escalate_list_cmd
escalate_list_cmd(false, 0, undefined as unknown as any);
// Call escalate_resolve_cmd
escalate_resolve_cmd(undefined as unknown as any, "example_resolution");
// Call events_cmd
events_cmd(undefined as unknown as any, 0, undefined as unknown as any);
// Call explain_cmd
explain_cmd(undefined as unknown as any);
// Call explorer_cmd
explorer_cmd();
// Call fallbacks_cmd
fallbacks_cmd(undefined as unknown as any);
// Call feedback_cmd
feedback_cmd(undefined as unknown as any, 0, undefined as unknown as any);
// Call forensics_snapshot_cmd
forensics_snapshot_cmd(undefined as unknown as any, undefined as unknown as any);
// Call get_exit_message
get_exit_message();
// Call govern_configure_cmd
govern_configure_cmd(undefined as unknown as any, false);
// Call govern_cost_cmd
govern_cost_cmd(undefined as unknown as any, 0, undefined as unknown as any);
// Call govern_go_cycle_cmd
govern_go_cycle_cmd(undefined as unknown as any, false, undefined as unknown as any);
// Call govern_go_health_cmd
govern_go_health_cmd(undefined as unknown as any, undefined as unknown as any);
// Call govern_go_status_cmd
govern_go_status_cmd(undefined as unknown as any);
// Call govern_go_watch_cmd
govern_go_watch_cmd(undefined as unknown as any, 0, undefined as unknown as any);
// Call guardrails_check_cmd
guardrails_check_cmd("example_prompt", undefined as unknown as any, undefined as unknown as any);
// Call guardrails_show_cmd
guardrails_show_cmd();
// Call handoff_cmd
handoff_cmd("example_owner");
// Call handoff_confirm_cmd
handoff_confirm_cmd("example_snapshot_id", "example_incoming_owner", 0);
// Call handoff_list_cmd
handoff_list_cmd(0, undefined as unknown as any);
// Call handoff_show_cmd
handoff_show_cmd("example_snapshot_id", undefined as unknown as any);
// Call history_cmd
history_cmd(0, undefined as unknown as any);
// Call inbox_list_cmd
inbox_list_cmd(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, 0, undefined as unknown as any);
// Call inbox_wait_cmd
inbox_wait_cmd(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, 0, 0, false, undefined as unknown as any);
// Call inspect_cmd
inspect_cmd(undefined as unknown as any, undefined as unknown as any, 0, false, undefined as unknown as any, false);
// Call interruption_list_cmd
interruption_list_cmd(0, undefined as unknown as any);
// Call interruption_snooze_cmd
interruption_snooze_cmd("example_alert_id", 0, "example_itype");
// Call list_agents_cmd
list_agents_cmd();
// Call list_droids_cmd
list_droids_cmd(undefined as unknown as any);
// Call list_model_contract_schema_cmd
list_model_contract_schema_cmd();
// Call list_models_cmd
list_models_cmd(undefined as unknown as any, false, false, false);
// Call load_status_cmd
load_status_cmd(undefined as unknown as any);
// Call logs_cmd
logs_cmd(undefined as unknown as any, false, false, 0, 0, false);
// Call loop_cmd
loop_cmd("example_prompt", "example_todo_spec", undefined as unknown as any, "example_checker", "example_loop_mode", undefined as unknown as any);
// Call loop_send_cmd
loop_send_cmd(undefined as unknown as any, "example_prompt");
// Call loop_stop_cmd
loop_stop_cmd(undefined as unknown as any);
// Call metrics_cmd
metrics_cmd(undefined as unknown as any, false, 0);
// Call migration_cmd
migration_cmd("example_contract_id", "example_version", undefined as unknown as any);
// Call modes_cmd
modes_cmd(undefined as unknown as any, undefined as unknown as any);
// Call monitor_cmd
monitor_cmd(0);
// Call observe_summary_cmd
observe_summary_cmd(0, 0, 0, 0, undefined as unknown as any, undefined as unknown as any, 0, 0);
// Call on_progress
on_progress(0, 0, "example_message");
// Call on_worker_output
on_worker_output("example_text");
// Call operations_cmd
operations_cmd(undefined as unknown as any, undefined as unknown as any);
// Call pause_cmd
pause_cmd(undefined as unknown as any);
// Call plan_analyze_cmd
plan_analyze_cmd(undefined as unknown as any, false, false, false, undefined as unknown as any);
// Call plan_claim_cmd
plan_claim_cmd("example_item_id", undefined as unknown as any, undefined as unknown as any);
// Call plan_complete_cmd
plan_complete_cmd("example_item_id", undefined as unknown as any, undefined as unknown as any);
// Call plan_do_next_cmd
plan_do_next_cmd(undefined as unknown as any, 0, undefined as unknown as any);
// Call plan_get_next_cmd
plan_get_next_cmd(undefined as unknown as any, undefined as unknown as any);
// Call plan_incorporate_cmd
plan_incorporate_cmd(undefined as unknown as any, false);
// Call plan_loop_cmd
plan_loop_cmd(undefined as unknown as any, 0, 0, "example_agent", false);
// Call plan_progress_cmd
plan_progress_cmd(0, undefined as unknown as any);
// Call plan_wait_next_cmd
plan_wait_next_cmd(undefined as unknown as any, 0, 0, undefined as unknown as any, undefined as unknown as any);
// Call policy_check_cmd
policy_check_cmd("example_agent", undefined as unknown as any, "example_lane", 0);
// Call policy_purge_cmd
policy_purge_cmd(false);
// Call policy_show_cmd
policy_show_cmd();
// Call project_list_cmd
project_list_cmd();
// Call project_register_cmd
project_register_cmd("example_path", undefined as unknown as any);
// Call prompt_key
prompt_key("example_msg");
// Call ps_cmd
ps_cmd(false, undefined as unknown as any, undefined as unknown as any, false);
// Call purge_cmd
purge_cmd(false);
// Call quality_index_cmd
quality_index_cmd(undefined as unknown as any, false);
// Call queue_list_cmd
queue_list_cmd(false);
// Call recover_status_cmd
recover_status_cmd();
// Call release_pack_cmd
release_pack_cmd("example_version");
// Call replay_cmd
replay_cmd("example_run_id", undefined as unknown as any);
// Call resolve_model_route_cmd
resolve_model_route_cmd("example_model", undefined as unknown as any, "example_policy", 0, undefined as unknown as any);
// Call resume_cmd
resume_cmd(undefined as unknown as any);
// Call retry_cmd
retry_cmd(undefined as unknown as any, undefined as unknown as any, false, undefined as unknown as any, undefined as unknown as any);
// Call roadmap_cmd
roadmap_cmd();
// Call rules_sync_cmd
rules_sync_cmd(false, false, undefined as unknown as any);
// Call run_cmd
run_cmd(undefined as unknown as any, "example_prompt", undefined as unknown as any, "example_mode", 0, false, false, undefined as unknown as any, undefined as unknown as any, false, undefined as unknown as any, false, undefined as unknown as any, "example_lane", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, false, false, false, undefined as unknown as any, false, undefined as unknown as any, undefined as unknown as any);
// Call run_diff_cmd
run_diff_cmd("example_run_a", "example_run_b");
// Call scratchpad_cmd
scratchpad_cmd("example_action", undefined as unknown as any);
// Call self_heal_tests_cmd
self_heal_tests_cmd(undefined as unknown as any);
// Call session_cmd
session_cmd(undefined as unknown as any, false, undefined as unknown as any);
// Call session_contract_health_gate_cmd
session_contract_health_gate_cmd(false, undefined as unknown as any, false, undefined as unknown as any, 0, undefined as unknown as any, false, 0, undefined as unknown as any, undefined as unknown as any, false);
// Call session_contract_health_report_cmd
session_contract_health_report_cmd(false, undefined as unknown as any, false, 0, undefined as unknown as any, false, 0, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, false);
// Call session_contract_health_trend_cmd
session_contract_health_trend_cmd("example_payload_type", false, undefined as unknown as any, false, undefined as unknown as any, 0, 0, 0, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, false);
// Call session_contract_negotiate_cmd
session_contract_negotiate_cmd("example_contract_id", "example_supported_versions", undefined as unknown as any);
// Call session_contract_trend_analysis_cmd
session_contract_trend_analysis_cmd();
// Call session_contracts_cmd
session_contracts_cmd(false, undefined as unknown as any, undefined as unknown as any, false, false, false);
// Call set_env
set_env("example_key", "example_value");
// Call setup_cmd
setup_cmd("example_api_key", "example_model", "example_openrouter_key", "example_kilo_key", "example_zai_key", "example_minimax_key", false, false, false, false, false, false, "example_agents");
// Call signatures_list_cmd
signatures_list_cmd(0, undefined as unknown as any);
// Call signatures_verify_cmd
signatures_verify_cmd("example_run_id");
// Call sitback_dashboard_cmd
sitback_dashboard_cmd(undefined as unknown as any, undefined as unknown as any, "example_profile");
// Call speed_index_cmd
speed_index_cmd(undefined as unknown as any, false);
// Call status_cmd
status_cmd(undefined as unknown as any, undefined as unknown as any, false);
// Call stop_cmd
stop_cmd(undefined as unknown as any, false, false, 0);
// Call summary_cmd
summary_cmd("example_period", undefined as unknown as any, false, "example_agent", false, undefined as unknown as any);
// Call sweep_cmd
sweep_cmd(0, false, undefined as unknown as any);
// Call takeover_cmd
takeover_cmd("example_session_id");
// Call team_create_cmd
team_create_cmd("example_name", undefined as unknown as any, undefined as unknown as any);
// Call team_task_add_cmd
team_task_add_cmd("example_team_id", "example_title", "example_description");
// Call team_task_list_cmd
team_task_list_cmd("example_team_id");
// Call teammates_delegate_cmd
teammates_delegate_cmd("example_teammate_id", "example_prompt", "example_parent_run_id");
// Call teammates_list_cmd
teammates_list_cmd();
// Call teammates_status_cmd
teammates_status_cmd("example_run_id");
// Call terminal_route_cmd
terminal_route_cmd("example_prompt", undefined as unknown as any);
// Call trace_replay_cmd
trace_replay_cmd("example_run_id");
// Call traffic_cmd
traffic_cmd();
// Call trust_status_cmd
trust_status_cmd(undefined as unknown as any);
// Call usage_cmd
usage_cmd(undefined as unknown as any, false);
// Call wait_cmd
wait_cmd(undefined as unknown as any, 0);
// Call watchdog_cmd
watchdog_cmd(0);
// Call workstream_dashboard_cmd
workstream_dashboard_cmd();
// Call workstream_dependencies_cmd
workstream_dependencies_cmd();
// Call workstream_launch_cmd
workstream_launch_cmd();
// Call workstream_query_cmd
workstream_query_cmd("example_query");
// Call workstream_stats_cmd
workstream_stats_cmd();
// Call wrapper
wrapper();
