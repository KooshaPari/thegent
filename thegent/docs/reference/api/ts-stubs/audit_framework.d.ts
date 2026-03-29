// Auto-generated TypeScript declarations for audit_framework
// Source: generate-api-docs.py

export declare class AuditIssue {
  to_dict(): void;
}

export declare class AuditRegistry {
  constructor();
  get_all_audits(): void;
  register(audit: AuditType): void;
}

export declare class AuditResult {
  add_issue(issue: AuditIssue): void;
  complete(): void;
  to_dict(): void;
}

export declare class AuditSeverity {
}

export declare class AuditType extends ABC {
  description(): void;
  name(): void;
}

export declare class ConfigAuditType extends AuditType {
  description(): void;
  name(): void;
}

export declare class DagAuditType extends AuditType {
  description(): void;
  name(): void;
}

export declare class DoctorAuditType extends AuditType {
  description(): void;
  name(): void;
}

export declare class InitiativeAuditType extends AuditType {
  description(): void;
  name(): void;
}

export declare class PlanAuditType extends AuditType {
  description(): void;
  name(): void;
}

export declare class SystemAuditFramework {
  constructor(registry: any);
}

export declare function add_issue(issue: AuditIssue): void;
export declare function complete(): void;
export declare function description(): string;
export declare function get_all_audits(): Array<AuditType>;
export declare function name(): string;
export declare function register(audit: AuditType): void;
export declare function to_dict(): Record<(str, Any)>;
