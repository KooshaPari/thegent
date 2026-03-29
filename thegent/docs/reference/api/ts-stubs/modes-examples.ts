// Auto-generated usage examples for modes
// Source: generate-api-docs.py

import { register_modes, thegent_dag_ready, thegent_dag_recover, thegent_dag_sync, thegent_discussion_add_question, thegent_discussion_finalize, thegent_discussion_start, thegent_plan_approve, thegent_plan_create, thegent_plan_get, thegent_plan_save, thegent_plan_status, thegent_protocol_get, thegent_protocol_list, thegent_research_finalize, thegent_team_create, thegent_team_delegate, thegent_team_list, thegent_validation_report } from "./modes";

// Call register_modes
register_modes(undefined as unknown as FastMCP);
// Call thegent_dag_ready
thegent_dag_ready(undefined as unknown as any);
// Call thegent_dag_recover
thegent_dag_recover(undefined as unknown as any, "example_action");
// Call thegent_dag_sync
thegent_dag_sync(undefined as unknown as any, false);
// Call thegent_discussion_add_question
thegent_discussion_add_question("example_session_id", "example_question", undefined as unknown as any);
// Call thegent_discussion_finalize
thegent_discussion_finalize("example_brief_content", undefined as unknown as any, undefined as unknown as any);
// Call thegent_discussion_start
thegent_discussion_start("example_topic", undefined as unknown as any);
// Call thegent_plan_approve
thegent_plan_approve("example_plan_id", undefined as unknown as any);
// Call thegent_plan_create
thegent_plan_create("example_prompt", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call thegent_plan_get
thegent_plan_get(undefined as unknown as any, undefined as unknown as any);
// Call thegent_plan_save
thegent_plan_save("example_content", undefined as unknown as any, undefined as unknown as any);
// Call thegent_plan_status
thegent_plan_status(undefined as unknown as any);
// Call thegent_protocol_get
thegent_protocol_get(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call thegent_protocol_list
thegent_protocol_list(undefined as unknown as any);
// Call thegent_research_finalize
thegent_research_finalize("example_report_content", undefined as unknown as any, undefined as unknown as any);
// Call thegent_team_create
thegent_team_create("example_prompt", "example_mode", 0, undefined as unknown as any);
// Call thegent_team_delegate
thegent_team_delegate("example_teammate_id", "example_prompt", undefined as unknown as any);
// Call thegent_team_list
thegent_team_list(undefined as unknown as any);
// Call thegent_validation_report
thegent_validation_report(undefined as unknown as any, undefined as unknown as any);
