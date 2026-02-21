// Auto-generated TypeScript declarations for litellm_router
// Source: generate-api-docs.py

export declare class EnhancedRouter {
  constructor(policy: any);
  alert_manager(): void;
  cost_tracker(): void;
  donut_adapter(): void;
  route(prompt: string, model: any, stream: boolean): void;
  route_stream(prompt: string, model: any): void;
}

export declare class RouterConfig {
}

export declare class RoutingResult {
}

export declare function alert_manager(): void;
export declare function build_fallback_chains(): void;
export declare function build_litellm_model_list(): void;
export declare function cost_tracker(): void;
export declare function donut_adapter(): void;
export declare function get_all_models_with_metadata(): Array<string>;
export declare function get_context_window(model: string): void;
export declare function get_enhanced_router(policy: any): void;
export declare function get_litellm_router(policy: string): void;
export declare function get_model_metadata(model_id: string): any;
export declare function get_pareto_preferred_model(complexity_tier: string): void;
export declare function get_router_config(): void;
export declare function has_model_metadata(model_id: string): boolean;
export declare function reset_enhanced_router(): void;
export declare function route(prompt: string, model: any, stream: boolean): void;
export declare function route_stream(prompt: string, model: any): void;
export declare function validate_context_window(model: string, prompt_tokens: number): void;
