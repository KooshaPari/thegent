// Auto-generated TypeScript declarations for workstream_automation
// Source: generate-api-docs.py

export declare class WorkStreamAutomation {
  constructor(work_stream_path: any);
  claim_item(item_id: string, agent_id: string): void;
  complete_item(item_id: string, agent_id: string): void;
  read_backlog(): void;
}

export declare function claim_item(item_id: string, agent_id: string): void;
export declare function complete_item(item_id: string, agent_id: string): void;
export declare function read_backlog(): void;
