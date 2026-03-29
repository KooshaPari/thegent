// Auto-generated TypeScript declarations for artifacts
// Source: generate-api-docs.py

export declare class MAIFArtifact {
}

export declare class MAIFArtifactStore {
  constructor(db_path: string);
  get(artifact_id: string): void;
  store(artifact: MAIFArtifact): void;
}

export declare class MAIFHook {
  constructor(artifact_store: MAIFArtifactStore, private_key: rsa.RSAPrivateKey, agent_id: string, session_id: string);
  record_action(action_type: string, payload: Record<(str, Any)>, chain_of_thought: any): void;
}

export declare function generate_signing_key(): void;
export declare function get(artifact_id: string): void;
export declare function load_private_key(path: string, password: any): void;
export declare function record_action(action_type: string, payload: Record<(str, Any)>, chain_of_thought: any): void;
export declare function save_private_key(private_key: rsa.RSAPrivateKey, path: string, password: any): void;
export declare function sign_artifact(artifact: MAIFArtifact, private_key: rsa.RSAPrivateKey): void;
export declare function store(artifact: MAIFArtifact): void;
export declare function verify_artifact(artifact: MAIFArtifact, public_key: rsa.RSAPublicKey): void;
