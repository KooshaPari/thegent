// Auto-generated TypeScript declarations for hybrid_coordination
// Source: generate-api-docs.py

export declare class CoordinationMetrics {
}

export declare class CoordinationMode extends Enum {
}

export declare class HybridCoordinationStrategy {
  constructor();
  coordinate(task_id: string, agents: Array<string>, swarm_size: number, avg_load: number): void;
  route_task(task_id: string, agents: Array<string>, mode: CoordinationMode, avg_load: number): void;
  select_mode(swarm_size: number, avg_load: number): void;
}

export declare function coordinate(task_id: string, agents: Array<string>, swarm_size: number, avg_load: number): void;
export declare function route_task(task_id: string, agents: Array<string>, mode: CoordinationMode, avg_load: number): void;
export declare function select_mode(swarm_size: number, avg_load: number): void;
