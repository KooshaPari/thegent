// Auto-generated TypeScript declarations for hash_chain
// Source: generate-api-docs.py

export declare class HashChainValidator {
  constructor(verifying_key: VerifyingKey);
  get_chain_head(session_id: string): void;
  has_chain_head(session_id: string): void;
  reset_session(session_id: string): void;
  verify_artifact(artifact: MAIFArtifact): void;
  verify_chain(artifacts: Array<MAIFArtifact>): void;
  verify_chain_from_head(session_id: string, artifacts: Array<MAIFArtifact>): void;
}

export declare function get_chain_head(session_id: string): void;
export declare function has_chain_head(session_id: string): void;
export declare function reset_session(session_id: string): void;
export declare function verify_artifact(artifact: MAIFArtifact): void;
export declare function verify_chain(artifacts: Array<MAIFArtifact>): void;
export declare function verify_chain_from_head(session_id: string, artifacts: Array<MAIFArtifact>): void;
