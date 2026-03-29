// Auto-generated TypeScript declarations for self_healing
// Source: generate-api-docs.py

export declare class RecoveryRouter {
  constructor();
  attempt_recovery(result: RunResult): void;
  back_project_failure(run_id: string, prompt: string, failure_type: string): void;
}

export declare class StabilityTracker {
  constructor(window_size: number);
  get_stability_score(): void;
  record_result(result: RunResult): void;
}

export declare function attempt_recovery(result: RunResult): void;
export declare function back_project_failure(run_id: string, prompt: string, failure_type: string): void;
export declare function get_stability_score(): void;
export declare function record_result(result: RunResult): void;
