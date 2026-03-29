// Auto-generated usage examples for cli_git
// Source: generate-api-docs.py

import { add, callback, commit, diff, get_agent_id, lock_cleanup_main, lock_cleanup_service, log, merge, run_system_git, status } from "./cli_git";

// Call add
add(undefined as unknown as Array<string>, "example_agent_id", "example_project_root");
// Call callback
callback(undefined as unknown as typer.Context);
// Call commit
commit("example_message", "example_agent_id", "example_ref", "example_project_root");
// Call diff
diff("example_project_root", "example_agent_id", false);
// Call get_agent_id
get_agent_id();
// Call lock_cleanup_main
lock_cleanup_main(undefined as unknown as typer.Context, undefined as unknown as Array<string>, 0, false);
// Call lock_cleanup_service
lock_cleanup_service("example_action");
// Call log
log("example_project_root", 0);
// Call merge
merge("example_base", "example_ours", "example_theirs", "example_output");
// Call run_system_git
run_system_git(undefined as unknown as Array<string>);
// Call status
status("example_agent_id", "example_project_root", false);
