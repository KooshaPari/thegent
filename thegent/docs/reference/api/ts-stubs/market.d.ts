// Auto-generated TypeScript declarations for market
// Source: generate-api-docs.py

export declare class AgentService extends BaseModel {
}

export declare class GlobalServiceRegistry {
  constructor(storage_path: string);
  discover_services(capability: string): void;
  list_service(service: AgentService): void;
  run_auction(task_id: string, capability: string, budget: number): void;
}

export declare function discover_services(capability: string): void;
export declare function list_service(service: AgentService): void;
export declare function run_auction(task_id: string, capability: string, budget: number): void;
