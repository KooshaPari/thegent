// Auto-generated TypeScript declarations for resilience
// Source: generate-api-docs.py

export declare class FailureKind extends StrEnum {
}

export declare class FailureTaxonomy extends StrEnum {
}

export declare class RecoveryEngine {
  suggest_playbook(failure_type: string): void;
}

export declare class RetryBudget {
}

export declare class ToolCircuitBreaker {
  constructor(name: string, threshold: number, window_s: number);
  is_open(): void;
  record_failure(): void;
}

export declare class ToolClass extends StrEnum {
}

export declare class TransientAgentError extends Exception {
  constructor(result: RunResult);
}

export declare class UsageLimitError extends Exception {
  constructor(result: RunResult, agent: string);
}

export declare function classify_failure(result: RunResult): void;
export declare function classify_to_taxonomy(error_msg: string): void;
export declare function decorator(fn: Callable<(Ellipsis, T)>): Callable<(Ellipsis, T)>;
export declare function is_open(): void;
export declare function is_retryable(result: RunResult): void;
export declare function is_usage_limit(result: RunResult): void;
export declare function record_failure(): void;
export declare function suggest_playbook(failure_type: string): void;
export declare function with_retry(max_attempts: number, min_wait: number, max_wait: number): void;
