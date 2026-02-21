// Auto-generated usage examples for progress
// Source: generate-api-docs.py

import { decorator, measure_time, print_section, print_status, print_step, progress_context, spinner_context, wrapper } from "./progress";

// Call decorator
decorator(undefined as unknown as any);
// Call measure_time
measure_time("example_description");
// Call print_section
print_section("example_title");
// Call print_status
print_status("example_message", "example_status");
// Call print_step
print_step(0, 0, "example_message");
// Call progress_context
progress_context("example_description", undefined as unknown as any, false, false);
// Call spinner_context
spinner_context("example_message");
// Call wrapper
wrapper();
