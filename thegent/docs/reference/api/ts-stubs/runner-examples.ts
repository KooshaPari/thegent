// Auto-generated usage examples for runner
// Source: generate-api-docs.py

import { MAIFRunner, record_run_end, record_run_start } from "./runner";

// Create a MAIFRunner instance
const maifrunner = new MAIFRunner();
maifrunner.record_run_end("example_run_id", "example_status", "example_output_summary");
maifrunner.record_run_start("example_run_id", "example_owner", "example_prompt", "example_agent");

// Call record_run_end
record_run_end(undefined as unknown as any, "example_run_id", "example_status", "example_output_summary");
// Call record_run_start
record_run_start(undefined as unknown as any, "example_run_id", "example_owner", "example_prompt", "example_agent");
