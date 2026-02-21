// Auto-generated TypeScript declarations for git
// Source: generate-api-docs.py

export declare class GitParallelismManager {
  constructor(project_root: string, agent_id: string, mesh_root: string);
  create_commit_from_index(message: string, parent_ref: string): void;
  ensure_index(): void;
  get_agent_status(): void;
  stage_files(files: Array<string>): void;
  update_ref_cas(ref: string, new_hash: string, old_hash: string): void;
}

export declare function create_commit_from_index(message: string, parent_ref: string): void;
export declare function ensure_index(): void;
export declare function get_agent_status(): void;
export declare function stage_files(files: Array<string>): void;
export declare function update_ref_cas(ref: string, new_hash: string, old_hash: string): void;
