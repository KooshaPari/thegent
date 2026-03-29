// Auto-generated TypeScript declarations for collaboration
// Source: generate-api-docs.py

export declare class CollaborativeSession {
  constructor(settings: ThegentSettings, task_id: string);
  broadcast_state(state: Record<(str, Any)>): void;
  recruit_participants(needed_capabilities: Array<string>): void;
}

export declare function broadcast_state(state: Record<(str, Any)>): void;
export declare function recruit_participants(needed_capabilities: Array<string>): void;
