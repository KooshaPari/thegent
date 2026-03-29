// Auto-generated usage examples for pareto_router
// Source: generate-api-docs.py

import { Offer, ParetoRouter, RoleConfig, RouteCandidate, RouteTrace, get_optimal_providers, key, select, select_by_strategy, select_offer, select_offer_with_fallbacks, select_offer_with_trace } from "./pareto_router";

// Create a Offer instance
const offer = new Offer();

// Create a ParetoRouter instance
const paretorouter = new ParetoRouter();
paretorouter.get_optimal_providers(undefined as unknown as Array<RouteCandidate>);
paretorouter.select(undefined as unknown as Array<RouteCandidate>);
paretorouter.select_by_strategy("example_strategy", undefined as unknown as Array<RouteCandidate>);

// Create a RoleConfig instance
const roleconfig = new RoleConfig();

// Create a RouteCandidate instance
const routecandidate = new RouteCandidate();

// Create a RouteTrace instance
const routetrace = new RouteTrace();

// Call get_optimal_providers
get_optimal_providers(undefined as unknown as any, undefined as unknown as Array<RouteCandidate>);
// Call key
key(undefined as unknown as Offer);
// Call select
select(undefined as unknown as any, undefined as unknown as Array<RouteCandidate>);
// Call select_by_strategy
select_by_strategy(undefined as unknown as any, "example_strategy", undefined as unknown as Array<RouteCandidate>);
// Call select_offer
select_offer("example_complexity_tier", 0, 0, undefined as unknown as [(str, Ellipsis)], undefined as unknown as any);
// Call select_offer_with_fallbacks
select_offer_with_fallbacks("example_complexity_tier", 0, 0, 0, undefined as unknown as any);
// Call select_offer_with_trace
select_offer_with_trace("example_complexity_tier", 0, 0, undefined as unknown as [(str, Ellipsis)], undefined as unknown as any);
