// Auto-generated TypeScript declarations for pareto_routing
// Source: generate-api-docs.py

export declare class ParetoRouting {
  constructor();
  apply_hysteresis(current_route: string, new_route: string, cost_diff: number): void;
  find_pareto_optimal(options: Array<Record<(str, Any)>>): void;
}

export declare function apply_hysteresis(current_route: string, new_route: string, cost_diff: number): void;
export declare function find_pareto_optimal(options: Array<Record<(str, Any)>>): void;
