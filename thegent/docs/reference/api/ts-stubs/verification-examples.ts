// Auto-generated usage examples for verification
// Source: generate-api-docs.py

import { CoTVerifier, VerificationResult, get_summary, verify_step } from "./verification";

// Create a CoTVerifier instance
const cotverifier = new CoTVerifier("example_run_id");
cotverifier.get_summary();
cotverifier.verify_step("example_step_id", "example_prompt", "example_reasoning");

// Create a VerificationResult instance
const verificationresult = new VerificationResult();

// Call get_summary
get_summary(undefined as unknown as any);
// Call verify_step
verify_step(undefined as unknown as any, "example_step_id", "example_prompt", "example_reasoning");
