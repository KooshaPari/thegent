// Auto-generated TypeScript declarations for zkp
// Source: generate-api-docs.py

export declare class ZKGovernor {
  constructor(agent_id: string);
  generate_proof(secret_context: string, challenge: string): void;
  verify_proof(proof: ZKProof, known_commitment: string): void;
}

export declare class ZKProof extends BaseModel {
}

export declare function generate_proof(secret_context: string, challenge: string): void;
export declare function verify_proof(proof: ZKProof, known_commitment: string): void;
