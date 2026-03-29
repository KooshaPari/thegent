// Auto-generated TypeScript declarations for compliance_reports
// Source: generate-api-docs.py

export declare class ComplianceReporter {
  constructor();
  export_report(compliance_data: Record<(str, Any)>, output_path: string, format: string): void;
  generate_report(compliance_data: Record<(str, Any)>, format: string): void;
}

export declare function export_report(compliance_data: Record<(str, Any)>, output_path: string, format: string): void;
export declare function generate_report(compliance_data: Record<(str, Any)>, format: string): void;
