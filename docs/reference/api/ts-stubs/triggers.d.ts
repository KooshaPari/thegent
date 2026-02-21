// Auto-generated TypeScript declarations for triggers
// Source: generate-api-docs.py

export declare class HealthThresholdTrigger {
  constructor(loop: any, threshold: number, check_interval: number);
  start(): void;
  stop(): void;
}

export declare class ManualTrigger {
  constructor(loop: any);
  run(force: boolean): void;
}

export declare class TimerTrigger {
  constructor(loop: any, config: TriggerConfig);
  start(): void;
  stop(): void;
}

export declare class TriggerConfig extends BaseModel {
}

export declare class TriggerProtocol extends Protocol {
  start(): void;
  stop(): void;
}

export declare class WatchdogTrigger {
  constructor(loop: any, config: TriggerConfig);
  start(): void;
  stop(): void;
}

export declare class _WatchdogEventHandler extends FileSystemEventHandler {
  constructor(on_change: any, exclude_dirs: frozenset<string>, watch_extensions: frozenset<string>);
  on_created(event: any): void;
  on_deleted(event: any): void;
  on_modified(event: any): void;
}

export declare function cli(mode: string, interval: number, debounce: number, max_cycles: any, force: boolean, watch: any, project_dir: string, health_targets: any, threshold: number, lifecycle_mode: string, watch_health: number, watch_health_interval: number): void;
export declare function create_trigger(mode: string, loop: any, config: TriggerConfig): void;
export declare function main(): void;
export declare function monitor(): void;
export declare function on_created(event: any): void;
export declare function on_deleted(event: any): void;
export declare function on_modified(event: any): void;
export declare function run(force: boolean): void;
export declare function shutdown(signum: number, frame: any): void;
export declare function start(): void;
export declare function stop(): void;
export declare function watch_filter(change: Change, path_str: string): void;
