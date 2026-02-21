// Auto-generated TypeScript declarations for evidence
// Source: generate-api-docs.py

export declare class PromotionGate {
  constructor(session_dir: string);
  capture_evidence(run_id: string, csm: any): void;
  validate_promotion(csm: any, policy: FallbackPolicy): void;
  verify_evidence_hash(run_id: string, phase: string, expected_hash: string): void;
}

export declare function capture_evidence(run_id: string, csm: any): void;
export declare function validate_promotion(csm: any, policy: FallbackPolicy): void;
export declare function verify_evidence_hash(run_id: string, phase: string, expected_hash: string): void;
