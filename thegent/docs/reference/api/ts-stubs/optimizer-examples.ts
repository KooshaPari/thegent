// Auto-generated usage examples for optimizer
// Source: generate-api-docs.py

import { PromptOptimizer, PromptVersion, get_best_prompt, optimize, record_run } from "./optimizer";

// Create a PromptOptimizer instance
const promptoptimizer = new PromptOptimizer("example_agent_id", undefined as unknown as any);
promptoptimizer.get_best_prompt();
promptoptimizer.optimize("example_current_prompt", undefined as unknown as any);
promptoptimizer.record_run("example_version_id", undefined as unknown as RunResult, 0, 0);

// Create a PromptVersion instance
const promptversion = new PromptVersion();

// Call get_best_prompt
get_best_prompt(undefined as unknown as any);
// Call optimize
optimize(undefined as unknown as any, "example_current_prompt", undefined as unknown as any);
// Call record_run
record_run(undefined as unknown as any, "example_version_id", undefined as unknown as RunResult, 0, 0);
