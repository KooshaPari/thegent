// Auto-generated usage examples for fast_file_watcher
// Source: generate-api-docs.py

import { FastFileWatcher, SimpleHandler, backend, on_any_event, start, stop, watch, watch_files } from "./fast_file_watcher";

// Create a FastFileWatcher instance
const fastfilewatcher = new FastFileWatcher(undefined as unknown as any, false);
fastfilewatcher.backend();
fastfilewatcher.start(undefined as unknown as any);
fastfilewatcher.stop();
fastfilewatcher.watch(undefined as unknown as Callable<(Any, None)>);

// Create a SimpleHandler instance
const simplehandler = new SimpleHandler();
simplehandler.on_any_event(undefined as unknown as FileSystemEvent);

// Call backend
backend(undefined as unknown as any);
// Call on_any_event
on_any_event(undefined as unknown as any, undefined as unknown as FileSystemEvent);
// Call start
start(undefined as unknown as any, undefined as unknown as any);
// Call stop
stop(undefined as unknown as any);
// Call watch
watch(undefined as unknown as any, undefined as unknown as Callable<(Any, None)>);
// Call watch_files
watch_files(undefined as unknown as any, undefined as unknown as Callable<(Any, None)>, false);
