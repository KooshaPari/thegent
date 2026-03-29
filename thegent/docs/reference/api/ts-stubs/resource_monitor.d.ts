// Auto-generated TypeScript declarations for resource_monitor
// Source: generate-api-docs.py

export declare class ResourceMonitor {
  constructor(check_interval: number);
  detect_leak(): void;
  get_history(): void;
  get_process_info(pid: number): void;
  get_stats(): void;
  start(): void;
  stop(): void;
}

export declare class ResourceStats {
  get_suspicion_level(): void;
  is_critical(): void;
}

export declare function detect_leak(): void;
export declare function get_history(): void;
export declare function get_process_info(pid: number): void;
export declare function get_resource_monitor(): void;
export declare function get_stats(): void;
export declare function get_suspicion_level(): void;
export declare function is_critical(): void;
export declare function start(): void;
export declare function stop(): void;
