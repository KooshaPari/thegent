// Auto-generated TypeScript declarations for budget_alerts
// Source: generate-api-docs.py

export declare class BudgetAlertSystem {
  constructor(cost_dir: any, config: any);
  check_budget(current_cost: number, context: string): void;
  from_settings(settings: any): void;
  get_daily_spend(): void;
  get_hourly_spend(): void;
}

export declare class BudgetConfig {
}

export declare function check_budget(current_cost: number, context: string): void;
export declare function from_settings(settings: any): void;
export declare function get_daily_spend(): void;
export declare function get_hourly_spend(): void;
