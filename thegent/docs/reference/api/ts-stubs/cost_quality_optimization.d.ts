// Auto-generated TypeScript declarations for cost_quality_optimization
// Source: generate-api-docs.py

export declare class CostQualityOptimizer {
  constructor();
  get_routing_stats(): void;
  register_model(model_id: string, cost_per_token: number, quality_score: number): void;
  route_request(task_complexity: number, quality_threshold: number, max_cost: any): void;
}

export declare function get_routing_stats(): void;
export declare function register_model(model_id: string, cost_per_token: number, quality_score: number): void;
export declare function route_request(task_complexity: number, quality_threshold: number, max_cost: any): void;
