// Auto-generated usage examples for evidence
// Source: generate-api-docs.py

import { PromotionGate, capture_evidence, validate_promotion, verify_evidence_hash } from "./evidence";

// Create a PromotionGate instance
const promotiongate = new PromotionGate("example_session_dir");
promotiongate.capture_evidence("example_run_id", undefined as unknown as any);
promotiongate.validate_promotion(undefined as unknown as any, undefined as unknown as FallbackPolicy);
promotiongate.verify_evidence_hash("example_run_id", "example_phase", "example_expected_hash");

// Call capture_evidence
capture_evidence(undefined as unknown as any, "example_run_id", undefined as unknown as any);
// Call validate_promotion
validate_promotion(undefined as unknown as any, undefined as unknown as any, undefined as unknown as FallbackPolicy);
// Call verify_evidence_hash
verify_evidence_hash(undefined as unknown as any, "example_run_id", "example_phase", "example_expected_hash");
