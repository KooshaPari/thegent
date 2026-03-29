// Auto-generated TypeScript declarations for constitution
// Source: generate-api-docs.py

export declare class ConstitutionManager {
  constructor(constitution_path: string);
  critique_action(action: Record<(str, Any)>): void;
  generate_poa(action_id: string, aligned: boolean): void;
}

export declare class ConstitutionalViolation extends BaseModel {
}

export declare class ProofOfAlignment extends BaseModel {
}

export declare function critique_action(action: Record<(str, Any)>): void;
export declare function generate_poa(action_id: string, aligned: boolean): void;
