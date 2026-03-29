// Auto-generated TypeScript declarations for ledger
// Source: generate-api-docs.py

export declare class IncidentLedger extends LedgerVerifier {
  constructor(ledger_path: string);
  get_run_artifacts(run_id: string): void;
  record_artifact(run_id: string, action: string, payload: Record<(str, Any)>): void;
  verify_integrity(): void;
}

export declare class LedgerVerifier {
  constructor(ledger_path: string);
  verify_integrity(): void;
}

export declare function get_run_artifacts(run_id: string): void;
export declare function record_artifact(run_id: string, action: string, payload: Record<(str, Any)>): void;
export declare function verify_integrity(): boolean;
