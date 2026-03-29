// Auto-generated usage examples for offload
// Source: generate-api-docs.py

import { ComputeOffload, available_targets, offload, register_target } from "./offload";

// Create a ComputeOffload instance
const computeoffload = new ComputeOffload(undefined as unknown as any, undefined as unknown as any);
computeoffload.available_targets();
computeoffload.offload("example_target_id", "example_command", 0);
computeoffload.register_target("example_target_id", "example_host", 0);

// Call available_targets
available_targets(undefined as unknown as any);
// Call offload
offload(undefined as unknown as any, "example_target_id", "example_command", 0);
// Call register_target
register_target(undefined as unknown as any, "example_target_id", "example_host", 0);
