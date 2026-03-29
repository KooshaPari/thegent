// Auto-generated usage examples for snapshot
// Source: generate-api-docs.py

import { ForensicSnapshotter, capture_post_run, capture_pre_run } from "./snapshot";

// Create a ForensicSnapshotter instance
const forensicsnapshotter = new ForensicSnapshotter("example_session_dir");
forensicsnapshotter.capture_post_run("example_run_id", "example_project_root", 0);
forensicsnapshotter.capture_pre_run("example_run_id", "example_project_root");

// Call capture_post_run
capture_post_run(undefined as unknown as any, "example_run_id", "example_project_root", 0);
// Call capture_pre_run
capture_pre_run(undefined as unknown as any, "example_run_id", "example_project_root");
