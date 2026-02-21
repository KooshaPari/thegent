// Auto-generated TypeScript declarations for traceability
// Source: generate-api-docs.py

export declare class TraceabilityAuditor {
  constructor(root_dir: string);
  audit(expected_ids: Array<string>): void;
  generate_markdown_report(report: TraceabilityReport): void;
}

export declare class TraceabilityReport extends BaseModel {
}

export declare function audit(expected_ids: Array<string>): void;
export declare function generate_markdown_report(report: TraceabilityReport): void;
