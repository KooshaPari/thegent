// Auto-generated TypeScript declarations for unified_registry_cli
// Source: generate-api-docs.py

export declare function assign_project(agent_id: string, project_id: string, role: string): void;
export declare function discover(description: string, capabilities: Array<AgentCapability>, project: any): void;
export declare function get_agent(agent_id: string): void;
export declare function list_agents(status: any, project: any, capability: any): void;
export declare function register_agent(agent_id: string, name: string, capabilities: Array<AgentCapability>): void;
