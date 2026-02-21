// Auto-generated TypeScript declarations for crew
// Source: generate-api-docs.py

export declare class Crew {
  add_agent(agent: any): void;
  add_task(task: any): void;
  get_agent_by_id(agent_id: string): void;
  get_task_by_id(task_id: string): void;
}

export declare class ExecutionMode extends StrEnum {
}

export declare function add_agent(agent: any): void;
export declare function add_task(task: any): void;
export declare function get_agent_by_id(agent_id: string): void;
export declare function get_task_by_id(task_id: string): void;
