// Auto-generated TypeScript declarations for team_coordinator
// Source: generate-api-docs.py

export declare class TeamCoordinator {
  constructor(hierarchy_manager: AgentHierarchyManager);
  coordinate_team_task(team_id: string, task: string, context: any): void;
  coordinate_team_task_collaborative(team_id: string, task: string, context: any, active_members: Array<AgentNode>): void;
  coordinate_team_task_hierarchical(team_id: string, task: string, context: any, active_members: Array<AgentNode>): void;
  delegate_cross_team(from_agent_id: string, to_agent_id: string, task: string, context: any, mediator_id: any): void;
  delegate_within_team(from_agent_id: string, to_agent_id: string, task: string, context: any): void;
  get_team_coordination_status(team_id: string): void;
}

export declare function coordinate_team_task(team_id: string, task: string, context: any): void;
export declare function coordinate_team_task_collaborative(team_id: string, task: string, context: any, active_members: Array<AgentNode>): void;
export declare function coordinate_team_task_hierarchical(team_id: string, task: string, context: any, active_members: Array<AgentNode>): void;
export declare function delegate_cross_team(from_agent_id: string, to_agent_id: string, task: string, context: any, mediator_id: any): void;
export declare function delegate_within_team(from_agent_id: string, to_agent_id: string, task: string, context: any): void;
export declare function get_team_coordination_status(team_id: string): void;
