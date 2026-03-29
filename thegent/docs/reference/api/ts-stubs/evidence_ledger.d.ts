// Auto-generated TypeScript declarations for evidence_ledger
// Source: generate-api-docs.py

export declare class EvidenceEvent extends BaseModel {
}

export declare class EvidenceLedger {
  constructor(session_dir: string);
  ledger_path(): void;
  link_to_graph(graph: EvidenceGraph, event_hash: string, artifact_id: string): void;
  query(cycle_id: any, event_type: any): void;
  record(event_type: string, cycle_id: string, payload: Record<(str, Any)>): void;
  verify_chain(): void;
}

export declare function ledger_path(): string;
export declare function link_to_graph(graph: EvidenceGraph, event_hash: string, artifact_id: string): void;
export declare function query(cycle_id: any, event_type: any): void;
export declare function record(event_type: string, cycle_id: string, payload: Record<(str, Any)>): void;
export declare function verify_chain(): void;
