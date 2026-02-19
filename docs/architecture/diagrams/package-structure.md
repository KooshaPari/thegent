```mermaid
graph TD
  %% Thegent Package Structure
  root["thegent"]
  root_cli_document_queue["cli_document_queue"]
  root --> root_cli_document_queue
  root_execution["execution"]
  root --> root_execution
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
  root_mgmt_manage["mgmt_manage"]
  root --> root_mgmt_manage
  root_tui["tui"]
  root --> root_tui
  root_sitback_plugins["sitback_plugins"]
  root --> root_sitback_plugins
  root_install["install"]
  root --> root_install
  root_mcp_sitback["mcp_sitback"]
  root --> root_mcp_sitback
  root_main["main"]
  root --> root_main
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
  agents_tool_adapter["tool_adapter"]
  agents --> agents_tool_adapter
  agents_optimizer["optimizer"]
  agents --> agents_optimizer
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
  context["context"]
  root --> context
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
  governance_plugin_lifecycle["plugin_lifecycle"]
  governance --> governance_plugin_lifecycle
  governance_personas["personas"]
  governance --> governance_personas
  governance_scanner["scanner"]
  governance --> governance_scanner
  governance_agileplus["agileplus"]
  governance --> governance_agileplus
  governance_support["support"]
  governance --> governance_support
  governance_triggers["triggers"]
  governance --> governance_triggers
  governance_audit["audit"]
  governance --> governance_audit
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
  governance_analyzer["analyzer"]
  governance --> governance_analyzer
  governance_ledger["ledger"]
  governance --> governance_ledger
  governance_health_score["health_score"]
  governance --> governance_health_score
  governance_agent_deployer["agent_deployer"]
  governance --> governance_agent_deployer
  governance_drift["drift"]
  governance --> governance_drift
  governance_overrides["overrides"]
  governance --> governance_overrides
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
  governance_cost_controller["cost_controller"]
  governance --> governance_cost_controller
  governance_verification_gate["verification_gate"]
  governance --> governance_verification_gate
  governance_cost["cost"]
  governance --> governance_cost
  governance_sharecli_bridge["sharecli_bridge"]
  governance --> governance_sharecli_bridge
  governance_tee_check["tee_check"]
  governance --> governance_tee_check
  governance_federation["federation"]
  governance --> governance_federation
  governance_meta["meta"]
  governance --> governance_meta
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
  infra_runtime_init["runtime_init"]
  infra --> infra_runtime_init
  infra_drift_corrector["drift_corrector"]
  infra --> infra_drift_corrector
  infra_fast_file_watcher["fast_file_watcher"]
  infra --> infra_fast_file_watcher
  infra_fast_yaml_parser["fast_yaml_parser"]
  infra --> infra_fast_yaml_parser
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
  infra_fast_subprocess["fast_subprocess"]
  infra --> infra_fast_subprocess
  infra_fast_uuid["fast_uuid"]
  infra --> infra_fast_uuid
  infra_fast_compression["fast_compression"]
  infra --> infra_fast_compression
  infra_fast_path_ops["fast_path_ops"]
  infra --> infra_fast_path_ops
  infra_fast_cache["fast_cache"]
  infra --> infra_fast_cache
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
  learning["learning"]
  root --> learning
  learning_promotion["promotion"]
  learning --> learning_promotion
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
  observability_egress["egress"]
  observability --> observability_egress
  observability_otel_instrumentation["otel_instrumentation"]
  observability --> observability_otel_instrumentation
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
  orchestration_lanes["lanes"]
  orchestration --> orchestration_lanes
  orchestration_transactions["transactions"]
  orchestration --> orchestration_transactions
  orchestration_graph["graph"]
  orchestration --> orchestration_graph
  orchestration_prompts["prompts"]
  orchestration --> orchestration_prompts
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
  planning["planning"]
  root --> planning
  planning_simulation["simulation"]
  planning --> planning_simulation
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
  planning_selector["selector"]
  planning --> planning_selector
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
  queue_storage["storage"]
  queue --> queue_storage
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
  routing_preemption["preemption"]
  routing --> routing_preemption
  routing_task_router["task_router"]
  routing --> routing_task_router
  routing_litellm_router["litellm_router"]
  routing --> routing_litellm_router
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
  sitback["sitback"]
  root --> sitback
  sitback_watchdog["watchdog"]
  sitback --> sitback_watchdog
  sitback_never_idle["never_idle"]
  sitback --> sitback_never_idle
  sitback_gardening["gardening"]
  sitback --> sitback_gardening
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
  tools_human["human"]
  tools --> tools_human
  tools_xml_repair["xml_repair"]
  tools --> tools_xml_repair
  tools_universal_adapter["universal_adapter"]
  tools --> tools_universal_adapter
  utils["utils"]
  root --> utils
  utils_shell["shell"]
  utils --> utils_shell
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
```
