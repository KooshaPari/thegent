// Auto-generated usage examples for cli_crew
// Source: generate-api-docs.py

import { crew_add_agent_cmd, crew_add_task_cmd, crew_create_cmd, crew_execute_cmd, crew_list_cmd, crew_show_cmd, crew_status_cmd } from "./cli_crew";

// Call crew_add_agent_cmd
crew_add_agent_cmd("example_crew_id", "example_role", "example_name", "example_description", "example_capabilities", "example_model");
// Call crew_add_task_cmd
crew_add_task_cmd("example_crew_id", "example_description", "example_dependencies", "example_agent_id");
// Call crew_create_cmd
crew_create_cmd("example_name", "example_description", "example_execution_mode", "example_output");
// Call crew_execute_cmd
crew_execute_cmd("example_crew_file", "example_cwd", "example_mode", 0, "example_model");
// Call crew_list_cmd
crew_list_cmd();
// Call crew_show_cmd
crew_show_cmd("example_crew_id");
// Call crew_status_cmd
crew_status_cmd("example_crew_id");
