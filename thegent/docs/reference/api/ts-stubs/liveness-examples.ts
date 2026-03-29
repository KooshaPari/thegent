// Auto-generated usage examples for liveness
// Source: generate-api-docs.py

import { LivenessChecker, LivenessViolation, check_invariants, record_step } from "./liveness";

// Create a LivenessChecker instance
const livenesschecker = new LivenessChecker("example_run_id", 0, 0);
livenesschecker.check_invariants();
livenesschecker.record_step("example_step_type", undefined as unknown as Record<(str, Any)>);

// Create a LivenessViolation instance
const livenessviolation = new LivenessViolation();

// Call check_invariants
check_invariants(undefined as unknown as any);
// Call record_step
record_step(undefined as unknown as any, "example_step_type", undefined as unknown as Record<(str, Any)>);
