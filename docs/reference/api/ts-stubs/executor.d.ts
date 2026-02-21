// Auto-generated TypeScript declarations for executor
// Source: generate-api-docs.py

export declare class AgentAssigner {
  assign(tasks: Array<Task>, agents: Array<CrewAgent>): void;
}

export declare class CrewExecutor {
  constructor(crew: Crew, task_executor: any, agent_assigner: any);
  assign_tasks_to_agents(): void;
  execute(): void;
}

export declare class ExecutionResult {
}

export declare class HierarchicalAssigner extends AgentAssigner {
  assign(tasks: Array<Task>, agents: Array<CrewAgent>): void;
}

export declare class RoundRobinAssigner extends AgentAssigner {
  assign(tasks: Array<Task>, agents: Array<CrewAgent>): void;
}

export declare class SkillBasedAssigner extends AgentAssigner {
  assign(tasks: Array<Task>, agents: Array<CrewAgent>): void;
}

export declare class TaskExecutor {
  constructor(max_retries: number, timeout_seconds: number, agent_executor: any);
  execute_all(tasks: Array<Task>, task_assignments: Record<(str, str)>): void;
  execute_task(task: Task, agent_id: string, context: any): void;
  get_task_input(task: Task, completed_tasks: Record<(str, ExecutionResult)>): void;
  resolve_dependencies(tasks: Array<Task>): void;
}

export declare function assign(tasks: Array<Task>, agents: Array<CrewAgent>): void;
export declare function assign_tasks_to_agents(): void;
export declare function execute(): void;
export declare function execute_all(tasks: Array<Task>, task_assignments: Record<(str, str)>): void;
export declare function execute_task(task: Task, agent_id: string, context: any): void;
export declare function get_task_input(task: Task, completed_tasks: Record<(str, ExecutionResult)>): void;
export declare function resolve_dependencies(tasks: Array<Task>): void;
