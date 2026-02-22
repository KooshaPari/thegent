# Merged Fragmented Markdown

## Source: architecture/diagrams/module-dependencies.md

```mermaid
graph TD
  %% Thegent Module Dependencies
  thegent["thegent"]
  thegent_discovery["thegent_discovery"]
  thegent_git["thegent_git"]
  thegent_platform["thegent_platform"]
  thegent_shm["thegent_shm"]
  config_provider --> thegent
  cli_document_queue --> thegent
  cli_crew --> thegent
  git_lock_manage --> thegent
  execution --> thegent
  cli_legacy --> thegent
  mcp_manage --> thegent
  platform_paths --> thegent
  discovery --> thegent
  discovery --> thegent_discovery
  shared_server_integration --> thegent
  roid_main --> thegent
  mcp_tools_seeds --> thegent
  output_parser --> thegent
  cli_impl --> thegent
  cliproxy_adapter --> thegent
  dex_main --> thegent
  prompts --> thegent
  summary --> thegent
  cli --> thegent
  utils --> thegent
  clode_main --> thegent
  cli_sync --> thegent
  cli_linkcheck --> thegent
  mgmt_manage --> thegent
  tui --> thegent
  sitback_plugins --> thegent
  resources --> thegent
  install --> thegent
  errors --> thegent
  cli_concurrency --> thegent
  mcp_sitback --> thegent
  main --> thegent
  provider_model_manager --> thegent
  cli_initiative --> thegent
  shared_mcp_manager --> thegent
  doctor --> thegent
  cli_commands_shared_servers --> thegent
  mcp_tools_modes --> thegent
  mcp_server --> thegent
  always_dumps_research --> thegent
  library_psutil_research --> thegent
  phase15_enterprise_lifecycle --> thegent
  remote_compute_research --> thegent
  agent_hierarchy_impl_research --> thegent
  phase14_cost_sensing_tests --> thegent
  phase13_compliance_profiles --> thegent
  phase15_enterprise_compliance_tests --> thegent
  phase14_autonomous_learning --> thegent
  governance_escalation_dlq_research --> thegent
  phase13_cost_sensitivity_research --> thegent
  library_diskcache_research --> thegent
  auto_setup --> thegent
  auto_init --> thegent
  design_language --> thegent
  registry --> thegent
  tool_artifacts --> thegent
  decision_artifacts --> thegent
  generators --> thegent
  api --> thegent
  code_artifacts --> thegent
  storage --> thegent
  arbitrage --> thegent
  runtime_init --> thegent
  drift_corrector --> thegent
  subprocess_manager --> thegent
  resource_monitor --> thegent
  fast_subprocess --> thegent
  terminal_keepalive --> thegent
  fast_cache --> thegent
  power --> thegent
  provisioner --> thegent
  universal_adapter --> thegent
  integration --> thegent
  garden --> thegent
  seed_storage --> thegent
  rbac --> thegent
  tenancy --> thegent
  plugins --> thegent
  registry_tui --> thegent
  workstream_dashboard --> thegent
  compositor --> thegent
  app --> thegent
  harmonized_paths --> thegent
  work_stream --> thegent
  manage_devkit --> thegent
  consistency_checker --> thegent
  unified_config --> thegent
  promotion --> thegent
  swarm_memory --> thegent
  conformance --> thegent
  migration --> thegent
  adapters --> thegent
  validation --> thegent
  budget_alerts --> thegent
  harness --> thegent
  remediation_planner --> thegent
  workstream_db --> thegent
  selector --> thegent
  auto_launch --> thegent
  self_healing --> thegent
  autopoiesis --> thegent
  loop_controller --> thegent
  gardener --> thegent
  policy_evolver --> thegent
  teammates --> thegent
  codex_proxy --> thegent
  droid --> thegent
  state_machine --> thegent
  role_agent --> thegent
  cursor_api_runner --> thegent
  unified_registry_cli --> thegent
  optimizer --> thegent
  reward_model --> thegent
  cliproxy_manager --> thegent
  direct_agents --> thegent
  resilience --> thegent
  checker --> thegent
  synthesis --> thegent
  edit_links --> thegent
  link_checker --> thegent
  workstream --> thegent
  headless_manager --> thegent
  serena_integration --> thegent
  commands --> thegent
  catalog --> thegent
  cost_values --> thegent
  hybrid_router --> thegent
  scrapers --> thegent
  speed_values --> thegent
  quality_values --> thegent
  otel_instrumentation --> thegent
  snapshot --> thegent_git
  coordination --> thegent
  formal_loop --> thegent
  ethics_proof --> thegent
  alerts --> thegent
  explanations --> thegent
  session_tui --> thegent
  kpis --> thegent
  fallback_ui --> thegent
  models_providers_tui --> thegent
  queue_tui --> thegent
  launch --> thegent
  calibration --> thegent
  base_provider --> thegent
  sub_user_provider --> thegent
  executor_integration --> thegent
  server --> thegent
  registry_router --> thegent
  client --> thegent
  validator --> thegent
  shm --> thegent
  shm --> thegent_shm
  playbooks --> thegent
  checkpoint --> thegent
  billing --> thegent
  deferral --> thegent
  session_watcher --> thegent
  context --> thegent
  load_based_limits --> thegent
  circuit_breaker --> thegent
  session_scraper --> thegent
  collaboration --> thegent
  cost --> thegent
  evidence --> thegent
  dlq --> thegent
  agileplus --> thegent
  triggers --> thegent
  audit --> thegent
  input_guardrails --> thegent
  scoring --> thegent
  dlq_integration --> thegent
  health_score --> thegent
  health_score --> thegent_shm
  agent_deployer --> thegent
  drift --> thegent
  heliosShield_bridge --> thegent
  overrides --> thegent
  forensics --> thegent
  escalation --> thegent
  evidence_ledger --> thegent
  signatures --> thegent
  trust --> thegent
  attestation --> thegent
  constitution --> thegent
  retention --> thegent
  adapter_policy --> thegent
  config_provider_cp --> thegent
  tee_check --> thegent
  hash_chain --> thegent
  artifact_generator --> thegent
  dispatch_graph --> thegent
  donut_adapter --> thegent
  cost_tracker --> thegent
  pareto_router --> thegent
  task_router --> thegent
  litellm_responses_handler --> thegent
  litellm_router --> thegent
  auto_router --> thegent
  alerting --> thegent
  orchestrator --> thegent
  unified_sync --> thegent
  audit_framework --> thegent
  never_idle --> thegent
```

---

## Source: architecture/diagrams/package-structure.md

