// Auto-generated TypeScript declarations for speculative_strategies
// Source: generate-api-docs.py

export declare class SpeculativeConfig {
}

export declare class SpeculativeStrategy extends Enum {
}

export declare function compute_adaptive_timeout(historical_p95_ms: number, base_timeout_ms: number, safety_multiplier: number): void;
export declare function select_speculative_providers(available_providers: Array<string>, strategy: SpeculativeStrategy, cost_budget: number): void;
export declare function should_terminate_early(elapsed_ms: number, timeout_ms: number, other_results: Array<any>, strategy: SpeculativeStrategy): void;
