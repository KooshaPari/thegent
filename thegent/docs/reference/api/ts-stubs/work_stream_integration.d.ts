// Auto-generated TypeScript declarations for work_stream_integration
// Source: generate-api-docs.py

export declare class WorkStreamIntegration {
  constructor(work_stream_path: any);
  incorporate_from_plans(plan_files: Array<string>): void;
  update_work_stream(items: Array<Record<(str, Any)>>): void;
}

export declare function incorporate_from_plans(plan_files: Array<string>): void;
export declare function update_work_stream(items: Array<Record<(str, Any)>>): void;
