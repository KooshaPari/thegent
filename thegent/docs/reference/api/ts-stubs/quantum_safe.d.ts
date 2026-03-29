// Auto-generated TypeScript declarations for quantum_safe
// Source: generate-api-docs.py

export declare class PQCSigner {
  constructor(algorithm: string);
  sign_artifact(artifact_data: Uint8Array): void;
  verify_signature(artifact_data: Uint8Array, signature: string, public_key: string): void;
}

export declare function sign_artifact(artifact_data: Uint8Array): void;
export declare function verify_signature(artifact_data: Uint8Array, signature: string, public_key: string): void;
