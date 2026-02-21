// Auto-generated TypeScript declarations for cost_aware_router
// Source: generate-api-docs.py

export declare class Budget {
  remaining(): void;
  utilization(): void;
}

export declare class BudgetAwareRouter {
  constructor(budget_manager: BudgetManager, pareto_router: any, warn_at_pct: number, degraded_at_pct: number);
  route(project_id: string, candidates: Array<RouteCandidate>, strategy: string): void;
}

export declare class BudgetExceededError extends Exception {
  constructor(budget_type: string, limit: number, current: number);
}

export declare class BudgetManager {
  constructor();
  add_budget(budget: Budget): void;
  check_budget(project_id: string, requested_cost: number): void;
  record_spend(project_id: string, cost: number): void;
}

export declare class BudgetStatus {
}

export declare class BudgetType extends Enum {
}

export declare class CostAwareRouter {
  constructor(budget: CostBudget, tracker: SimpleCostTracker);
  select(candidates: Array<_SimpleCandidate>): void;
}

export declare class CostBudget {
}

export declare class CostMeter {
  constructor();
  get_project_cost(project_id: string): void;
}

export declare class SimpleCostTracker {
  constructor();
  daily_total(): void;
  record(amount: number): void;
  reset_session(): void;
  session_total(): void;
}

export declare class _SimpleCandidate {
}

export declare function add_budget(budget: Budget): void;
export declare function check_budget(project_id: string, requested_cost: number): void;
export declare function daily_total(): number;
export declare function get_project_cost(project_id: string): void;
export declare function record(amount: number): void;
export declare function record_spend(project_id: string, cost: number): void;
export declare function remaining(): void;
export declare function reset_session(): void;
export declare function route(project_id: string, candidates: Array<RouteCandidate>, strategy: string): void;
export declare function select(candidates: Array<_SimpleCandidate>): void;
export declare function session_total(): number;
export declare function utilization(): void;
