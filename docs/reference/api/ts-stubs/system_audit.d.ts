// Auto-generated TypeScript declarations for system_audit
// Source: generate-api-docs.py

export declare class AuditReport {
  add_results(results: Array<AuditResult>): void;
  has_drift(): void;
  to_dict(): void;
}

export declare class AuditResult {
  is_ok(): void;
  to_dict(): void;
}

export declare class AuditStatus extends str, Enum {
}

export declare class SystemAuditor {
  constructor(project_root: any);
  audit_agents(): void;
  audit_config(): void;
  audit_dependencies(): void;
  audit_hooks(): void;
  export_json(report: AuditReport, path: string): void;
  format_report(report: AuditReport): void;
  run_full_audit(): void;
}

export declare function add_results(results: Array<AuditResult>): void;
export declare function audit_agents(): void;
export declare function audit_config(): void;
export declare function audit_dependencies(): void;
export declare function audit_hooks(): void;
export declare function export_json(report: AuditReport, path: string): void;
export declare function format_report(report: AuditReport): void;
export declare function has_drift(): void;
export declare function is_ok(): void;
export declare function run_full_audit(): void;
export declare function to_dict(): void;
