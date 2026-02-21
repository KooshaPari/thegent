// Auto-generated TypeScript declarations for plangent_subagents
// Source: generate-api-docs.py

export declare class PlangentSubagents {
  constructor();
  execute(subagent_name: string, task: Record<(str, Any)>): void;
  register_subagent(name: string, agent: any): void;
}

export declare function execute(subagent_name: string, task: Record<(str, Any)>): void;
export declare function register_subagent(name: string, agent: any): void;
