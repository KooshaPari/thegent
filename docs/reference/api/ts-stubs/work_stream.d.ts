// Auto-generated TypeScript declarations for work_stream
// Source: generate-api-docs.py

export declare class WorkStreamManager {
  constructor(settings: ThegentSettings, base_dir: any);
  claim(item_id: string, agent_id: string): void;
  complete(item_id: string, agent_id: string): void;
}

export declare function claim(item_id: string, agent_id: string): void;
export declare function complete(item_id: string, agent_id: string): void;
