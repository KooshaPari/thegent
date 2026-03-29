// Auto-generated TypeScript declarations for evidence_graph
// Source: generate-api-docs.py

export declare class EvidenceGraph {
  constructor(session_dir: string);
  add_link(parent_id: string, child_id: string): void;
  bundle_evidence(target_path: string): void;
}

export declare function add_link(parent_id: string, child_id: string): void;
export declare function bundle_evidence(target_path: string): void;
