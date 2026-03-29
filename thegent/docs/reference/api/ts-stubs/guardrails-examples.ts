// Auto-generated usage examples for guardrails
// Source: generate-api-docs.py

import { CommandValidator, Guardrails, RateLimit, RateLimiter, SecretManager, SecurityInvariant, TokenOptimizer, add_limit, check, check_invariant, check_rate_limit, compress_context, estimate_tokens, get_secret, mask_secret, optimize_context, optimize_prompt, remove_secrets, reset, sanitize_path, validate_and_sanitize_command, validate_command, validate_secret_present } from "./guardrails";

// Create a CommandValidator instance
const commandvalidator = new CommandValidator();
commandvalidator.sanitize_path("example_path");
commandvalidator.validate_command(undefined as unknown as any);

// Create a Guardrails instance
const guardrails = new Guardrails();
guardrails.check_invariant("example_invariant_name", undefined as unknown as any);
guardrails.optimize_context("example_context", undefined as unknown as any);
guardrails.validate_and_sanitize_command(undefined as unknown as any, "example_operation_type");

// Create a RateLimit instance
const ratelimit = new RateLimit();
ratelimit.check();
ratelimit.reset();

// Create a RateLimiter instance
const ratelimiter = new RateLimiter();
ratelimiter.add_limit("example_key", 0, 0);
ratelimiter.check("example_key");
ratelimiter.reset("example_key");

// Create a SecretManager instance
const secretmanager = new SecretManager();
secretmanager.get_secret("example_name", undefined as unknown as any);
secretmanager.mask_secret("example_value");
secretmanager.validate_secret_present("example_name");

// Create a SecurityInvariant instance
const securityinvariant = new SecurityInvariant();

// Create a TokenOptimizer instance
const tokenoptimizer = new TokenOptimizer();
tokenoptimizer.compress_context("example_context", 0);
tokenoptimizer.estimate_tokens("example_text");
tokenoptimizer.optimize_prompt("example_prompt", undefined as unknown as any);
tokenoptimizer.remove_secrets("example_text");

// Call add_limit
add_limit(undefined as unknown as any, "example_key", 0, 0);
// Call check
check(undefined as unknown as any, "example_key");
// Call check_invariant
check_invariant(undefined as unknown as any, "example_invariant_name", undefined as unknown as any);
// Call check_rate_limit
check_rate_limit("example_operation_type");
// Call compress_context
compress_context("example_context", 0);
// Call estimate_tokens
estimate_tokens("example_text");
// Call get_secret
get_secret("example_name", undefined as unknown as any);
// Call mask_secret
mask_secret("example_value");
// Call optimize_context
optimize_context(undefined as unknown as any, "example_context", undefined as unknown as any);
// Call optimize_prompt
optimize_prompt("example_prompt", undefined as unknown as any);
// Call remove_secrets
remove_secrets("example_text");
// Call reset
reset(undefined as unknown as any, "example_key");
// Call sanitize_path
sanitize_path("example_path");
// Call validate_and_sanitize_command
validate_and_sanitize_command(undefined as unknown as any, undefined as unknown as any, "example_operation_type");
// Call validate_command
validate_command(undefined as unknown as any);
// Call validate_secret_present
validate_secret_present("example_name");
