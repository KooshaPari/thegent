// Auto-generated TypeScript declarations for slo_regulator
// Source: generate-api-docs.py

export declare class SLORegulator {
  constructor(target_latency_ms: number);
  evaluate_and_adjust(current_latency_ms: number): void;
}

export declare function evaluate_and_adjust(current_latency_ms: number): void;
