// Auto-generated usage examples for summary
// Source: generate-api-docs.py

import { get_chat_logs, get_git_commits, get_project_key, get_time_range, summary_impl } from "./summary";

// Call get_chat_logs
get_chat_logs("example_session_dir", "example_project_key", undefined as unknown as datetime, undefined as unknown as datetime);
// Call get_git_commits
get_git_commits("example_project_path", undefined as unknown as datetime, undefined as unknown as datetime);
// Call get_project_key
get_project_key("example_project_path");
// Call get_time_range
get_time_range("example_period");
// Call summary_impl
summary_impl("example_period", undefined as unknown as any, false, "example_agent");
