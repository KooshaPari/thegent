// Auto-generated TypeScript declarations for artifact_generator
// Source: generate-api-docs.py

export declare class MAIFArtifactGenerator {
  constructor(signer: SigningKey);
  create_artifact(action_type: ActionType, agent_id: string, session_id: string, input_data: Uint8Array, output_data: Uint8Array, metadata: any): void;
  get_last_hash(session_id: string): void;
  reset_session(session_id: string): void;
}

export declare function create_artifact(action_type: ActionType, agent_id: string, session_id: string, input_data: Uint8Array, output_data: Uint8Array, metadata: any): void;
export declare function get_last_hash(session_id: string): void;
export declare function reset_session(session_id: string): void;
