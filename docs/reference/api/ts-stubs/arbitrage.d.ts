// Auto-generated TypeScript declarations for arbitrage
// Source: generate-api-docs.py

export declare class ArbitrageEngine {
  constructor(market: AgentMarket);
  estimate_global_savings(run_count: number): void;
  find_best_value(task_id: string, capabilities: Array<string>, max_budget: number): void;
}

export declare function estimate_global_savings(run_count: number): void;
export declare function find_best_value(task_id: string, capabilities: Array<string>, max_budget: number): void;
