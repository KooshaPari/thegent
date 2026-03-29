// Auto-generated TypeScript declarations for proof_carrying
// Source: generate-api-docs.py

export declare class PCCVerifier {
  constructor();
  register_proof(tool_id: string, property_id: string, signature: string, proof_type: string): void;
  verify_tool(tool_id: string, tool_code: string): void;
}

export declare class Proof extends BaseModel {
}

export declare function register_proof(tool_id: string, property_id: string, signature: string, proof_type: string): void;
export declare function verify_tool(tool_id: string, tool_code: string): void;
