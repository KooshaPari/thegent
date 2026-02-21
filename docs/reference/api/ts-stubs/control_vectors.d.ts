// Auto-generated TypeScript declarations for control_vectors
// Source: generate-api-docs.py

export declare class ControlVectorManager {
  constructor(agent_id: string);
  analyze_and_inject(prompt: string, agent_state: Record<(str, Any)>): void;
  prepare_environment(workspace_path: string): void;
}

export declare function analyze_and_inject(prompt: string, agent_state: Record<(str, Any)>): void;
export declare function prepare_environment(workspace_path: string): void;
