// Auto-generated TypeScript declarations for api
// Source: generate-api-docs.py

export declare class ArtifactAPI {
  constructor(signing_key: SigningKey, verifying_key: VerifyingKey, storage: any, registry: any);
  get_artifact_type_info(artifact_type: string): void;
}

export declare function get_artifact_type_info(artifact_type: string): void;
