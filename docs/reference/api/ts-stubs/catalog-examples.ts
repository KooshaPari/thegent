// Auto-generated usage examples for catalog
// Source: generate-api-docs.py

import { CatalogView, ModelCatalog, ResolvedRoute, Route, filter_models_for_provider, get_cache, normalize_model_id, normalize_route_policy, resolve_route, resolve_route_contract, route_contract, routes_for, to_catalog_view, to_contract_view } from "./catalog";

// Create a CatalogView instance
const catalogview = new CatalogView();

// Create a ModelCatalog instance
const modelcatalog = new ModelCatalog();
modelcatalog.routes_for("example_model_id", false);
modelcatalog.to_catalog_view(false);
modelcatalog.to_contract_view(false, undefined as unknown as any, false);

// Create a ResolvedRoute instance
const resolvedroute = new ResolvedRoute();

// Create a Route instance
const route = new Route();

// Call filter_models_for_provider
filter_models_for_provider("example_provider", undefined as unknown as Array<string>);
// Call get_cache
get_cache();
// Call normalize_model_id
normalize_model_id("example_model_id");
// Call normalize_route_policy
normalize_route_policy(undefined as unknown as any);
// Call resolve_route
resolve_route("example_model_id", undefined as unknown as any, undefined as unknown as RoutePolicy, 0, undefined as unknown as any);
// Call resolve_route_contract
resolve_route_contract("example_model_id", undefined as unknown as any, undefined as unknown as RoutePolicy);
// Call route_contract
route_contract();
// Call routes_for
routes_for("example_model_id", false);
// Call to_catalog_view
to_catalog_view(false);
// Call to_contract_view
to_contract_view(false, undefined as unknown as any, false);
