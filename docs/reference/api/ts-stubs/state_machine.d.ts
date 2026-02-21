// Auto-generated TypeScript declarations for state_machine
// Source: generate-api-docs.py

export declare class FallbackStateMachine {
  constructor(providers: Array<string>, run_id: any, policy: any, telemetry: any, max_retries_per_provider: number, retry_delay_base: number);
  run(runner_factory: any, prompt: string, model: any): void;
  suggest_fallbacks(): void;
  validate_transition(from_state: string, to_state: string): void;
}

export declare class OrchestrationState {
}

export declare class PromotionGate {
  constructor(session_dir: string);
  capture_evidence(run_id: string, csm: any): void;
  validate_promotion(csm: any, policy: any): void;
}

export declare function capture_evidence(run_id: string, csm: any): void;
export declare function run(runner_factory: any, prompt: string, model: any): void;
export declare function suggest_fallbacks(): void;
export declare function validate_promotion(csm: any, policy: any): void;
export declare function validate_transition(from_state: string, to_state: string): void;
