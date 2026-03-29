// Auto-generated usage examples for state_machine
// Source: generate-api-docs.py

import { FallbackStateMachine, OrchestrationState, PromotionGate, capture_evidence, run, suggest_fallbacks, validate_promotion, validate_transition } from "./state_machine";

// Create a FallbackStateMachine instance
const fallbackstatemachine = new FallbackStateMachine(undefined as unknown as Array<string>, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, 0, 0);
fallbackstatemachine.run(undefined as unknown as any, "example_prompt", undefined as unknown as any);
fallbackstatemachine.suggest_fallbacks();
fallbackstatemachine.validate_transition("example_from_state", "example_to_state");

// Create a OrchestrationState instance
const orchestrationstate = new OrchestrationState();

// Create a PromotionGate instance
const promotiongate = new PromotionGate("example_session_dir");
promotiongate.capture_evidence("example_run_id", undefined as unknown as any);
promotiongate.validate_promotion(undefined as unknown as any, undefined as unknown as any);

// Call capture_evidence
capture_evidence(undefined as unknown as any, "example_run_id", undefined as unknown as any);
// Call run
run(undefined as unknown as any, undefined as unknown as any, "example_prompt", undefined as unknown as any);
// Call suggest_fallbacks
suggest_fallbacks(undefined as unknown as any);
// Call validate_promotion
validate_promotion(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call validate_transition
validate_transition(undefined as unknown as any, "example_from_state", "example_to_state");
