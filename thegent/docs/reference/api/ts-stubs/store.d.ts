// Auto-generated TypeScript declarations for store
// Source: generate-api-docs.py

export declare class MAIFArtifactStore {
  constructor(db_path: string);
  get(artifact_id: string): void;
  list_by_session(session_id: string): void;
  store(artifact: MAIFArtifact): void;
}

export declare function get(artifact_id: string): void;
export declare function list_by_session(session_id: string): void;
export declare function store(artifact: MAIFArtifact): void;
