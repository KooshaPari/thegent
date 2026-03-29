// Auto-generated usage examples for plangent
// Source: generate-api-docs.py

import { Plan, PlanNode, PlangentExecutor, PlangentPlanner, decompose, done_ids, execute, failed_ids, get_node, is_complete, is_ready, mark_done, mark_failed, next_ready_tasks, to_dict, to_work_stream_rows } from "./plangent";

// Create a Plan instance
const plan = new Plan();
plan.done_ids();
plan.failed_ids();
plan.get_node("example_node_id");
plan.to_dict();

// Create a PlanNode instance
const plannode = new PlanNode();
plannode.is_ready(undefined as unknown as set<string>);
plannode.to_dict();

// Create a PlangentExecutor instance
const plangentexecutor = new PlangentExecutor(undefined as unknown as any);
plangentexecutor.execute(undefined as unknown as Plan, undefined as unknown as RunnerType);

// Create a PlangentPlanner instance
const plangentplanner = new PlangentPlanner();
plangentplanner.decompose("example_goal", 0);
plangentplanner.is_complete(undefined as unknown as Plan);
plangentplanner.mark_done(undefined as unknown as Plan, "example_node_id", "example_result");
plangentplanner.mark_failed(undefined as unknown as Plan, "example_node_id", "example_error");
plangentplanner.next_ready_tasks(undefined as unknown as Plan);
plangentplanner.to_work_stream_rows(undefined as unknown as Plan);

// Call decompose
decompose(undefined as unknown as any, "example_goal", 0);
// Call done_ids
done_ids(undefined as unknown as any);
// Call execute
execute(undefined as unknown as any, undefined as unknown as Plan, undefined as unknown as RunnerType);
// Call failed_ids
failed_ids(undefined as unknown as any);
// Call get_node
get_node(undefined as unknown as any, "example_node_id");
// Call is_complete
is_complete(undefined as unknown as any, undefined as unknown as Plan);
// Call is_ready
is_ready(undefined as unknown as any, undefined as unknown as set<string>);
// Call mark_done
mark_done(undefined as unknown as any, undefined as unknown as Plan, "example_node_id", "example_result");
// Call mark_failed
mark_failed(undefined as unknown as any, undefined as unknown as Plan, "example_node_id", "example_error");
// Call next_ready_tasks
next_ready_tasks(undefined as unknown as any, undefined as unknown as Plan);
// Call to_dict
to_dict(undefined as unknown as any);
// Call to_work_stream_rows
to_work_stream_rows(undefined as unknown as any, undefined as unknown as Plan);
