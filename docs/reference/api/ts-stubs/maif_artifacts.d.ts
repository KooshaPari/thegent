// Auto-generated TypeScript declarations for maif_artifacts
// Source: generate-api-docs.py

export declare class MAIFArtifact {
  constructor(action: Record<(str, Any)>, signature: any);
  sign(private_key: string): void;
  to_dict(): void;
  verify(public_key: string): void;
}

export declare function sign(private_key: string): void;
export declare function to_dict(): void;
export declare function verify(public_key: string): void;
