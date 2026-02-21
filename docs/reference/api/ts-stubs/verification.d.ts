// Auto-generated TypeScript declarations for verification
// Source: generate-api-docs.py

export declare class CoTVerifier {
  constructor(run_id: string);
  get_summary(): void;
  verify_step(step_id: string, prompt: string, reasoning: string): void;
}

export declare class VerificationResult extends BaseModel {
}

export declare function get_summary(): void;
export declare function verify_step(step_id: string, prompt: string, reasoning: string): void;
