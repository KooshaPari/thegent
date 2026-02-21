// Auto-generated TypeScript declarations for agent_deployer
// Source: generate-api-docs.py

export declare class AgentDeployer {
  constructor(cost_controller: CostControllerProtocol, verification_gate: any, max_concurrent: number, lifecycle_mode: string, checker_agent_name: string);
  deploy(plan: any, pre_scan: any, cycle_id: string): void;
  get_ready_batch(plan: any, completed_task_ids: set<string>): void;
}

export declare class CostControllerProtocol extends Protocol {
  can_spawn(estimated_calls: number): void;
  get_tier(): void;
  record_call(dimension: string, agent_type: string): void;
}

export declare class DeploymentResult extends BaseModel {
}

export declare class TaskExecutionResult extends BaseModel {
}

export declare class VerificationGateProtocol extends Protocol {
  should_reroll(attempts: number): void;
  verify_task(task: any, execution: any, pre_scan: any): void;
}

export declare function can_spawn(estimated_calls: number): boolean;
export declare function deploy(plan: any, pre_scan: any, cycle_id: string): void;
export declare function get_ready_batch(plan: any, completed_task_ids: set<string>): void;
export declare function get_tier(): string;
export declare function record_call(dimension: string, agent_type: string): void;
export declare function should_reroll(attempts: number): boolean;
export declare function verify_task(task: any, execution: any, pre_scan: any): any;
