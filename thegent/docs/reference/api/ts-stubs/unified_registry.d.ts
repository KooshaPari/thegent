// Auto-generated TypeScript declarations for unified_registry
// Source: generate-api-docs.py

export declare class Agent extends BaseModel {
}

export declare class AgentCapability extends StrEnum {
}

export declare class AgentRegistryService {
  constructor(storage_path: any);
  assign_to_project(agent_id: string, assignment: ProjectAssignment): void;
  delete_agent(agent_id: string): void;
  discover_best_agent(task_description: string, required_capabilities: Array<AgentCapability>, project_id: any): void;
  get_agent(agent_id: string): void;
  list_agents(status: any, project_id: any, capability: any): void;
  register_agent(agent: Agent): void;
  update_agent(agent_id: string, updates: Record<(str, Any)>): void;
  update_collaboration_rules(agent_id: string, rules: CollaborationRule): void;
  update_metrics(agent_id: string, metrics_update: Record<(str, Any)>): void;
}

export declare class AgentStatus extends StrEnum {
}

export declare class Availability extends BaseModel {
}

export declare class CollaborationRule extends BaseModel {
}

export declare class PerformanceMetrics extends BaseModel {
}

export declare class ProjectAssignment extends BaseModel {
}

export declare function assign_to_project(agent_id: string, assignment: ProjectAssignment): void;
export declare function delete_agent(agent_id: string): void;
export declare function discover_best_agent(task_description: string, required_capabilities: Array<AgentCapability>, project_id: any): void;
export declare function get_agent(agent_id: string): void;
export declare function list_agents(status: any, project_id: any, capability: any): void;
export declare function register_agent(agent: Agent): void;
export declare function update_agent(agent_id: string, updates: Record<(str, Any)>): void;
export declare function update_collaboration_rules(agent_id: string, rules: CollaborationRule): void;
export declare function update_metrics(agent_id: string, metrics_update: Record<(str, Any)>): void;
