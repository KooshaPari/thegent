// Auto-generated TypeScript declarations for prompts
// Source: generate-api-docs.py

export declare class PromptOrchestrator {
  constructor(settings: ThegentSettings);
  decompose(goal: string): void;
  route_subtasks(sub_tasks: Array<Record<(str, Any)>>): void;
}

export declare function decompose(goal: string): void;
export declare function route_subtasks(sub_tasks: Array<Record<(str, Any)>>): void;
