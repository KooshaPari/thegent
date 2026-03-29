// Auto-generated usage examples for team_coordinator
// Source: generate-api-docs.py

import { TeamCoordinator, coordinate_team_task, coordinate_team_task_collaborative, coordinate_team_task_hierarchical, delegate_cross_team, delegate_within_team, get_team_coordination_status } from "./team_coordinator";

// Create a TeamCoordinator instance
const teamcoordinator = new TeamCoordinator(undefined as unknown as AgentHierarchyManager);
teamcoordinator.coordinate_team_task("example_team_id", "example_task", undefined as unknown as any);
teamcoordinator.coordinate_team_task_collaborative("example_team_id", "example_task", undefined as unknown as any, undefined as unknown as Array<AgentNode>);
teamcoordinator.coordinate_team_task_hierarchical("example_team_id", "example_task", undefined as unknown as any, undefined as unknown as Array<AgentNode>);
teamcoordinator.delegate_cross_team("example_from_agent_id", "example_to_agent_id", "example_task", undefined as unknown as any, undefined as unknown as any);
teamcoordinator.delegate_within_team("example_from_agent_id", "example_to_agent_id", "example_task", undefined as unknown as any);
teamcoordinator.get_team_coordination_status("example_team_id");

// Call coordinate_team_task
coordinate_team_task(undefined as unknown as any, "example_team_id", "example_task", undefined as unknown as any);
// Call coordinate_team_task_collaborative
coordinate_team_task_collaborative(undefined as unknown as any, "example_team_id", "example_task", undefined as unknown as any, undefined as unknown as Array<AgentNode>);
// Call coordinate_team_task_hierarchical
coordinate_team_task_hierarchical(undefined as unknown as any, "example_team_id", "example_task", undefined as unknown as any, undefined as unknown as Array<AgentNode>);
// Call delegate_cross_team
delegate_cross_team(undefined as unknown as any, "example_from_agent_id", "example_to_agent_id", "example_task", undefined as unknown as any, undefined as unknown as any);
// Call delegate_within_team
delegate_within_team(undefined as unknown as any, "example_from_agent_id", "example_to_agent_id", "example_task", undefined as unknown as any);
// Call get_team_coordination_status
get_team_coordination_status(undefined as unknown as any, "example_team_id");
