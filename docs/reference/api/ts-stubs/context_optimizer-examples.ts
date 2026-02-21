// Auto-generated usage examples for context_optimizer
// Source: generate-api-docs.py

import { ContextOptimizer, compress_whitespace, estimate_tokens, optimize, optimize_context, optimize_prompt, remove_secrets, truncate_smart } from "./context_optimizer";

// Create a ContextOptimizer instance
const contextoptimizer = new ContextOptimizer(undefined as unknown as any, undefined as unknown as any);
contextoptimizer.compress_whitespace("example_text");
contextoptimizer.estimate_tokens("example_text");
contextoptimizer.optimize("example_context", false);
contextoptimizer.optimize_prompt("example_prompt", undefined as unknown as any);
contextoptimizer.remove_secrets("example_text");
contextoptimizer.truncate_smart("example_text", 0);

// Call compress_whitespace
compress_whitespace(undefined as unknown as any, "example_text");
// Call estimate_tokens
estimate_tokens(undefined as unknown as any, "example_text");
// Call optimize
optimize(undefined as unknown as any, "example_context", false);
// Call optimize_context
optimize_context("example_context", undefined as unknown as any, false);
// Call optimize_prompt
optimize_prompt(undefined as unknown as any, "example_prompt", undefined as unknown as any);
// Call remove_secrets
remove_secrets(undefined as unknown as any, "example_text");
// Call truncate_smart
truncate_smart(undefined as unknown as any, "example_text", 0);
