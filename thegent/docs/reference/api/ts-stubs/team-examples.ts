// Auto-generated usage examples for team
// Source: generate-api-docs.py

import { team_create, team_crew, team_delegate, team_hierarchy, team_list, team_status, teammates_delegate, teammates_list, teammates_show, teammates_status } from "./team";

// Call team_create
team_create("example_name", undefined as unknown as Array<string>, "example_objective");
// Call team_crew
team_crew("example_format");
// Call team_delegate
team_delegate("example_prompt", "example_teammate");
// Call team_hierarchy
team_hierarchy("example_format");
// Call team_list
team_list("example_format");
// Call team_status
team_status("example_run_id");
// Call teammates_delegate
teammates_delegate("example_teammate", "example_task", "example_parent_run_id");
// Call teammates_list
teammates_list();
// Call teammates_show
teammates_show("example_req_id");
// Call teammates_status
teammates_status("example_run_id");
