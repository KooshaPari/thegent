// Auto-generated TypeScript declarations for cost_controller
// Source: generate-api-docs.py

export declare class BudgetTier extends StrEnum {
}

export declare class CostController {
  constructor(session_dir: string, health_targets_path: string);
  calls_remaining(): void;
  can_spawn(estimated_calls: number): void;
  get_tier(): void;
  get_today_usage(): void;
  record_call(dimension: string, agent: string): void;
  usage_path(): void;
}

export declare class DailyUsage extends BaseModel {
}

export declare function calls_remaining(): void;
export declare function can_spawn(estimated_calls: number): void;
export declare function get_tier(): void;
export declare function get_today_usage(): void;
export declare function record_call(dimension: string, agent: string): void;
export declare function usage_path(): string;
