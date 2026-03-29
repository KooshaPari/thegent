// Auto-generated TypeScript declarations for liveness
// Source: generate-api-docs.py

export declare class LivenessChecker {
  constructor(run_id: string, max_retries: number, progress_timeout_s: number);
  check_invariants(): void;
  record_step(step_type: string, state: Record<(str, Any)>): void;
}

export declare class LivenessViolation extends BaseModel {
}

export declare function check_invariants(): void;
export declare function record_step(step_type: string, state: Record<(str, Any)>): void;
