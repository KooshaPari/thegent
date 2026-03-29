// Auto-generated usage examples for work_stream
// Source: generate-api-docs.py

import { WorkStreamManager, claim, complete } from "./work_stream";

// Create a WorkStreamManager instance
const workstreammanager = new WorkStreamManager(undefined as unknown as ThegentSettings, undefined as unknown as any);
workstreammanager.claim("example_item_id", "example_agent_id");
workstreammanager.complete("example_item_id", "example_agent_id");

// Call claim
claim(undefined as unknown as any, "example_item_id", "example_agent_id");
// Call complete
complete(undefined as unknown as any, "example_item_id", "example_agent_id");
