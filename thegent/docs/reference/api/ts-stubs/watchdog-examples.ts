// Auto-generated usage examples for watchdog
// Source: generate-api-docs.py

import { BackgroundTaskWatcher, check_completions, get_known_sessions, register_callback, reset, run_once, wait_for_completion } from "./watchdog";

// Create a BackgroundTaskWatcher instance
const backgroundtaskwatcher = new BackgroundTaskWatcher(undefined as unknown as any, 0);
backgroundtaskwatcher.check_completions();
backgroundtaskwatcher.get_known_sessions();
backgroundtaskwatcher.register_callback(undefined as unknown as CompletionCallback);
backgroundtaskwatcher.reset();
backgroundtaskwatcher.run_once();
backgroundtaskwatcher.wait_for_completion(undefined as unknown as any);

// Call check_completions
check_completions(undefined as unknown as any);
// Call get_known_sessions
get_known_sessions(undefined as unknown as any);
// Call register_callback
register_callback(undefined as unknown as any, undefined as unknown as CompletionCallback);
// Call reset
reset(undefined as unknown as any);
// Call run_once
run_once(undefined as unknown as any);
// Call wait_for_completion
wait_for_completion(undefined as unknown as any, undefined as unknown as any);
