// Auto-generated TypeScript declarations for cost_aggregation
// Source: generate-api-docs.py

export declare class CostAggregator {
  constructor();
  get_cost_by_model(): void;
  get_total_cost(): void;
  record_run_cost(run_id: string, cost: number, model: string, tokens: Record<(str, int)>): void;
}

export declare function get_cost_by_model(): void;
export declare function get_total_cost(): void;
export declare function record_run_cost(run_id: string, cost: number, model: string, tokens: Record<(str, int)>): void;
