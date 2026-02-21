// Auto-generated usage examples for session_watcher
// Source: generate-api-docs.py

import { CompletionHandler, SessionEventWatcher, on_complete, on_completion, start, stop, watch_loop } from "./session_watcher";

// Create a CompletionHandler instance
const completionhandler = new CompletionHandler(undefined as unknown as SessionEventWatcher);
completionhandler.on_completion("example_session_id", 0);

// Create a SessionEventWatcher instance
const sessioneventwatcher = new SessionEventWatcher("example_session_dir");
sessioneventwatcher.on_complete(undefined as unknown as Callable<(Any, None)>);
sessioneventwatcher.start();
sessioneventwatcher.stop();

// Call on_complete
on_complete(undefined as unknown as any, undefined as unknown as Callable<(Any, None)>);
// Call on_completion
on_completion(undefined as unknown as any, "example_session_id", 0);
// Call start
start(undefined as unknown as any);
// Call stop
stop(undefined as unknown as any);
// Call watch_loop
watch_loop();
