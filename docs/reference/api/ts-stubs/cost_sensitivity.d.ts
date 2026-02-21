// Auto-generated TypeScript declarations for cost_sensitivity
// Source: generate-api-docs.py

export declare class CostSensitivityExperiment {
  constructor();
  analyze(): void;
  record_baseline(cost: number): void;
  record_variant(cost: number): void;
}

export declare function analyze(): void;
export declare function record_baseline(cost: number): void;
export declare function record_variant(cost: number): void;
