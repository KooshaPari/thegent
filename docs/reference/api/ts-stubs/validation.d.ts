// Auto-generated TypeScript declarations for validation
// Source: generate-api-docs.py

export declare class InvariantViolation extends SemanticValidationError {
}

export declare class SemanticPolicyEngine {
  constructor(strict: boolean);
  add_rule(rule: Callable<(Any, list<str])>>): void;
  evaluate(csm: CanonicalStructuredMessage): void;
}

export declare class SemanticValidationError extends Exception {
}

export declare function add_rule(rule: Callable<(Any, list<str])>>): void;
export declare function ensure_valid_csm(csm: CanonicalStructuredMessage): void;
export declare function evaluate(csm: CanonicalStructuredMessage): void;
export declare function validate_csm(csm: CanonicalStructuredMessage): void;
