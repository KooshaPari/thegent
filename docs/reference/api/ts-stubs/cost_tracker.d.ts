// Auto-generated TypeScript declarations for cost_tracker
// Source: generate-api-docs.py

export declare class CostEntry {
  to_json(): void;
}

export declare class CostTracker {
  constructor(log_path: any, daily_budget: any);
  clear(): void;
  daily_budget(): void;
  get_budget_burn_ratio(): void;
  get_budget_remaining(): void;
  get_daily_spend(): void;
  get_stats(): void;
  is_over_budget(): void;
  log_path(): void;
  track(provider: string, model: string, usage: Record<(str, int)>, cost: number, latency_ms: number, session_id: any, is_error: boolean, is_fallback: boolean): void;
}

export declare class RoutingStats {
}

export declare function clear(): void;
export declare function daily_budget(): void;
export declare function get_budget_burn_ratio(): void;
export declare function get_budget_remaining(): void;
export declare function get_cost_tracker(): void;
export declare function get_daily_spend(): void;
export declare function get_stats(): void;
export declare function is_over_budget(): void;
export declare function log_path(): void;
export declare function reset_cost_tracker(): void;
export declare function to_json(): void;
export declare function track(provider: string, model: string, usage: Record<(str, int)>, cost: number, latency_ms: number, session_id: any, is_error: boolean, is_fallback: boolean): void;
