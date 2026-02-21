// Auto-generated TypeScript declarations for donut_adapter
// Source: generate-api-docs.py

export declare class RoutingDonutAdapter {
  constructor(queue_path: any, harvest_path: any);
  clear_stats(): void;
  get_router(policy: string): void;
  get_stats(): void;
  get_team_router_config(): void;
  harvest_on_stop(): void;
  harvest_path(): void;
  queue_path(): void;
  read_model_preference_from_queue(): void;
  record_request(model: string, provider: string, category: string, tokens: number, cost_usd: number, is_fallback: boolean, is_error: boolean): void;
}

export declare class RoutingStats {
}

export declare function clear_stats(): void;
export declare function get_donut_adapter(): void;
export declare function get_router(policy: string): void;
export declare function get_stats(): void;
export declare function get_team_router_config(): void;
export declare function harvest_on_stop(): void;
export declare function harvest_path(): void;
export declare function queue_path(): void;
export declare function read_model_preference_from_queue(): void;
export declare function record_request(model: string, provider: string, category: string, tokens: number, cost_usd: number, is_fallback: boolean, is_error: boolean): void;
