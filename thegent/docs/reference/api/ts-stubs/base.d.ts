// Auto-generated TypeScript declarations for base
// Source: generate-api-docs.py

export declare class SmolAgent {
  constructor(name: string, tools: Array<Tool>);
  add_tool(tool: Tool): void;
  children(): void;
  delegate(sub_task: any): void;
  execute_job(job: SmolGentJob): void;
  get_tool(name: string): void;
  memory(): void;
  parent(): void;
  recall(key: string): void;
  remember(key: string, value: any): void;
  run(task: any): void;
  set_parent(parent: SmolAgent): void;
  tools(): void;
}

export declare class SmolGentJob {
}

export declare class SmolGentResult {
}

export declare function add_tool(tool: Tool): void;
export declare function children(): void;
export declare function delegate(sub_task: any): void;
export declare function execute_job(job: SmolGentJob): void;
export declare function get_tool(name: string): void;
export declare function memory(): void;
export declare function parent(): void;
export declare function recall(key: string): void;
export declare function remember(key: string, value: any): void;
export declare function run(task: any): void;
export declare function set_parent(parent: SmolAgent): void;
export declare function tools(): void;
