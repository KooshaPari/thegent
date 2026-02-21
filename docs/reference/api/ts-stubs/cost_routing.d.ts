// Auto-generated TypeScript declarations for cost_routing
// Source: generate-api-docs.py

export declare class CostRoutingResearch {
  constructor();
  compare_strategies(requests: Array<Record<(str, Any)>>): void;
  register_strategy(name: string, strategy: Record<(str, Any)>): void;
  simulate_routing(requests: Array<Record<(str, Any)>>, strategy: string): void;
}

export declare function compare_strategies(requests: Array<Record<(str, Any)>>): void;
export declare function register_strategy(name: string, strategy: Record<(str, Any)>): void;
export declare function simulate_routing(requests: Array<Record<(str, Any)>>, strategy: string): void;
