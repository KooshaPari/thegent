// Auto-generated TypeScript declarations for hierarchy_orchestrator
// Source: generate-api-docs.py

export declare class HierarchyOrchestrator {
  constructor(planner: any, executor: any);
  decompose(goal: string, max_depth: number): void;
  execute(plan: Plan, runner: any): void;
  get_agent(name: string): void;
  get_context(): void;
  list_agents(): void;
  register_agent(config: SubAgentConfig): void;
  set_context(key: string, value: any): void;
}

export declare class SubAgentConfig {
}

export declare function decompose(goal: string, max_depth: number): void;
export declare function execute(plan: Plan, runner: any): void;
export declare function get_agent(name: string): void;
export declare function get_context(): void;
export declare function list_agents(): void;
export declare function register_agent(config: SubAgentConfig): void;
export declare function set_context(key: string, value: any): void;
