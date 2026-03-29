// Auto-generated TypeScript declarations for plan_system
// Source: generate-api-docs.py

export declare class PlanSystemIntegration {
  constructor(plan_file: any, plan_status_file: any);
  get_blocked_tasks(): void;
  get_tasks_for_phase(phase: string): void;
  update_task_status(task_id: string, status: string): void;
}

export declare function get_blocked_tasks(): void;
export declare function get_tasks_for_phase(phase: string): void;
export declare function update_task_status(task_id: string, status: string): void;
