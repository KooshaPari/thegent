// Auto-generated TypeScript declarations for signatures
// Source: generate-api-docs.py

export declare class ArtifactSigner {
  constructor(settings: any);
  create_signed_artifact(artifact_type: string, payload: Record<(str, Any)>): void;
  verify_envelope(envelope: Record<(str, Any)>): void;
}

export declare function create_signed_artifact(artifact_type: string, payload: Record<(str, Any)>): void;
export declare function generate_artifact_hash(data: Record<(str, Any)>): void;
export declare function sign_artifact(data: Record<(str, Any)>, secret_key: string): void;
export declare function verify_envelope(envelope: Record<(str, Any)>): void;
export declare function verify_signature(data: Record<(str, Any)>, signature: string, secret_key: string): void;
