// Auto-generated TypeScript declarations for rust_manager
// Source: generate-api-docs.py

export declare class RustMAIFManager {
  constructor(binary_path: string, private_key_path: string, public_key_path: string);
  create_artifact(action: string, payload: Record<(str, Any)>, agent: string, session: string, output_path: string): void;
  ensure_keys(bits: number): void;
  verify_artifact(artifact_path: string): void;
}

export declare function create_artifact(action: string, payload: Record<(str, Any)>, agent: string, session: string, output_path: string): void;
export declare function ensure_keys(bits: number): void;
export declare function verify_artifact(artifact_path: string): void;
