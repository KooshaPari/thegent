// Auto-generated TypeScript declarations for compliance
// Source: generate-api-docs.py

export declare class ComplianceAuditTrail {
  constructor(storage_path: string);
  record_action(action: string, context: Record<(str, Any)>, profile: ComplianceProfile): void;
}

export declare class ComplianceControl {
}

export declare class ComplianceEnforcer {
  constructor(profile: ComplianceProfile);
  check_control(control_id: string, context: Record<(str, Any)>): void;
  enforce_mandatory(action: string, context: Record<(str, Any)>): void;
}

export declare class ComplianceExporter {
  constructor(session_dir: string);
  export_bundle(framework: string, target_path: string): void;
}

export declare class ComplianceProfile {
  get_mandatory_controls(): void;
}

export declare class ComplianceProfileType extends Enum {
}

export declare function check_control(control_id: string, context: Record<(str, Any)>): void;
export declare function enforce_mandatory(action: string, context: Record<(str, Any)>): void;
export declare function export_bundle(framework: string, target_path: string): void;
export declare function get_mandatory_controls(): void;
export declare function record_action(action: string, context: Record<(str, Any)>, profile: ComplianceProfile): void;
