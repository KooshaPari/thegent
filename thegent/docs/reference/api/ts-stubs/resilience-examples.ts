// Auto-generated usage examples for resilience
// Source: generate-api-docs.py

import { FailureKind, FailureTaxonomy, RecoveryEngine, RetryBudget, ToolCircuitBreaker, ToolClass, TransientAgentError, UsageLimitError, classify_failure, classify_to_taxonomy, decorator, is_open, is_retryable, is_usage_limit, record_failure, suggest_playbook, with_retry } from "./resilience";

// Create a FailureKind instance
const failurekind = new FailureKind();

// Create a FailureTaxonomy instance
const failuretaxonomy = new FailureTaxonomy();

// Create a RecoveryEngine instance
const recoveryengine = new RecoveryEngine();
recoveryengine.suggest_playbook("example_failure_type");

// Create a RetryBudget instance
const retrybudget = new RetryBudget();

// Create a ToolCircuitBreaker instance
const toolcircuitbreaker = new ToolCircuitBreaker("example_name", 0, 0);
toolcircuitbreaker.is_open();
toolcircuitbreaker.record_failure();

// Create a ToolClass instance
const toolclass = new ToolClass();

// Create a TransientAgentError instance
const transientagenterror = new TransientAgentError(undefined as unknown as RunResult);

// Create a UsageLimitError instance
const usagelimiterror = new UsageLimitError(undefined as unknown as RunResult, "example_agent");

// Call classify_failure
classify_failure(undefined as unknown as RunResult);
// Call classify_to_taxonomy
classify_to_taxonomy("example_error_msg");
// Call decorator
decorator(undefined as unknown as Callable<(Ellipsis, T)>);
// Call is_open
is_open(undefined as unknown as any);
// Call is_retryable
is_retryable(undefined as unknown as RunResult);
// Call is_usage_limit
is_usage_limit(undefined as unknown as RunResult);
// Call record_failure
record_failure(undefined as unknown as any);
// Call suggest_playbook
suggest_playbook(undefined as unknown as any, "example_failure_type");
// Call with_retry
with_retry(0, 0, 0);
