// Auto-generated TypeScript declarations for agent_hierarchy
// Source: generate-api-docs.py

export declare class AgentHierarchyManager {
  constructor(storage_path: string);
  add_team_member(team_id: string, agent_run_id: string): void;
  can_delegate(from_agent_id: string, to_agent_id: string, task_context: any): void;
  check_team_consistency(): void;
  create_relationship(parent_id: string, child_id: string, relationship_type: RelationshipType, task_id: any, delegation_prompt: any, handoff_context: any): void;
  create_team(team_id: string, name: string, description: string, team_type: TeamType, coordination_mode: CoordinationMode, lead_id: string, boundaries: any, communication_channels: any): void;
  detect_circular_relationships(start_id: string): void;
  detect_orphaned_agents(): void;
  get_agent(run_id: string): void;
  get_ancestors(agent_id: string): void;
  get_children(parent_id: string): void;
  get_descendants(agent_id: string): void;
  get_hierarchy_tree(root_id: any): void;
  get_team(team_id: string): void;
  get_team_members(team_id: string): void;
  list_all_agents(): void;
  list_all_relationships(): void;
  list_all_teams(): void;
  register_agent(agent_id: string, run_id: string, role: AgentRole, parent_id: any, team_id: any, validate: boolean): void;
  remove_team_member(team_id: string, agent_run_id: string): void;
  update_agent_status(run_id: string, status: string): void;
  update_team_status(team_id: string, status: string): void;
  validate_agent_id(agent_id: string): void;
  validate_before_register(agent_id: string, run_id: string, parent_id: any, team_id: any): void;
}

export declare class AgentNode {
  from_dict(data: Record<(str, Any)>): void;
  to_dict(): void;
}

export declare class AgentRelationship {
  from_dict(data: Record<(str, Any)>): void;
  to_dict(): void;
}

export declare class AgentRole extends Enum {
}

export declare class AgentTeam {
  from_dict(data: Record<(str, Any)>): void;
  to_dict(): void;
}

export declare class CoordinationMode extends Enum {
}

export declare class RelationshipType extends Enum {
}

export declare class TeamType extends Enum {
}

export declare function add_team_member(team_id: string, agent_run_id: string): void;
export declare function build_tree(node: AgentNode): Record<(str, Any)>;
export declare function can_delegate(from_agent_id: string, to_agent_id: string, task_context: any): void;
export declare function check_team_consistency(): void;
export declare function collect_descendants(node: AgentNode): void;
export declare function create_relationship(parent_id: string, child_id: string, relationship_type: RelationshipType, task_id: any, delegation_prompt: any, handoff_context: any): void;
export declare function create_team(team_id: string, name: string, description: string, team_type: TeamType, coordination_mode: CoordinationMode, lead_id: string, boundaries: any, communication_channels: any): void;
export declare function detect_circular_relationships(start_id: string): void;
export declare function detect_orphaned_agents(): void;
export declare function dfs(node_id: string): boolean;
export declare function from_dict(data: Record<(str, Any)>): void;
export declare function get_agent(run_id: string): void;
export declare function get_ancestors(agent_id: string): void;
export declare function get_children(parent_id: string): void;
export declare function get_descendants(agent_id: string): void;
export declare function get_hierarchy_tree(root_id: any): void;
export declare function get_team(team_id: string): void;
export declare function get_team_members(team_id: string): void;
export declare function list_all_agents(): void;
export declare function list_all_relationships(): void;
export declare function list_all_teams(): void;
export declare function register_agent(agent_id: string, run_id: string, role: AgentRole, parent_id: any, team_id: any, validate: boolean): void;
export declare function remove_team_member(team_id: string, agent_run_id: string): void;
export declare function to_dict(): void;
export declare function update_agent_status(run_id: string, status: string): void;
export declare function update_team_status(team_id: string, status: string): void;
export declare function validate_agent_id(agent_id: string): void;
export declare function validate_before_register(agent_id: string, run_id: string, parent_id: any, team_id: any): void;
