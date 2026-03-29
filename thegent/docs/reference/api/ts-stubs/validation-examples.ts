// Auto-generated usage examples for validation
// Source: generate-api-docs.py

import { InvariantViolation, SemanticPolicyEngine, SemanticValidationError, add_rule, ensure_valid_csm, evaluate, validate_csm } from "./validation";

// Create a InvariantViolation instance
const invariantviolation = new InvariantViolation();

// Create a SemanticPolicyEngine instance
const semanticpolicyengine = new SemanticPolicyEngine(false);
semanticpolicyengine.add_rule(undefined as unknown as Callable<(Any, list<str])>>);
semanticpolicyengine.evaluate(undefined as unknown as CanonicalStructuredMessage);

// Create a SemanticValidationError instance
const semanticvalidationerror = new SemanticValidationError();

// Call add_rule
add_rule(undefined as unknown as any, undefined as unknown as Callable<(Any, list<str])>>);
// Call ensure_valid_csm
ensure_valid_csm(undefined as unknown as CanonicalStructuredMessage);
// Call evaluate
evaluate(undefined as unknown as any, undefined as unknown as CanonicalStructuredMessage);
// Call validate_csm
validate_csm(undefined as unknown as CanonicalStructuredMessage);
