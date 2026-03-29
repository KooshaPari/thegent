// Auto-generated usage examples for unified_registry_cli
// Source: generate-api-docs.py

import { assign_project, discover, get_agent, list_agents, register_agent } from "./unified_registry_cli";

// Call assign_project
assign_project("example_agent_id", "example_project_id", "example_role");
// Call discover
discover("example_description", undefined as unknown as Array<AgentCapability>, undefined as unknown as any);
// Call get_agent
get_agent("example_agent_id");
// Call list_agents
list_agents(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
// Call register_agent
register_agent("example_agent_id", "example_name", undefined as unknown as Array<AgentCapability>);
