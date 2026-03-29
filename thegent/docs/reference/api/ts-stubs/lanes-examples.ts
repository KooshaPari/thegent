// Auto-generated usage examples for lanes
// Source: generate-api-docs.py

import { Lane, LaneModel, check_capacity, get_priority, get_urgency, is_protected, sort_tasks } from "./lanes";

// Create a Lane instance
const lane = new Lane();

// Create a LaneModel instance
const lanemodel = new LaneModel();
lanemodel.check_capacity("example_lane", 0, 0);
lanemodel.get_priority("example_lane");
lanemodel.get_urgency("example_lane");
lanemodel.is_protected("example_lane");
lanemodel.sort_tasks(undefined as unknown as Array<Record<(str, Any)>>);

// Call check_capacity
check_capacity(undefined as unknown as any, "example_lane", 0, 0);
// Call get_priority
get_priority(undefined as unknown as any, "example_lane");
// Call get_urgency
get_urgency(undefined as unknown as any, "example_lane");
// Call is_protected
is_protected(undefined as unknown as any, "example_lane");
// Call sort_tasks
sort_tasks(undefined as unknown as any, undefined as unknown as Array<Record<(str, Any)>>);
