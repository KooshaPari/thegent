// Auto-generated TypeScript declarations for agent_workflow
// Source: generate-api-docs.py

export declare class AgentWorkflow {
  constructor();
  create_docgen_workflow(): void;
  execute(context: Record<(str, Any)>): void;
  register_step(name: string, func: callable, dependencies: any): void;
}

export declare function create_docgen_workflow(): void;
export declare function execute(context: Record<(str, Any)>): void;
export declare function register_step(name: string, func: callable, dependencies: any): void;
