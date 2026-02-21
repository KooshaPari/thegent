// Auto-generated usage examples for heliosShield_bridge
// Source: generate-api-docs.py

import { SmartMerge, broadcast_intent, create_shared_task, get_session_state, heliosShieldBridge, is_available, manager, merge_files } from "./heliosShield_bridge";

// Create a SmartMerge instance
const smartmerge = new SmartMerge();
smartmerge.merge_files("example_base", "example_ours", "example_theirs", "example_output");

// Create a heliosShieldBridge instance
const heliosshieldbridge = new heliosShieldBridge(undefined as unknown as any);
heliosshieldbridge.broadcast_intent("example_agent_id", "example_intent_type", "example_target");
heliosshieldbridge.create_shared_task("example_task_id", "example_description", undefined as unknown as any);
heliosshieldbridge.get_session_state("example_session_id");
heliosshieldbridge.is_available();
heliosshieldbridge.manager();

// Call broadcast_intent
broadcast_intent(undefined as unknown as any, "example_agent_id", "example_intent_type", "example_target");
// Call create_shared_task
create_shared_task(undefined as unknown as any, "example_task_id", "example_description", undefined as unknown as any);
// Call get_session_state
get_session_state(undefined as unknown as any, "example_session_id");
// Call is_available
is_available(undefined as unknown as any);
// Call manager
manager(undefined as unknown as any);
// Call merge_files
merge_files(undefined as unknown as any, "example_base", "example_ours", "example_theirs", "example_output");
