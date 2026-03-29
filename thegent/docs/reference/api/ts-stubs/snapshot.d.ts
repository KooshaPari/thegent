// Auto-generated TypeScript declarations for snapshot
// Source: generate-api-docs.py

export declare class ForensicSnapshotter {
  constructor(session_dir: string);
  capture_post_run(run_id: string, project_root: string, exit_code: number): void;
  capture_pre_run(run_id: string, project_root: string): void;
}

export declare function capture_post_run(run_id: string, project_root: string, exit_code: number): void;
export declare function capture_pre_run(run_id: string, project_root: string): void;
