// Auto-generated TypeScript declarations for workflow
// Source: generate-api-docs.py

export declare class CrewStage {
}

export declare class WorkflowEngine {
  constructor();
  add_stage(stage: CrewStage): void;
  execute(): void;
  execute_stage(stage: CrewStage): void;
  resolve_stage_dependencies(): void;
}

export declare function add_stage(stage: CrewStage): void;
export declare function execute(): void;
export declare function execute_stage(stage: CrewStage): void;
export declare function resolve_stage_dependencies(): void;
