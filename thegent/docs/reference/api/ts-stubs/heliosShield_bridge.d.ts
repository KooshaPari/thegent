// Auto-generated TypeScript declarations for heliosShield_bridge
// Source: generate-api-docs.py

export declare class SmartMerge {
  constructor();
  merge_files(base: string, ours: string, theirs: string, output: string): void;
}

export declare class heliosShieldBridge {
  constructor(settings: any);
  broadcast_intent(agent_id: string, intent_type: string, target: string): void;
  create_shared_task(task_id: string, description: string, depends_on: any): void;
  get_session_state(session_id: string): void;
  is_available(): void;
  manager(): void;
}

export declare function broadcast_intent(agent_id: string, intent_type: string, target: string): void;
export declare function create_shared_task(task_id: string, description: string, depends_on: any): void;
export declare function get_session_state(session_id: string): void;
export declare function is_available(): void;
export declare function manager(): void;
export declare function merge_files(base: string, ours: string, theirs: string, output: string): void;
