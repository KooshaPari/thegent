// Auto-generated usage examples for donut_adapter
// Source: generate-api-docs.py

import { RoutingDonutAdapter, RoutingStats, clear_stats, get_donut_adapter, get_router, get_stats, get_team_router_config, harvest_on_stop, harvest_path, queue_path, read_model_preference_from_queue, record_request } from "./donut_adapter";

// Create a RoutingDonutAdapter instance
const routingdonutadapter = new RoutingDonutAdapter(undefined as unknown as any, undefined as unknown as any);
routingdonutadapter.clear_stats();
routingdonutadapter.get_router("example_policy");
routingdonutadapter.get_stats();
routingdonutadapter.get_team_router_config();
routingdonutadapter.harvest_on_stop();
routingdonutadapter.harvest_path();
routingdonutadapter.queue_path();
routingdonutadapter.read_model_preference_from_queue();
routingdonutadapter.record_request("example_model", "example_provider", "example_category", 0, 0, false, false);

// Create a RoutingStats instance
const routingstats = new RoutingStats();

// Call clear_stats
clear_stats(undefined as unknown as any);
// Call get_donut_adapter
get_donut_adapter();
// Call get_router
get_router(undefined as unknown as any, "example_policy");
// Call get_stats
get_stats(undefined as unknown as any);
// Call get_team_router_config
get_team_router_config(undefined as unknown as any);
// Call harvest_on_stop
harvest_on_stop(undefined as unknown as any);
// Call harvest_path
harvest_path(undefined as unknown as any);
// Call queue_path
queue_path(undefined as unknown as any);
// Call read_model_preference_from_queue
read_model_preference_from_queue(undefined as unknown as any);
// Call record_request
record_request(undefined as unknown as any, "example_model", "example_provider", "example_category", 0, 0, false, false);
