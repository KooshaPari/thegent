// Auto-generated TypeScript declarations for task_router
// Source: generate-api-docs.py

export declare class ConstraintValidator {
  constructor(config: ThegentSettings);
  validate(task_metadata: TaskMetadata, registry: RunRegistry | None, model: any): void;
}

export declare class TaskClassifier {
  constructor(config: ThegentSettings);
  classify(prompt: string, agent_role: any): void;
  detect_role(prompt: string, agent_role: any): void;
}

export declare class TaskRouter {
  constructor(config: ThegentSettings);
  classify(prompt: string): void;
  find_active_terminal_for_path(path: string): void;
  get_fallback_chain(category: TaskCategory): void;
  route(prompt: string, registry: RunRegistry | None, model: any): void;
  route_by_capability(task_type: string): void;
  route_dag_tasks(dag: any): void;
  shape_task(prompt: string, category: TaskCategory): void;
  should_delegate_to_reviewer(confidence: number): void;
  validate(task_metadata: TaskMetadata, registry: RunRegistry | None, model: any): void;
}

export declare function classify(prompt: string): void;
export declare function detect_role(prompt: string, agent_role: any): void;
export declare function find_active_terminal_for_path(path: string): void;
export declare function get_fallback_chain(category: TaskCategory): void;
export declare function route(prompt: string, registry: RunRegistry | None, model: any): void;
export declare function route_by_capability(task_type: string): void;
export declare function route_dag_tasks(dag: any): void;
export declare function shape_task(prompt: string, category: TaskCategory): void;
export declare function should_delegate_to_reviewer(confidence: number): void;
export declare function validate(task_metadata: TaskMetadata, registry: RunRegistry | None, model: any): void;
