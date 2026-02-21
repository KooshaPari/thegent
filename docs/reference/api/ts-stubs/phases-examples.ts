// Auto-generated usage examples for phases
// Source: generate-api-docs.py

import { PhaseTransitionContract, allowed_targets, validate, validate_transition } from "./phases";

// Create a PhaseTransitionContract instance
const phasetransitioncontract = new PhaseTransitionContract();
phasetransitioncontract.allowed_targets("example_from_state");
phasetransitioncontract.validate("example_from_state", "example_to_state");

// Call allowed_targets
allowed_targets(undefined as unknown as any, "example_from_state");
// Call validate
validate(undefined as unknown as any, "example_from_state", "example_to_state");
// Call validate_transition
validate_transition("example_from_state", "example_to_state");
