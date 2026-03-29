// Auto-generated usage examples for omega_safety
// Source: generate-api-docs.py

import { OmegaInvariantViolation, OmegaSafetyGuard, is_safe, verify_action } from "./omega_safety";

// Create a OmegaInvariantViolation instance
const omegainvariantviolation = new OmegaInvariantViolation();

// Create a OmegaSafetyGuard instance
const omegasafetyguard = new OmegaSafetyGuard();
omegasafetyguard.is_safe("example_action_id", undefined as unknown as Record<(str, Any)>);
omegasafetyguard.verify_action("example_action_id", undefined as unknown as Record<(str, Any)>);

// Call is_safe
is_safe(undefined as unknown as any, "example_action_id", undefined as unknown as Record<(str, Any)>);
// Call verify_action
verify_action(undefined as unknown as any, "example_action_id", undefined as unknown as Record<(str, Any)>);
