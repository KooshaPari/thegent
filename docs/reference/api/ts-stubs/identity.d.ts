// Auto-generated TypeScript declarations for identity
// Source: generate-api-docs.py

export declare class AgentDIDDocument extends BaseModel {
}

export declare class AgentIdentity {
  constructor(agent_name: string, swarm_id: string);
  get_did_document(): void;
  sign(data: string): void;
  verify(data: string, signature: string): void;
}

export declare class VerifiableCredential extends BaseModel {
}

export declare function get_did_document(): void;
export declare function sign(data: string): void;
export declare function verify(data: string, signature: string): void;
