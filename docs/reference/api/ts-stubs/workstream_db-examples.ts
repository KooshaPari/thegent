// Auto-generated usage examples for workstream_db
// Source: generate-api-docs.py

import { WorkstreamDB, execute_query, generate_work_stream_md, get_active_items, get_dependency_graph, get_next_items, get_ready_items, get_recent_costs, get_running_count, get_running_count_by_lane, get_running_sessions, get_session, get_statistics, get_top_agents, mark_session_complete, record_constitutional_violation, record_cost, record_launch, record_resource_usage, record_session, sync_from_agileplus, sync_from_queues, sync_with_markdown, sync_workstream, upsert_canonical_item } from "./workstream_db";

// Create a WorkstreamDB instance
const workstreamdb = new WorkstreamDB(undefined as unknown as any, undefined as unknown as any);
workstreamdb.execute_query("example_query", undefined as unknown as [(Any, Ellipsis)]);
workstreamdb.generate_work_stream_md("example_output_path");
workstreamdb.get_active_items();
workstreamdb.get_dependency_graph();
workstreamdb.get_next_items(0, undefined as unknown as any);
workstreamdb.get_ready_items(0, 0);
workstreamdb.get_recent_costs(0);
workstreamdb.get_running_count();
workstreamdb.get_running_count_by_lane();
workstreamdb.get_running_sessions();
workstreamdb.get_session("example_session_id");
workstreamdb.get_statistics();
workstreamdb.get_top_agents(0);
workstreamdb.mark_session_complete("example_session_id", 0);
workstreamdb.record_constitutional_violation("example_item_id", undefined as unknown as any, undefined as unknown as any);
workstreamdb.record_cost("example_session_id", 0, 0, undefined as unknown as any);
workstreamdb.record_launch("example_item_id", "example_session_id", "example_lane", "example_model", 0, "example_trigger_type", undefined as unknown as any);
workstreamdb.record_resource_usage("example_session_id", undefined as unknown as Record<(str, Any)>);
workstreamdb.record_session("example_session_id", "example_agent", "example_prompt", "example_status", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
workstreamdb.sync_from_agileplus("example_session_dir");
workstreamdb.sync_from_queues("example_session_dir");
workstreamdb.sync_with_markdown("example_work_stream_path");
workstreamdb.sync_workstream(undefined as unknown as Record<(str, Any)>);
workstreamdb.upsert_canonical_item("example_item_id", "example_title", "example_source", "example_source_system", "example_priority", "example_status", undefined as unknown as any, undefined as unknown as any);

// Call execute_query
execute_query(undefined as unknown as any, "example_query", undefined as unknown as [(Any, Ellipsis)]);
// Call generate_work_stream_md
generate_work_stream_md(undefined as unknown as any, "example_output_path");
// Call get_active_items
get_active_items(undefined as unknown as any);
// Call get_dependency_graph
get_dependency_graph(undefined as unknown as any);
// Call get_next_items
get_next_items(undefined as unknown as any, 0, undefined as unknown as any);
// Call get_ready_items
get_ready_items(undefined as unknown as any, 0, 0);
// Call get_recent_costs
get_recent_costs(undefined as unknown as any, 0);
// Call get_running_count
get_running_count(undefined as unknown as any);
// Call get_running_count_by_lane
get_running_count_by_lane(undefined as unknown as any);
// Call get_running_sessions
get_running_sessions(undefined as unknown as any);
// Call get_session
get_session(undefined as unknown as any, "example_session_id");
// Call get_statistics
get_statistics(undefined as unknown as any);
// Call get_top_agents
get_top_agents(undefined as unknown as any, 0);
// Call mark_session_complete
mark_session_complete(undefined as unknown as any, "example_session_id", 0);
// Call record_constitutional_violation
record_constitutional_violation(undefined as unknown as any, "example_item_id", undefined as unknown as any, undefined as unknown as any);
// Call record_cost
record_cost(undefined as unknown as any, "example_session_id", 0, 0, undefined as unknown as any);
// Call record_launch
record_launch(undefined as unknown as any, "example_item_id", "example_session_id", "example_lane", "example_model", 0, "example_trigger_type", undefined as unknown as any);
// Call record_resource_usage
record_resource_usage(undefined as unknown as any, "example_session_id", undefined as unknown as Record<(str, Any)>);
// Call record_session
record_session(undefined as unknown as any, "example_session_id", "example_agent", "example_prompt", "example_status", undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call sync_from_agileplus
sync_from_agileplus(undefined as unknown as any, "example_session_dir");
// Call sync_from_queues
sync_from_queues(undefined as unknown as any, "example_session_dir");
// Call sync_with_markdown
sync_with_markdown(undefined as unknown as any, "example_work_stream_path");
// Call sync_workstream
sync_workstream(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call upsert_canonical_item
upsert_canonical_item(undefined as unknown as any, "example_item_id", "example_title", "example_source", "example_source_system", "example_priority", "example_status", undefined as unknown as any, undefined as unknown as any);
