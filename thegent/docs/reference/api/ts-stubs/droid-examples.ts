// Auto-generated usage examples for droid
// Source: generate-api-docs.py

import { CodexRunner, CustomCliRunner, DroidRunner, get_droid_runner, run } from "./droid";

// Create a CodexRunner instance
const codexrunner = new CodexRunner("example_droid_name", "example_droids_dir", "example_codex_cmd", "example_model", undefined as unknown as any);
codexrunner.run("example_prompt", undefined as unknown as any, "example_mode", 0);

// Create a CustomCliRunner instance
const customclirunner = new CustomCliRunner("example_droid_name", "example_droids_dir", "example_custom_cmd", "example_model");
customclirunner.run("example_prompt", undefined as unknown as any, "example_mode", 0);

// Create a DroidRunner instance
const droidrunner = new DroidRunner("example_droid_name", "example_droids_dir", "example_droid_cmd", "example_model", undefined as unknown as any);
droidrunner.run("example_prompt", undefined as unknown as any, "example_mode", 0);

// Call get_droid_runner
get_droid_runner("example_backend", "example_droid_name", "example_droids_dir");
// Call run
run(undefined as unknown as any, "example_prompt", undefined as unknown as any, "example_mode", 0);
