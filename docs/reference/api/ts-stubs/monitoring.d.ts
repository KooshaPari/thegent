// Auto-generated TypeScript declarations for monitoring
// Source: generate-api-docs.py

export declare class CostMetrics {
}

export declare class HealthStatus {
}

export declare class MonitoringEngine {
  constructor();
  check_health(crew: Crew): void;
  get_summary(crew_id: string): void;
  record_execution(crew_id: string, results: Record<(str, ExecutionResult)>, metadata: any): void;
  track_costs(crew_id: string, results: Record<(str, ExecutionResult)>): void;
  track_performance(crew_id: string, results: Record<(str, ExecutionResult)>): void;
}

export declare class PerformanceMetrics {
}

export declare function check_health(crew: Crew): void;
export declare function get_summary(crew_id: string): void;
export declare function record_execution(crew_id: string, results: Record<(str, ExecutionResult)>, metadata: any): void;
export declare function track_costs(crew_id: string, results: Record<(str, ExecutionResult)>): void;
export declare function track_performance(crew_id: string, results: Record<(str, ExecutionResult)>): void;
