// Auto-generated TypeScript declarations for watch_mode
// Source: generate-api-docs.py

export declare class DocumentationWatcher {
  constructor(source_dir: string, output_dir: string, build_func: Callable);
  start(poll_interval: number): void;
  stop(): void;
}

export declare function start(poll_interval: number): void;
export declare function stop(): void;
