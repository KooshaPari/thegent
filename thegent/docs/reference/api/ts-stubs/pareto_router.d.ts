// Auto-generated TypeScript declarations for pareto_router
// Source: generate-api-docs.py

export declare class Offer {
}

export declare class ParetoRouter {
  get_optimal_providers(candidates: Array<RouteCandidate>): void;
  select(candidates: Array<RouteCandidate>): void;
  select_by_strategy(strategy: string, candidates: Array<RouteCandidate>): void;
}

export declare class RoleConfig {
}

export declare class RouteCandidate {
}

export declare class RouteTrace {
}

export declare function get_optimal_providers(candidates: Array<RouteCandidate>): void;
export declare function key(o: Offer): [(float, number, float)];
export declare function select(candidates: Array<RouteCandidate>): void;
export declare function select_by_strategy(strategy: string, candidates: Array<RouteCandidate>): void;
export declare function select_offer(complexity_tier: string, min_quality: number, max_cost_weight: number, opt_order: [(str, Ellipsis)], role: any): void;
export declare function select_offer_with_fallbacks(complexity_tier: string, min_quality: number, max_cost_weight: number, k: number, role: any): void;
export declare function select_offer_with_trace(complexity_tier: string, min_quality: number, max_cost_weight: number, opt_order: [(str, Ellipsis)], role: any): void;
