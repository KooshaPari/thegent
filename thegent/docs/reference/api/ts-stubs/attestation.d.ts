// Auto-generated TypeScript declarations for attestation
// Source: generate-api-docs.py

export declare class AttestationGenerator {
  constructor(settings: ThegentSettings);
  generate_attestation(run_id: string): void;
}

export declare class AuditReportGenerator {
  constructor(settings: ThegentSettings);
  generate_monthly_report(): void;
}

export declare function generate_attestation(run_id: string): void;
export declare function generate_monthly_report(): void;
