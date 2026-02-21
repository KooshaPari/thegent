// Auto-generated usage examples for codex_proxy
// Source: generate-api-docs.py

import { CodexProxyRunner, run, run_with_metadata } from "./codex_proxy";

// Create a CodexProxyRunner instance
const codexproxyrunner = new CodexProxyRunner("example_agent_name", undefined as unknown as any, "example_model", undefined as unknown as any);
codexproxyrunner.run("example_prompt", undefined as unknown as any, "example_mode", 0);
codexproxyrunner.run_with_metadata("example_prompt", undefined as unknown as any, "example_mode", 0);

// Call run
run(undefined as unknown as any, "example_prompt", undefined as unknown as any, "example_mode", 0);
// Call run_with_metadata
run_with_metadata(undefined as unknown as any, "example_prompt", undefined as unknown as any, "example_mode", 0);
