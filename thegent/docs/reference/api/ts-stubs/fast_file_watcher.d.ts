// Auto-generated TypeScript declarations for fast_file_watcher
// Source: generate-api-docs.py

export declare class FastFileWatcher {
  constructor(path: any, recursive: boolean);
  backend(): void;
  start(event_handler: any): void;
  stop(): void;
  watch(callback: Callable<(Any, None)>): void;
}

export declare class SimpleHandler extends FileSystemEventHandler {
  on_any_event(event: FileSystemEvent): void;
}

export declare function backend(): void;
export declare function on_any_event(event: FileSystemEvent): void;
export declare function start(event_handler: any): void;
export declare function stop(): void;
export declare function watch(callback: Callable<(Any, None)>): void;
export declare function watch_files(path: any, callback: Callable<(Any, None)>, recursive: boolean): void;
