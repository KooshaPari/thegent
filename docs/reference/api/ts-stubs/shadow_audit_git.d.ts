// Auto-generated TypeScript declarations for shadow_audit_git
// Source: generate-api-docs.py

export declare class AuditEntry extends BaseModel {
  to_dict(): void;
}

export declare class ShadowAuditGit {
  constructor(db_path: any);
  export_audit(project_id: string, path: any): void;
  get_audit_log(project_id: string, limit: any): void;
  record_commit(project_id: string, sha: string, message: string, diff: string): void;
}

export declare function export_audit(project_id: string, path: any): void;
export declare function get_audit_log(project_id: string, limit: any): void;
export declare function record_commit(project_id: string, sha: string, message: string, diff: string): void;
export declare function to_dict(): void;
