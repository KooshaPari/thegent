// Auto-generated TypeScript declarations for catalog
// Source: generate-api-docs.py

export declare class CatalogView {
}

export declare class ModelCatalog {
  routes_for(model_id: string, use_scraped: boolean): void;
  to_catalog_view(use_scraped: boolean): void;
  to_contract_view(use_scraped: boolean, provider_filter: any, use_cache: boolean): void;
}

export declare class ResolvedRoute {
}

export declare class Route {
}

export declare function filter_models_for_provider(provider: string, models: Array<string>): void;
export declare function get_cache(): void;
export declare function normalize_model_id(model_id: string): void;
export declare function normalize_route_policy(policy: any): void;
export declare function resolve_route(model_id: string, provider_hint: any, policy: RoutePolicy, quality_floor: number, lane: any): void;
export declare function resolve_route_contract(model_id: string, provider_hint: any, policy: RoutePolicy): void;
export declare function route_contract(): void;
export declare function routes_for(model_id: string, use_scraped: boolean): void;
export declare function to_catalog_view(use_scraped: boolean): void;
export declare function to_contract_view(use_scraped: boolean, provider_filter: any, use_cache: boolean): void;
