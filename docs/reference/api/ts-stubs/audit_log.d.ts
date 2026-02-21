// Auto-generated TypeScript declarations for audit_log
// Source: generate-api-docs.py

export declare class ShadowAuditGit {
  constructor(audit_path: string);
  commit_transaction(episode_id: string, changed_files: Array<string>, message: string): void;
  get_diff(commit_hash: string): void;
  get_log(limit: number, episode_id: any): void;
  init_shadow_repo(): void;
  path(): void;
}

export declare function commit_transaction(episode_id: string, changed_files: Array<string>, message: string): void;
export declare function get_diff(commit_hash: string): void;
export declare function get_log(limit: number, episode_id: any): void;
export declare function init_shadow_repo(): void;
export declare function path(): string;
