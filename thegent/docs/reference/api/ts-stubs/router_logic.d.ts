// Auto-generated TypeScript declarations for router_logic
// Source: generate-api-docs.py

export declare class PurePythonRouter {
  constructor(strategy: RoutingStrategy);
  select_agent(task_description: string, available_agents: Array<unknown>): void;
}

export declare class RouteMetrics {
}

export declare class RoutingStrategy extends StrEnum {
}

export declare function select_agent(task_description: string, available_agents: Array<unknown>): any;
