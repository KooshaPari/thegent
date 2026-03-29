// Auto-generated usage examples for litellm_router
// Source: generate-api-docs.py

import { EnhancedRouter, RouterConfig, RoutingResult, alert_manager, build_fallback_chains, build_litellm_model_list, cost_tracker, donut_adapter, get_all_models_with_metadata, get_context_window, get_enhanced_router, get_litellm_router, get_model_metadata, get_pareto_preferred_model, get_router_config, has_model_metadata, reset_enhanced_router, route, route_stream, validate_context_window } from "./litellm_router";

// Create a EnhancedRouter instance
const enhancedrouter = new EnhancedRouter(undefined as unknown as any);
enhancedrouter.alert_manager();
enhancedrouter.cost_tracker();
enhancedrouter.donut_adapter();
enhancedrouter.route("example_prompt", undefined as unknown as any, false);
enhancedrouter.route_stream("example_prompt", undefined as unknown as any);

// Create a RouterConfig instance
const routerconfig = new RouterConfig();

// Create a RoutingResult instance
const routingresult = new RoutingResult();

// Call alert_manager
alert_manager(undefined as unknown as any);
// Call build_fallback_chains
build_fallback_chains();
// Call build_litellm_model_list
build_litellm_model_list();
// Call cost_tracker
cost_tracker(undefined as unknown as any);
// Call donut_adapter
donut_adapter(undefined as unknown as any);
// Call get_all_models_with_metadata
get_all_models_with_metadata();
// Call get_context_window
get_context_window("example_model");
// Call get_enhanced_router
get_enhanced_router(undefined as unknown as any);
// Call get_litellm_router
get_litellm_router("example_policy");
// Call get_model_metadata
get_model_metadata("example_model_id");
// Call get_pareto_preferred_model
get_pareto_preferred_model("example_complexity_tier");
// Call get_router_config
get_router_config();
// Call has_model_metadata
has_model_metadata("example_model_id");
// Call reset_enhanced_router
reset_enhanced_router();
// Call route
route(undefined as unknown as any, "example_prompt", undefined as unknown as any, false);
// Call route_stream
route_stream(undefined as unknown as any, "example_prompt", undefined as unknown as any);
// Call validate_context_window
validate_context_window("example_model", 0);
