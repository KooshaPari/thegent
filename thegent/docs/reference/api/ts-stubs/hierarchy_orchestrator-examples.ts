// Auto-generated usage examples for hierarchy_orchestrator
// Source: generate-api-docs.py

import { HierarchyOrchestrator, SubAgentConfig, decompose, execute, get_agent, get_context, list_agents, register_agent, set_context } from "./hierarchy_orchestrator";

// Create a HierarchyOrchestrator instance
const hierarchyorchestrator = new HierarchyOrchestrator(undefined as unknown as any, undefined as unknown as any);
hierarchyorchestrator.decompose("example_goal", 0);
hierarchyorchestrator.execute(undefined as unknown as Plan, undefined as unknown as any);
hierarchyorchestrator.get_agent("example_name");
hierarchyorchestrator.get_context();
hierarchyorchestrator.list_agents();
hierarchyorchestrator.register_agent(undefined as unknown as SubAgentConfig);
hierarchyorchestrator.set_context("example_key", undefined as unknown as any);

// Create a SubAgentConfig instance
const subagentconfig = new SubAgentConfig();

// Call decompose
decompose(undefined as unknown as any, "example_goal", 0);
// Call execute
execute(undefined as unknown as any, undefined as unknown as Plan, undefined as unknown as any);
// Call get_agent
get_agent(undefined as unknown as any, "example_name");
// Call get_context
get_context(undefined as unknown as any);
// Call list_agents
list_agents(undefined as unknown as any);
// Call register_agent
register_agent(undefined as unknown as any, undefined as unknown as SubAgentConfig);
// Call set_context
set_context(undefined as unknown as any, "example_key", undefined as unknown as any);
