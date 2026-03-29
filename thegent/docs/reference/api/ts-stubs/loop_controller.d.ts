// Auto-generated TypeScript declarations for loop_controller
// Source: generate-api-docs.py

export declare class LifecycleController {
  constructor(settings: ThegentSettings, worker_agent_name: string, checker_agent_name: string, mode: LoopMode, max_iterations: number, worker_model: any, task_id: any, verification_callback: any);
  run_loop(initial_prompt: string, todo_spec: string, on_worker_output: any, on_progress: any): void;
}

export declare class LoopMode extends StrEnum {
}

export declare class LoopState extends BaseModel {
}

export declare function run_loop(initial_prompt: string, todo_spec: string, on_worker_output: any, on_progress: any): void;
