// Auto-generated TypeScript declarations for gpu
// Source: generate-api-docs.py

export declare class GpuInfo {
}

export declare class GpuMonitor {
  get_gpus(): void;
  get_total_utilization(): void;
  is_available(): void;
}

export declare class GpuMonitorError extends Exception {
}

export declare function get_gpus(): void;
export declare function get_total_utilization(): void;
export declare function is_available(): void;
