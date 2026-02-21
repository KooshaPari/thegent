// Auto-generated usage examples for git_enhance
// Source: generate-api-docs.py

import { GitEnhance, detect_lock, git_status, passthrough_to_agent } from "./git_enhance";

// Create a GitEnhance instance
const gitenhance = new GitEnhance(0);
gitenhance.detect_lock("example_repo_path");
gitenhance.git_status("example_repo_path", false);
gitenhance.passthrough_to_agent("example_command", undefined as unknown as Array<string>);

// Call detect_lock
detect_lock(undefined as unknown as any, "example_repo_path");
// Call git_status
git_status(undefined as unknown as any, "example_repo_path", false);
// Call passthrough_to_agent
passthrough_to_agent(undefined as unknown as any, "example_command", undefined as unknown as Array<string>);
