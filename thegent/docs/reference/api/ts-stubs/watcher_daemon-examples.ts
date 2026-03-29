// Auto-generated usage examples for watcher_daemon
// Source: generate-api-docs.py

import { WatchEvent, WatchSpec, WatcherDaemon, _SpecHandler, add_watch, get_watcher_daemon, is_running, list_watches, on_created, on_deleted, on_modified, on_moved, remove_watch, start, stop } from "./watcher_daemon";

// Create a WatchEvent instance
const watchevent = new WatchEvent();

// Create a WatchSpec instance
const watchspec = new WatchSpec();

// Create a WatcherDaemon instance
const watcherdaemon = new WatcherDaemon();
watcherdaemon.add_watch(undefined as unknown as WatchSpec);
watcherdaemon.is_running();
watcherdaemon.list_watches();
watcherdaemon.remove_watch("example_watch_id");
watcherdaemon.start();
watcherdaemon.stop();

// Create a _SpecHandler instance
const _spechandler = new _SpecHandler("example_watch_id", undefined as unknown as WatchSpec, undefined as unknown as any);
_spechandler.on_created(undefined as unknown as any);
_spechandler.on_deleted(undefined as unknown as any);
_spechandler.on_modified(undefined as unknown as any);
_spechandler.on_moved(undefined as unknown as any);

// Call add_watch
add_watch(undefined as unknown as any, undefined as unknown as WatchSpec);
// Call get_watcher_daemon
get_watcher_daemon();
// Call is_running
is_running(undefined as unknown as any);
// Call list_watches
list_watches(undefined as unknown as any);
// Call on_created
on_created(undefined as unknown as any, undefined as unknown as any);
// Call on_deleted
on_deleted(undefined as unknown as any, undefined as unknown as any);
// Call on_modified
on_modified(undefined as unknown as any, undefined as unknown as any);
// Call on_moved
on_moved(undefined as unknown as any, undefined as unknown as any);
// Call remove_watch
remove_watch(undefined as unknown as any, "example_watch_id");
// Call start
start(undefined as unknown as any);
// Call stop
stop(undefined as unknown as any);
