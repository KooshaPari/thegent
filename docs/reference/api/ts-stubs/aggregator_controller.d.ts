// Auto-generated TypeScript declarations for aggregator_controller
// Source: generate-api-docs.py

export declare class BudgetTier extends Enum {
}

export declare class CostController {
  constructor(session_dir: string, health_targets_path: any);
  can_spawn(): void;
  get_tier(): void;
  get_today_usage(): void;
  record_call(dimension: string, agent: string): void;
}

export declare class UsageSnapshot {
  utilization_pct(): void;
}

export declare function can_spawn(): void;
export declare function get_tier(): void;
export declare function get_today_usage(): void;
export declare function record_call(dimension: string, agent: string): void;
export declare function utilization_pct(): number;
