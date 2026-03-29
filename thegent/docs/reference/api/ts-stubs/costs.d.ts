// Auto-generated TypeScript declarations for costs
// Source: generate-api-docs.py

export declare class BudgetAlert {
  constructor(threshold: number);
  set_budget(budget: number): void;
  should_alert(current_cost: number): void;
}

export declare class CostCap {
  constructor(max_cost: number);
  check(cost: number): void;
}

export declare class CostSensing {
  constructor(slo_regulator: any);
  check_cost_cap(action_cost: number, cap: number): void;
  get_cost_feedback(model_id: string): void;
}

export declare class CostTracker {
  constructor();
  get_session_cost(session_id: string): void;
  is_within_budget(session_id: string, budget: number): void;
  record_cost(session_id: string, cost: number): void;
  start_session(session_id: string): void;
}

export declare function check(cost: number): void;
export declare function check_cost_cap(action_cost: number, cap: number): void;
export declare function get_cost_feedback(model_id: string): void;
export declare function get_session_cost(session_id: string): void;
export declare function is_within_budget(session_id: string, budget: number): void;
export declare function record_cost(session_id: string, cost: number): void;
export declare function set_budget(budget: number): void;
export declare function should_alert(current_cost: number): void;
export declare function start_session(session_id: string): void;