```mermaid
graph TD
  %% Thegent Package Structure
  root["thegent"]
  root_config_provider["config_provider"]
  root --> root_config_provider
  root_cli_document_queue["cli_document_queue"]
  root --> root_cli_document_queue
  root_cli_crew["cli_crew"]
  root --> root_cli_crew
  root_git_lock_manage["git_lock_manage"]
  root --> root_git_lock_manage
  root_execution["execution"]
  root --> root_execution
  root_cli_legacy["cli_legacy"]
  root --> root_cli_legacy
  root_config["config"]
  root --> root_config
  root_mcp_manage["mcp_manage"]
  root --> root_mcp_manage
  root_thegent_platform["thegent_platform"]
  root --> root_thegent_platform
  root_platform_paths["platform_paths"]
  root --> root_platform_paths
  root_discovery["discovery"]
  root --> root_discovery
  root_shared_server_integration["shared_server_integration"]
  root --> root_shared_server_integration
  root_roid_main["roid_main"]
  root --> root_roid_main
  root_mcp_tools_seeds["mcp_tools_seeds"]
  root --> root_mcp_tools_seeds
  root_exit_codes["exit_codes"]
  root --> root_exit_codes
  root_terminal_cli["terminal_cli"]
  root --> root_terminal_cli
  root_output_parser["output_parser"]
  root --> root_output_parser
  root_cli_impl["cli_impl"]
  root --> root_cli_impl
  root_cliproxy_adapter["cliproxy_adapter"]
  root --> root_cliproxy_adapter
  root_orchestration_modes["orchestration_modes"]
  root --> root_orchestration_modes
  root_dex_main["dex_main"]
  root --> root_dex_main
  root_prompts["prompts"]
  root --> root_prompts
  root_thg_platform["thg_platform"]
  root --> root_thg_platform
  root_parser["parser"]
  root --> root_parser
  root_operations["operations"]
  root --> root_operations
  root_summary["summary"]
  root --> root_summary
  root_shared_lsp_manager["shared_lsp_manager"]
  root --> root_shared_lsp_manager
  root_cli["cli"]
  root --> root_cli
  root_utils["utils"]
  root --> root_utils
  root_clode_main["clode_main"]
  root --> root_clode_main
  root_cli_sync["cli_sync"]
  root --> root_cli_sync
  root_cli_linkcheck["cli_linkcheck"]
  root --> root_cli_linkcheck
  root_mgmt_manage["mgmt_manage"]
  root --> root_mgmt_manage
  root_tui["tui"]
  root --> root_tui
  root_sitback_plugins["sitback_plugins"]
  root --> root_sitback_plugins
  root_resources["resources"]
  root --> root_resources
  root_install["install"]
  root --> root_install
  root_errors["errors"]
  root --> root_errors
  root_cli_concurrency["cli_concurrency"]
  root --> root_cli_concurrency
  root_mcp_sitback["mcp_sitback"]
  root --> root_mcp_sitback
  root_main["main"]
  root --> root_main
  root_provider_model_manager["provider_model_manager"]
  root --> root_provider_model_manager
  root_cli_initiative["cli_initiative"]
  root --> root_cli_initiative
  root_shared_mcp_manager["shared_mcp_manager"]
  root --> root_shared_mcp_manager
  root_doctor["doctor"]
  root --> root_doctor
  root_cli_commands_shared_servers["cli_commands_shared_servers"]
  root --> root_cli_commands_shared_servers
  root_mcp_tools_modes["mcp_tools_modes"]
  root --> root_mcp_tools_modes
  root_prune_utils["prune_utils"]
  root --> root_prune_utils
  root_mcp_server["mcp_server"]
  root --> root_mcp_server
  root_shell_cli["shell_cli"]
  root --> root_shell_cli
  acp["acp"]
  root --> acp
  acp_server["server"]
  acp --> acp_server
  acp_client["client"]
  acp --> acp_client
  agent["agent"]
  root --> agent
  agent_monitoring_engine["monitoring_engine"]
  agent --> agent_monitoring_engine
  agent_crew_executor["crew_executor"]
  agent --> agent_crew_executor
  agent_workflow_engine["workflow_engine"]
  agent --> agent_workflow_engine
  agent_router_manager["router_manager"]
  agent --> agent_router_manager
  agent_crew["crew"]
  agent --> agent_crew
  agent_codex_harness["codex_harness"]
  agent --> agent_codex_harness
  agents["agents"]
  root --> agents
  agents_red_team["red_team"]
  agents --> agents_red_team
  agents_autopoiesis["autopoiesis"]
  agents --> agents_autopoiesis
  agents_loop_controller["loop_controller"]
  agents --> agents_loop_controller
  agents_verification["verification"]
  agents --> agents_verification
  agents_gardener["gardener"]
  agents --> agents_gardener
  agents_digital_twin["digital_twin"]
  agents --> agents_digital_twin
  agents_policy_evolver["policy_evolver"]
  agents --> agents_policy_evolver
  agents_presets["presets"]
  agents --> agents_presets
  agents_registry["registry"]
  agents --> agents_registry
  agents_teammates["teammates"]
  agents --> agents_teammates
  agents_information_life["information_life"]
  agents --> agents_information_life
  agents_codex_proxy["codex_proxy"]
  agents --> agents_codex_proxy
  agents_droid["droid"]
  agents --> agents_droid
  agents_refactoring["refactoring"]
  agents --> agents_refactoring
  agents_unified_registry["unified_registry"]
  agents --> agents_unified_registry
  agents_state_machine["state_machine"]
  agents --> agents_state_machine
  agents_modes["modes"]
  agents --> agents_modes
  agents_routing_contracts["routing_contracts"]
  agents --> agents_routing_contracts
  agents_role_agent["role_agent"]
  agents --> agents_role_agent
  agents_probing["probing"]
  agents --> agents_probing
  agents_cursor_api_runner["cursor_api_runner"]
  agents --> agents_cursor_api_runner
  agents_unified_registry_cli["unified_registry_cli"]
  agents --> agents_unified_registry_cli
  agents_tool_adapter["tool_adapter"]
  agents --> agents_tool_adapter
  agents_optimizer["optimizer"]
  agents --> agents_optimizer
  agents_reward_model["reward_model"]
  agents --> agents_reward_model
  agents_cliproxy_manager["cliproxy_manager"]
  agents --> agents_cliproxy_manager
  agents_self_healing["self_healing"]
  agents --> agents_self_healing
  agents_identity["identity"]
  agents --> agents_identity
  agents_direct_agents["direct_agents"]
  agents --> agents_direct_agents
  agents_resilience["resilience"]
  agents --> agents_resilience
  agents_base["base"]
  agents --> agents_base
  agents_checker["checker"]
  agents --> agents_checker
  agents_black_box_proxy["black_box_proxy"]
  agents --> agents_black_box_proxy
  agents_synthesis["synthesis"]
  agents --> agents_synthesis
  agents_document["agents.document"]
  agents --> agents_document
  agents_document_scanner["scanner"]
  agents_document --> agents_document_scanner
  agents_document_analyzer["analyzer"]
  agents_document --> agents_document_analyzer
  agents_document_processor["processor"]
  agents_document --> agents_document_processor
  agents_document_queue_manager["queue_manager"]
  agents_document --> agents_document_queue_manager
  artifacts["artifacts"]
  root --> artifacts
  artifacts_registry["registry"]
  artifacts --> artifacts_registry
  artifacts_tool_artifacts["tool_artifacts"]
  artifacts --> artifacts_tool_artifacts
  artifacts_decision_artifacts["decision_artifacts"]
  artifacts --> artifacts_decision_artifacts
  artifacts_generators["generators"]
  artifacts --> artifacts_generators
  artifacts_api["api"]
  artifacts --> artifacts_api
  artifacts_code_artifacts["code_artifacts"]
  artifacts --> artifacts_code_artifacts
  artifacts_storage["storage"]
  artifacts --> artifacts_storage
  artifacts_base["base"]
  artifacts --> artifacts_base
  compositor["compositor"]
  root --> compositor
  compositor_session_state["session_state"]
  compositor --> compositor_session_state
  compositor_pane_manager["pane_manager"]
  compositor --> compositor_pane_manager
  compositor_app["app"]
  compositor --> compositor_app
  compositor_layout_engine["layout_engine"]
  compositor --> compositor_layout_engine
  compositor_terminal_pane["terminal_pane"]
  compositor --> compositor_terminal_pane
  compositor_components["components"]
  compositor --> compositor_components
  compute["compute"]
  root --> compute
  compute_offload["offload"]
  compute --> compute_offload
  context["context"]
  root --> context
  context_context_injection["context_injection"]
  context --> context_context_injection
  context_dna_storage["dna_storage"]
  context --> context_dna_storage
  contracts["contracts"]
  root --> contracts
  contracts_registry["registry"]
  contracts --> contracts_registry
  contracts_events["events"]
  contracts --> contracts_events
  contracts_capability_registry["capability_registry"]
  contracts --> contracts_capability_registry
  contracts_policy["policy"]
  contracts --> contracts_policy
  contracts_telemetry["telemetry"]
  contracts --> contracts_telemetry
  contracts_parser["parser"]
  contracts --> contracts_parser
  contracts_marketplace["marketplace"]
  contracts --> contracts_marketplace
  contracts_conformance["conformance"]
  contracts --> contracts_conformance
  contracts_migration["migration"]
  contracts --> contracts_migration
  contracts_adapters["adapters"]
  contracts --> contracts_adapters
  contracts_validation["validation"]
  contracts --> contracts_validation
  control_plane["control_plane"]
  root --> control_plane
  control_plane_server["server"]
  control_plane --> control_plane_server
  control_plane_registry_router["registry_router"]
  control_plane --> control_plane_registry_router
  control_plane_client["client"]
  control_plane --> control_plane_client
  control_plane_cli["cli"]
  control_plane --> control_plane_cli
  control_plane_rules_loader["rules_loader"]
  control_plane --> control_plane_rules_loader
  coordination["coordination"]
  root --> coordination
  coordination_file_coordination["file_coordination"]
  coordination --> coordination_file_coordination
  coordination_smart_merge["smart_merge"]
  coordination --> coordination_smart_merge
  cost["cost"]
  root --> cost
  cost_budget_alerts["budget_alerts"]
  cost --> cost_budget_alerts
  cost_cost_quality_optimization["cost_quality_optimization"]
  cost --> cost_cost_quality_optimization
  crew["crew"]
  root --> crew
  crew_task["task"]
  crew --> crew_task
  crew_harness["harness"]
  crew --> crew_harness
  crew_monitoring["monitoring"]
  crew --> crew_monitoring
  crew_crew["crew"]
  crew --> crew_crew
  crew_agent["agent"]
  crew --> crew_agent
  crew_workflow["workflow"]
  crew --> crew_workflow
  crew_router["router"]
  crew --> crew_router
  crew_executor["executor"]
  crew --> crew_executor
  cross_platform["cross_platform"]
  root --> cross_platform
  cross_platform_shell_strategy["shell_strategy"]
  cross_platform --> cross_platform_shell_strategy
  cross_platform_security["security"]
  cross_platform --> cross_platform_security
  cross_platform_performance["performance"]
  cross_platform --> cross_platform_performance
  cross_platform_coordination["coordination"]
  cross_platform --> cross_platform_coordination
  cross_platform_desktop_automation["desktop_automation"]
  cross_platform --> cross_platform_desktop_automation
  design["design"]
  root --> design
  design_naming["naming"]
  design --> design_naming
  design_design_language["design_language"]
  design --> design_design_language
  discovery["discovery"]
  root --> discovery
  discovery_sync["sync"]
  discovery --> discovery_sync
  discovery_galactic["galactic"]
  discovery --> discovery_galactic
  discovery_market["market"]
  discovery --> discovery_market
  discovery_mesh["mesh"]
  discovery --> discovery_mesh
  discovery_edge_sync["edge_sync"]
  discovery --> discovery_edge_sync
  discovery_projects["projects"]
  discovery --> discovery_projects
  discovery_relativistic["relativistic"]
  discovery --> discovery_relativistic
  discovery_federation["federation"]
  discovery --> discovery_federation
  discovery_p2p["discovery.p2p"]
  discovery --> discovery_p2p
  discovery_p2p_protocol["protocol"]
  discovery_p2p --> discovery_p2p_protocol
  doc_tools["doc_tools"]
  root --> doc_tools
  doc_tools_playwright_recorder["playwright_recorder"]
  doc_tools --> doc_tools_playwright_recorder
  docgen["docgen"]
  root --> docgen
  docgen_llm_output["llm_output"]
  docgen --> docgen_llm_output
  docgen_api_typescript["api_typescript"]
  docgen --> docgen_api_typescript
  docgen_architecture_generator["architecture_generator"]
  docgen --> docgen_architecture_generator
  docgen_api_python["api_python"]
  docgen --> docgen_api_python
  docgen_openapi["openapi"]
  docgen --> docgen_openapi
  docgen_cli_examples["cli_examples"]
  docgen --> docgen_cli_examples
  docgen_sticky_nav["sticky_nav"]
  docgen --> docgen_sticky_nav
  docgen_parallel_generation["parallel_generation"]
  docgen --> docgen_parallel_generation
  docgen_code_annotation["code_annotation"]
  docgen --> docgen_code_annotation
  docgen_watch_mode["watch_mode"]
  docgen --> docgen_watch_mode
  docgen_content_tabs["content_tabs"]
  docgen --> docgen_content_tabs
  docgen_code_validator["code_validator"]
  docgen --> docgen_code_validator
  docgen_auto_sidebar["auto_sidebar"]
  docgen --> docgen_auto_sidebar
  docgen_agent_workflow["agent_workflow"]
  docgen --> docgen_agent_workflow
  docgen_versioning["versioning"]
  docgen --> docgen_versioning
  docgen_demo_gif_generator["demo_gif_generator"]
  docgen --> docgen_demo_gif_generator
  docgen_analytics["analytics"]
  docgen --> docgen_analytics
  docgen_math_support["math_support"]
  docgen --> docgen_math_support
  docgen_incremental_generation["incremental_generation"]
  docgen --> docgen_incremental_generation
  docgen_performance["performance"]
  docgen --> docgen_performance
  docgen_algolia_search["algolia_search"]
  docgen --> docgen_algolia_search
  economy["economy"]
  root --> economy
  economy_payments["payments"]
  economy --> economy_payments
  economy_reputation["reputation"]
  economy --> economy_reputation
  economy_arbitrage["arbitrage"]
  economy --> economy_arbitrage
  forensics["forensics"]
  root --> forensics
  forensics_snapshot["snapshot"]
  forensics --> forensics_snapshot
  governance["governance"]
  root --> governance
  governance_config_provider["config_provider"]
  governance --> governance_config_provider
  governance_plugin_lifecycle["plugin_lifecycle"]
  governance --> governance_plugin_lifecycle
  governance_compliance_reports["compliance_reports"]
  governance --> governance_compliance_reports
  governance_redaction["redaction"]
  governance --> governance_redaction
  governance_isolation["isolation"]
  governance --> governance_isolation
  governance_metrics["metrics"]
  governance --> governance_metrics
  governance_personas["personas"]
  governance --> governance_personas
  governance_scanner["scanner"]
  governance --> governance_scanner
  governance_override_expired["override_expired"]
  governance --> governance_override_expired
  governance_agileplus["agileplus"]
  governance --> governance_agileplus
  governance_support["support"]
  governance --> governance_support
  governance_triggers["triggers"]
  governance --> governance_triggers
  governance_audit["audit"]
  governance --> governance_audit
  governance_hitl["hitl"]
  governance --> governance_hitl
  governance_compliance["compliance"]
  governance --> governance_compliance
  governance_input_guardrails["input_guardrails"]
  governance --> governance_input_guardrails
  governance_control_vectors["control_vectors"]
  governance --> governance_control_vectors
  governance_handoff["handoff"]
  governance --> governance_handoff
  governance_teammates["teammates"]
  governance --> governance_teammates
  governance_semantic_firewall["semantic_firewall"]
  governance --> governance_semantic_firewall
  governance_scoring["scoring"]
  governance --> governance_scoring
  governance_analyzer["analyzer"]
  governance --> governance_analyzer
  governance_dlq_integration["dlq_integration"]
  governance --> governance_dlq_integration
  governance_policy["policy"]
  governance --> governance_policy
  governance_ledger["ledger"]
  governance --> governance_ledger
  governance_health_score["health_score"]
  governance --> governance_health_score
  governance_agent_deployer["agent_deployer"]
  governance --> governance_agent_deployer
  governance_drift["drift"]
  governance --> governance_drift
  governance_heliosShield_bridge["heliosShield_bridge"]
  governance --> governance_heliosShield_bridge
  governance_overrides["overrides"]
  governance --> governance_overrides
  governance_forensics["forensics"]
  governance --> governance_forensics
  governance_escalation["escalation"]
  governance --> governance_escalation
  governance_evidence_ledger["evidence_ledger"]
  governance --> governance_evidence_ledger
  governance_kill_switch["kill_switch"]
  governance --> governance_kill_switch
  governance_backlog["backlog"]
  governance --> governance_backlog
  governance_evidence_graph["evidence_graph"]
  governance --> governance_evidence_graph
  governance_agent_hierarchy["agent_hierarchy"]
  governance --> governance_agent_hierarchy
  governance_providers["providers"]
  governance --> governance_providers
  governance_signatures["signatures"]
  governance --> governance_signatures
  governance_breakers["breakers"]
  governance --> governance_breakers
  governance_trust["trust"]
  governance --> governance_trust
  governance_attestation["attestation"]
  governance --> governance_attestation
  governance_constitution["constitution"]
  governance --> governance_constitution
  governance_value_lock["value_lock"]
  governance --> governance_value_lock
  governance_retention["retention"]
  governance --> governance_retention
  governance_adapter_policy["adapter_policy"]
  governance --> governance_adapter_policy
  governance_costs["costs"]
  governance --> governance_costs
  governance_cost_aggregation["cost_aggregation"]
  governance --> governance_cost_aggregation
  governance_cost_controller["cost_controller"]
  governance --> governance_cost_controller
  governance_policy_federation["policy_federation"]
  governance --> governance_policy_federation
  governance_config_provider_cp["config_provider_cp"]
  governance --> governance_config_provider_cp
  governance_verification_gate["verification_gate"]
  governance --> governance_verification_gate
  governance_cost["cost"]
  governance --> governance_cost
  governance_tee_check["tee_check"]
  governance --> governance_tee_check
  governance_federation["federation"]
  governance --> governance_federation
  governance_slo["slo"]
  governance --> governance_slo
  governance_health_scorer["health_scorer"]
  governance --> governance_health_scorer
  governance_team_coordinator["team_coordinator"]
  governance --> governance_team_coordinator
  governance_meta["meta"]
  governance --> governance_meta
  hooks["hooks"]
  root --> hooks
  hooks_fr_index["fr_index"]
  hooks --> hooks_fr_index
  hooks_breaker["breaker"]
  hooks --> hooks_breaker
  hooks_affected_tests["affected_tests"]
  hooks --> hooks_affected_tests
  hooks_config_enhance["config_enhance"]
  hooks --> hooks_config_enhance
  hooks_prewarm_report["prewarm_report"]
  hooks --> hooks_prewarm_report
  hooks_learning["learning"]
  hooks --> hooks_learning
  hooks_debounce["debounce"]
  hooks --> hooks_debounce
  hooks_git_enhance["git_enhance"]
  hooks --> hooks_git_enhance
  hooks_changed_files_enhance["changed_files_enhance"]
  hooks --> hooks_changed_files_enhance
  hooks_incremental["incremental"]
  hooks --> hooks_incremental
  ide["ide"]
  root --> ide
  ide_auto_setup["auto_setup"]
  ide --> ide_auto_setup
  ide_auto_init["auto_init"]
  ide --> ide_auto_init
  infra["infra"]
  root --> infra
  infra_process_registry["process_registry"]
  infra --> infra_process_registry
  infra_fast_json_schema["fast_json_schema"]
  infra --> infra_fast_json_schema
  infra_resource_limits["resource_limits"]
  infra --> infra_resource_limits
  infra_fast_websocket["fast_websocket"]
  infra --> infra_fast_websocket
  infra_fast_process_monitor["fast_process_monitor"]
  infra --> infra_fast_process_monitor
  infra_discovery_v2["discovery_v2"]
  infra --> infra_discovery_v2
  infra_ipc["ipc"]
  infra --> infra_ipc
  infra_runtime_init["runtime_init"]
  infra --> infra_runtime_init
  infra_resource_management["resource_management"]
  infra --> infra_resource_management
  infra_drift_corrector["drift_corrector"]
  infra --> infra_drift_corrector
  infra_fast_file_watcher["fast_file_watcher"]
  infra --> infra_fast_file_watcher
  infra_fast_yaml_parser["fast_yaml_parser"]
  infra --> infra_fast_yaml_parser
  infra_git_parallelism["git_parallelism"]
  infra --> infra_git_parallelism
  infra_cache_v2["cache_v2"]
  infra --> infra_cache_v2
  infra_shell_injection["shell_injection"]
  infra --> infra_shell_injection
  infra_subprocess_manager["subprocess_manager"]
  infra --> infra_subprocess_manager
  infra_sandbox["sandbox"]
  infra --> infra_sandbox
  infra_resource_monitor["resource_monitor"]
  infra --> infra_resource_monitor
  infra_cage["cage"]
  infra --> infra_cage
  infra_fast_http_client["fast_http_client"]
  infra --> infra_fast_http_client
  infra_worktree["worktree"]
  infra --> infra_worktree
  infra_fast_subprocess["fast_subprocess"]
  infra --> infra_fast_subprocess
  infra_fast_uuid["fast_uuid"]
  infra --> infra_fast_uuid
  infra_fast_compression["fast_compression"]
  infra --> infra_fast_compression
  infra_terminal_keepalive["terminal_keepalive"]
  infra --> infra_terminal_keepalive
  infra_fast_path_ops["fast_path_ops"]
  infra --> infra_fast_path_ops
  infra_fast_cache["fast_cache"]
  infra --> infra_fast_cache
  infra_power["power"]
  infra --> infra_power
  infra_fast_string_ops["fast_string_ops"]
  infra --> infra_fast_string_ops
  infra_provisioner["provisioner"]
  infra --> infra_provisioner
  infra_fast_toml_parser["fast_toml_parser"]
  infra --> infra_fast_toml_parser
  infra_fast_file_ops["fast_file_ops"]
  infra --> infra_fast_file_ops
  integration["integration"]
  root --> integration
  integration_harmonized_paths["harmonized_paths"]
  integration --> integration_harmonized_paths
  integration_plan_system["plan_system"]
  integration --> integration_plan_system
  integration_work_stream["work_stream"]
  integration --> integration_work_stream
  integration_manage_devkit["manage_devkit"]
  integration --> integration_manage_devkit
  integration_consistency_checker["consistency_checker"]
  integration --> integration_consistency_checker
  integration_physical["physical"]
  integration --> integration_physical
  integration_slack["slack"]
  integration --> integration_slack
  integration_unified_config["unified_config"]
  integration --> integration_unified_config
  isolation["isolation"]
  root --> isolation
  isolation_base_provider["base_provider"]
  isolation --> isolation_base_provider
  isolation_models["models"]
  isolation --> isolation_models
  isolation_sub_user_provider["sub_user_provider"]
  isolation --> isolation_sub_user_provider
  isolation_executor_integration["executor_integration"]
  isolation --> isolation_executor_integration
  isolation_exceptions["exceptions"]
  isolation --> isolation_exceptions
  isolation_resource_isolation["resource_isolation"]
  isolation --> isolation_resource_isolation
  learning["learning"]
  root --> learning
  learning_promotion["promotion"]
  learning --> learning_promotion
  lsp["lsp"]
  root --> lsp
  lsp_headless_manager["headless_manager"]
  lsp --> lsp_headless_manager
  lsp_serena_integration["serena_integration"]
  lsp --> lsp_serena_integration
  lsp_auto_install["auto_install"]
  lsp --> lsp_auto_install
  lsp_jetbrains_cli["jetbrains_cli"]
  lsp --> lsp_jetbrains_cli
  lsp_commands["commands"]
  lsp --> lsp_commands
  maif["maif"]
  root --> maif
  maif_store["store"]
  maif --> maif_store
  maif_models["models"]
  maif --> maif_models
  maif_rust_manager["rust_manager"]
  maif --> maif_rust_manager
  maif_crypto["crypto"]
  maif --> maif_crypto
  maif_hash_chain["hash_chain"]
  maif --> maif_hash_chain
  maif_artifact_generator["artifact_generator"]
  maif --> maif_artifact_generator
  maif_artifacts["artifacts"]
  maif --> maif_artifacts
  maif_manager["manager"]
  maif --> maif_manager
  memory["memory"]
  root --> memory
  memory_garden["garden"]
  memory --> memory_garden
  memory_seed_storage["seed_storage"]
  memory --> memory_seed_storage
  memory_cache["cache"]
  memory --> memory_cache
  memory_test_seed_storage["test_seed_storage"]
  memory --> memory_test_seed_storage
  memory_cache_provider["cache_provider"]
  memory --> memory_cache_provider
  memory_test_seed_detector["test_seed_detector"]
  memory --> memory_test_seed_detector
  memory_seed_detector["seed_detector"]
  memory --> memory_seed_detector
  memory_manager["manager"]
  memory --> memory_manager
  memory_test_cache["test_cache"]
  memory --> memory_test_cache
  models["models"]
  root --> models
  models_catalog["catalog"]
  models --> models_catalog
  models_cost_values["cost_values"]
  models --> models_cost_values
  models_hybrid_router["hybrid_router"]
  models --> models_hybrid_router
  models_scrapers["scrapers"]
  models --> models_scrapers
  models_speed_values["speed_values"]
  models --> models_speed_values
  models_quality_values["quality_values"]
  models --> models_quality_values
  observability["observability"]
  root --> observability
  observability_observability_v2["observability_v2"]
  observability --> observability_observability_v2
  observability_egress["egress"]
  observability --> observability_egress
  observability_otel_instrumentation["otel_instrumentation"]
  observability --> observability_otel_instrumentation
  observability_analytics["analytics"]
  observability --> observability_analytics
  observability_explainability["explainability"]
  observability --> observability_explainability
  orchestration["orchestration"]
  root --> orchestration
  orchestration_oversight["oversight"]
  orchestration --> orchestration_oversight
  orchestration_swarm["swarm"]
  orchestration --> orchestration_swarm
  orchestration_swarm_consensus["swarm_consensus"]
  orchestration --> orchestration_swarm_consensus
  orchestration_shm["shm"]
  orchestration --> orchestration_shm
  orchestration_worker_pool["worker_pool"]
  orchestration --> orchestration_worker_pool
  orchestration_tasks["tasks"]
  orchestration --> orchestration_tasks
  orchestration_playbooks["playbooks"]
  orchestration --> orchestration_playbooks
  orchestration_checkpoint["checkpoint"]
  orchestration --> orchestration_checkpoint
  orchestration_billing["billing"]
  orchestration --> orchestration_billing
  orchestration_gardener["gardener"]
  orchestration --> orchestration_gardener
  orchestration_deferral["deferral"]
  orchestration --> orchestration_deferral
  orchestration_failure_modes["failure_modes"]
  orchestration --> orchestration_failure_modes
  orchestration_memory["memory"]
  orchestration --> orchestration_memory
  orchestration_discovery["discovery"]
  orchestration --> orchestration_discovery
  orchestration_swarm_memory["swarm_memory"]
  orchestration --> orchestration_swarm_memory
  orchestration_work_chunking["work_chunking"]
  orchestration --> orchestration_work_chunking
  orchestration_lanes["lanes"]
  orchestration --> orchestration_lanes
  orchestration_session_watcher["session_watcher"]
  orchestration --> orchestration_session_watcher
  orchestration_transactions["transactions"]
  orchestration --> orchestration_transactions
  orchestration_resource_management["resource_management"]
  orchestration --> orchestration_resource_management
  orchestration_graph["graph"]
  orchestration --> orchestration_graph
  orchestration_budget_alerts["budget_alerts"]
  orchestration --> orchestration_budget_alerts
  orchestration_prompts["prompts"]
  orchestration --> orchestration_prompts
  orchestration_speculative_strategies["speculative_strategies"]
  orchestration --> orchestration_speculative_strategies
  orchestration_phases["phases"]
  orchestration --> orchestration_phases
  orchestration_shm_context["shm_context"]
  orchestration --> orchestration_shm_context
  orchestration_context["context"]
  orchestration --> orchestration_context
  orchestration_load_based_limits["load_based_limits"]
  orchestration --> orchestration_load_based_limits
  orchestration_circuit_breaker["circuit_breaker"]
  orchestration --> orchestration_circuit_breaker
  orchestration_session_scraper["session_scraper"]
  orchestration --> orchestration_session_scraper
  orchestration_leasing["leasing"]
  orchestration --> orchestration_leasing
  orchestration_lock_free["lock_free"]
  orchestration --> orchestration_lock_free
  orchestration_collaboration["collaboration"]
  orchestration --> orchestration_collaboration
  orchestration_fork_guard["fork_guard"]
  orchestration --> orchestration_fork_guard
  orchestration_probes["probes"]
  orchestration --> orchestration_probes
  orchestration_cost["cost"]
  orchestration --> orchestration_cost
  orchestration_router["router"]
  orchestration --> orchestration_router
  orchestration_omega_consensus["omega_consensus"]
  orchestration --> orchestration_omega_consensus
  orchestration_shadow["shadow"]
  orchestration --> orchestration_shadow
  orchestration_evidence["evidence"]
  orchestration --> orchestration_evidence
  orchestration_dlq["dlq"]
  orchestration --> orchestration_dlq
  phases["phases"]
  root --> phases
  phases_tenant_boundary_tests["tenant_boundary_tests"]
  phases --> phases_tenant_boundary_tests
  phases_autonomous_learning_surface["autonomous_learning_surface"]
  phases --> phases_autonomous_learning_surface
  phases_cost_sensitivity["cost_sensitivity"]
  phases --> phases_cost_sensitivity
  phases_cost_sensing["cost_sensing"]
  phases --> phases_cost_sensing
  phases_enterprise_compliance_tests["enterprise_compliance_tests"]
  phases --> phases_enterprise_compliance_tests
  phases_policy_federation["policy_federation"]
  phases --> phases_policy_federation
  phases_enterprise_lifecycle["enterprise_lifecycle"]
  phases --> phases_enterprise_lifecycle
  phases_compliance_profile["compliance_profile"]
  phases --> phases_compliance_profile
  planning["planning"]
  root --> planning
  planning_simulation["simulation"]
  planning --> planning_simulation
  planning_cost_predictor["cost_predictor"]
  planning --> planning_cost_predictor
  planning_harness["harness"]
  planning --> planning_harness
  planning_remediation_planner["remediation_planner"]
  planning --> planning_remediation_planner
  planning_omega["omega"]
  planning --> planning_omega
  planning_multiverse["multiverse"]
  planning --> planning_multiverse
  planning_evolution["evolution"]
  planning --> planning_evolution
  planning_workstream_db["workstream_db"]
  planning --> planning_workstream_db
  planning_selector["selector"]
  planning --> planning_selector
  planning_auto_launch["auto_launch"]
  planning --> planning_auto_launch
  planning_work_stream["work_stream"]
  planning --> planning_work_stream
  planning_models_meta["models_meta"]
  planning --> planning_models_meta
  planning_tuning["tuning"]
  planning --> planning_tuning
  planning_learning["learning"]
  planning --> planning_learning
  planning_slo_regulator["slo_regulator"]
  planning --> planning_slo_regulator
  planning_self_healing["self_healing"]
  planning --> planning_self_healing
  queue["queue"]
  root --> queue
  queue_locking["locking"]
  queue --> queue_locking
  queue_storage["storage"]
  queue --> queue_storage
  research["research"]
  root --> research
  research_always_dumps_research["always_dumps_research"]
  research --> research_always_dumps_research
  research_library_replacements["library_replacements"]
  research --> research_library_replacements
  research_supermemory_integration["supermemory_integration"]
  research --> research_supermemory_integration
  research_library_psutil_research["library_psutil_research"]
  research --> research_library_psutil_research
  research_phase15_enterprise_lifecycle["phase15_enterprise_lifecycle"]
  research --> research_phase15_enterprise_lifecycle
  research_cost_routing["cost_routing"]
  research --> research_cost_routing
  research_hook_rust_phase4["hook_rust_phase4"]
  research --> research_hook_rust_phase4
  research_idea_seed_system["idea_seed_system"]
  research --> research_idea_seed_system
  research_autonomous_learning["autonomous_learning"]
  research --> research_autonomous_learning
  research_remote_compute_research["remote_compute_research"]
  research --> research_remote_compute_research
  research_agent_hierarchy_impl_research["agent_hierarchy_impl_research"]
  research --> research_agent_hierarchy_impl_research
  research_phase14_cost_sensing_tests["phase14_cost_sensing_tests"]
  research --> research_phase14_cost_sensing_tests
  research_phase13_compliance_profiles["phase13_compliance_profiles"]
  research --> research_phase13_compliance_profiles
  research_phase15_enterprise_compliance_tests["phase15_enterprise_compliance_tests"]
  research --> research_phase15_enterprise_compliance_tests
  research_phase14_autonomous_learning["phase14_autonomous_learning"]
  research --> research_phase14_autonomous_learning
  research_pareto_routing["pareto_routing"]
  research --> research_pareto_routing
  research_governance_dlq["governance_dlq"]
  research --> research_governance_dlq
  research_maif_artifacts["maif_artifacts"]
  research --> research_maif_artifacts
  research_agent_hierarchy["agent_hierarchy"]
  research --> research_agent_hierarchy
  research_governance_escalation_dlq_research["governance_escalation_dlq_research"]
  research --> research_governance_escalation_dlq_research
  research_economic_governance["economic_governance"]
  research --> research_economic_governance
  research_cost_sensitivity["cost_sensitivity"]
  research --> research_cost_sensitivity
  research_always_write_dumps["always_write_dumps"]
  research --> research_always_write_dumps
  research_phase13_cost_sensitivity_research["phase13_cost_sensitivity_research"]
  research --> research_phase13_cost_sensitivity_research
  research_cost_sensitivity_experiment["cost_sensitivity_experiment"]
  research --> research_cost_sensitivity_experiment
  research_remote_compute["remote_compute"]
  research --> research_remote_compute
  research_always_dumps["always_dumps"]
  research --> research_always_dumps
  research_library_diskcache_research["library_diskcache_research"]
  research --> research_library_diskcache_research
  routing["routing"]
  root --> routing
  routing_dispatch_graph["dispatch_graph"]
  routing --> routing_dispatch_graph
  routing_donut_adapter["donut_adapter"]
  routing --> routing_donut_adapter
  routing_cost_tracker["cost_tracker"]
  routing --> routing_cost_tracker
  routing_models["models"]
  routing --> routing_models
  routing_provider_types["provider_types"]
  routing --> routing_provider_types
  routing_scoring["scoring"]
  routing --> routing_scoring
  routing_pareto_router["pareto_router"]
  routing --> routing_pareto_router
  routing_harness_model_mapping["harness_model_mapping"]
  routing --> routing_harness_model_mapping
  routing_tool_router["tool_router"]
  routing --> routing_tool_router
  routing_preemption["preemption"]
  routing --> routing_preemption
  routing_model_metadata["model_metadata"]
  routing --> routing_model_metadata
  routing_task_router["task_router"]
  routing --> routing_task_router
  routing_litellm_responses_handler["litellm_responses_handler"]
  routing --> routing_litellm_responses_handler
  routing_litellm_router["litellm_router"]
  routing --> routing_litellm_router
  routing_auto_router["auto_router"]
  routing --> routing_auto_router
  routing_alerting["alerting"]
  routing --> routing_alerting
  rules["rules"]
  root --> rules
  rules_sync["sync"]
  rules --> rules_sync
  security["security"]
  root --> security
  security_auth_bridge["auth_bridge"]
  security --> security_auth_bridge
  security_payments["payments"]
  security --> security_payments
  security_hardware_id["hardware_id"]
  security --> security_hardware_id
  security_rbac["rbac"]
  security --> security_rbac
  security_homomorphic["homomorphic"]
  security --> security_homomorphic
  security_geo_guard["geo_guard"]
  security --> security_geo_guard
  security_tenancy["tenancy"]
  security --> security_tenancy
  security_quantum_safe["quantum_safe"]
  security --> security_quantum_safe
  security_sandboxing["sandboxing"]
  security --> security_sandboxing
  simulation["simulation"]
  root --> simulation
  simulation_replay["replay"]
  simulation --> simulation_replay
  sitback["sitback"]
  root --> sitback
  sitback_watchdog["watchdog"]
  sitback --> sitback_watchdog
  sitback_never_idle["never_idle"]
  sitback --> sitback_never_idle
  sitback_gardening["gardening"]
  sitback --> sitback_gardening
  sync["sync"]
  root --> sync
  sync_research_integration["research_integration"]
  sync --> sync_research_integration
  sync_plan_consolidation["plan_consolidation"]
  sync --> sync_plan_consolidation
  sync_orchestrator["orchestrator"]
  sync --> sync_orchestrator
  sync_unified_sync["unified_sync"]
  sync --> sync_unified_sync
  sync_audit_framework["audit_framework"]
  sync --> sync_audit_framework
  sync_work_stream_integration["work_stream_integration"]
  sync --> sync_work_stream_integration
  task["task"]
  root --> task
  task_validator["validator"]
  task --> task_validator
  task_sync["sync"]
  task --> task_sync
  task_types["types"]
  task --> task_types
  task_parser["parser"]
  task --> task_parser
  task_cli["cli"]
  task --> task_cli
  task_migrate["migrate"]
  task --> task_migrate
  team["team"]
  root --> team
  team_coordination["coordination"]
  team --> team_coordination
  team_manager["manager"]
  team --> team_manager
  tools["tools"]
  root --> tools
  tools_release_packager["release_packager"]
  tools --> tools_release_packager
  tools_research["research"]
  tools --> tools_research
  tools_terminal["terminal"]
  tools --> tools_terminal
  tools_cache["cache"]
  tools --> tools_cache
  tools_api_evolution["api_evolution"]
  tools --> tools_api_evolution
  tools_reddit_swarm["reddit_swarm"]
  tools --> tools_reddit_swarm
  tools_holdpty["holdpty"]
  tools --> tools_holdpty
  tools_human["human"]
  tools --> tools_human
  tools_agslag["agslag"]
  tools --> tools_agslag
  tools_xml_repair["xml_repair"]
  tools --> tools_xml_repair
  tools_deep_research["deep_research"]
  tools --> tools_deep_research
  tools_universal_adapter["universal_adapter"]
  tools --> tools_universal_adapter
  trace["trace"]
  root --> trace
  trace_recorder["recorder"]
  trace --> trace_recorder
  trace_integration["integration"]
  trace --> trace_integration
  trace_schema["schema"]
  trace --> trace_schema
  tui["tui"]
  root --> tui
  tui_themes["themes"]
  tui --> tui_themes
  tui_plugins["plugins"]
  tui --> tui_plugins
  tui_registry_tui["registry_tui"]
  tui --> tui_registry_tui
  tui_config["config"]
  tui --> tui_config
  tui_session_state["session_state"]
  tui --> tui_session_state
  tui_session["session"]
  tui --> tui_session
  tui_pane_manager["pane_manager"]
  tui --> tui_pane_manager
  tui_workstream_dashboard["workstream_dashboard"]
  tui --> tui_workstream_dashboard
  tui_compositor["compositor"]
  tui --> tui_compositor
  tui_compositor_v2["compositor_v2"]
  tui --> tui_compositor_v2
  tui_layouts["tui.layouts"]
  tui --> tui_layouts
  tui_layouts_manager["manager"]
  tui_layouts --> tui_layouts_manager
  tui_layouts_base["base"]
  tui_layouts --> tui_layouts_base
  tui_widgets["tui.widgets"]
  tui --> tui_widgets
  tui_widgets_menubar["menubar"]
  tui_widgets --> tui_widgets_menubar
  tui_widgets_statusbar["statusbar"]
  tui_widgets --> tui_widgets_statusbar
  tui_widgets_dialog["dialog"]
  tui_widgets --> tui_widgets_dialog
  tui_widgets_terminal_pane["terminal_pane"]
  tui_widgets --> tui_widgets_terminal_pane
  ui_compositor["ui.compositor"]
  ui --> ui_compositor
  ui_compositor_session_state["session_state"]
  ui_compositor --> ui_compositor_session_state
  ui_compositor_pane_manager["pane_manager"]
  ui_compositor --> ui_compositor_pane_manager
  ui_compositor_app["app"]
  ui_compositor --> ui_compositor_app
  ui_compositor_terminal_pane["terminal_pane"]
  ui_compositor --> ui_compositor_terminal_pane
  utils["utils"]
  root --> utils
  utils_error_helpers["error_helpers"]
  utils --> utils_error_helpers
  utils_edit_links["edit_links"]
  utils --> utils_edit_links
  utils_shell["shell"]
  utils --> utils_shell
  utils_workstream_automation["workstream_automation"]
  utils --> utils_workstream_automation
  utils_link_checker["link_checker"]
  utils --> utils_link_checker
  utils_helpers["helpers"]
  utils --> utils_helpers
  utils_reusable_helpers["reusable_helpers"]
  utils --> utils_reusable_helpers
  utils_batch_operations["batch_operations"]
  utils --> utils_batch_operations
  utils_workstream["workstream"]
  utils --> utils_workstream
  ux["ux"]
  root --> ux
  ux_alerts["alerts"]
  ux --> ux_alerts
  ux_explanations["explanations"]
  ux --> ux_explanations
  ux_pareto_viz["pareto_viz"]
  ux --> ux_pareto_viz
  ux_session_tui["session_tui"]
  ux --> ux_session_tui
  ux_kpis["kpis"]
  ux --> ux_kpis
  ux_fallback_ui["fallback_ui"]
  ux --> ux_fallback_ui
  ux_models_providers_tui["models_providers_tui"]
  ux --> ux_models_providers_tui
  ux_moral_ui["moral_ui"]
  ux --> ux_moral_ui
  ux_queue_tui["queue_tui"]
  ux --> ux_queue_tui
  ux_launch["launch"]
  ux --> ux_launch
  ux_compositor["compositor"]
  ux --> ux_compositor
  ux_calibration["calibration"]
  ux --> ux_calibration
  verification["verification"]
  root --> verification
  verification_omega_safety["omega_safety"]
  verification --> verification_omega_safety
  verification_proof_carrying["proof_carrying"]
  verification --> verification_proof_carrying
  verification_liveness["liveness"]
  verification --> verification_liveness
  verification_schema_formal["schema_formal"]
  verification --> verification_schema_formal
  verification_formal_loop["formal_loop"]
  verification --> verification_formal_loop
  verification_symbolic["symbolic"]
  verification --> verification_symbolic
  verification_tool_safety["tool_safety"]
  verification --> verification_tool_safety
  verification_ethics_proof["ethics_proof"]
  verification --> verification_ethics_proof
  verification_zkp["zkp"]
  verification --> verification_zkp
  verification_traceability["traceability"]
  verification --> verification_traceability
  work_packages["work_packages"]
  root --> work_packages
  work_packages_light_speed["light_speed"]
  work_packages --> work_packages_light_speed
  work_packages_neural_link["neural_link"]
  work_packages --> work_packages_neural_link
  work_packages_swarm_memory["swarm_memory"]
  work_packages --> work_packages_swarm_memory
  work_packages_timeline_merge["timeline_merge"]
  work_packages --> work_packages_timeline_merge
  work_packages_virtualized_consciousness["virtualized_consciousness"]
  work_packages --> work_packages_virtualized_consciousness
  work_packages_stellar_energy["stellar_energy"]
  work_packages --> work_packages_stellar_energy
  work_packages_sensor_mesh["sensor_mesh"]
  work_packages --> work_packages_sensor_mesh
  work_packages_final_state_consensus["final_state_consensus"]
  work_packages --> work_packages_final_state_consensus
  work_packages_matrioshka_brain["matrioshka_brain"]
  work_packages --> work_packages_matrioshka_brain
  work_packages_substrate_migration["substrate_migration"]
  work_packages --> work_packages_substrate_migration
  work_packages_molecular_compute["molecular_compute"]
  work_packages --> work_packages_molecular_compute
  work_packages_bio_digital["bio_digital"]
  work_packages --> work_packages_bio_digital
  work_packages_sensory_context["sensory_context"]
  work_packages --> work_packages_sensory_context
  work_packages_latency_scheduling["latency_scheduling"]
  work_packages --> work_packages_latency_scheduling
  work_packages_cold_storage["cold_storage"]
  work_packages --> work_packages_cold_storage
  work_packages_bio_feedback["bio_feedback"]
  work_packages --> work_packages_bio_feedback
  work_packages_co_consciousness["co_consciousness"]
  work_packages --> work_packages_co_consciousness
  work_packages_impact_simulation["impact_simulation"]
  work_packages --> work_packages_impact_simulation
  work_packages_gravity_scheduling["gravity_scheduling"]
  work_packages --> work_packages_gravity_scheduling
```

---
