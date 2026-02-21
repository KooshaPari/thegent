// Auto-generated TypeScript declarations for disk
// Source: generate-api-docs.py

export declare class DiskIoStats {
}

export declare class DiskMonitor {
  get_disk_usage(path: string): void;
  get_io_stats(device: any): void;
  list_devices(): void;
  sample_queue_depth(interval_s: number): void;
}

export declare class DiskQueueSample {
}

export declare function get_disk_usage(path: string): void;
export declare function get_io_stats(device: any): void;
export declare function list_devices(): void;
export declare function sample_queue_depth(interval_s: number): void;
