// Auto-generated TypeScript declarations for forensics
// Source: generate-api-docs.py

export declare class IncidentReplayer {
  constructor(ledger: IncidentLedger);
  generate_incident_report(run_id: string): void;
  replay(run_id: string): void;
}

export declare function generate_incident_report(run_id: string): void;
export declare function replay(run_id: string): void;
