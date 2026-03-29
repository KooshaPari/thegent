// Auto-generated usage examples for never_idle
// Source: generate-api-docs.py

import { NeverIdleLoop, current_step, get_findings, get_last_completion, get_never_idle, get_never_idle_status, get_status, is_running, register_wake_callback, start, start_never_idle, stop, stop_never_idle } from "./never_idle";

// Create a NeverIdleLoop instance
const neveridleloop = new NeverIdleLoop(undefined as unknown as any, 0, undefined as unknown as any);
neveridleloop.current_step();
neveridleloop.get_findings();
neveridleloop.get_last_completion();
neveridleloop.get_status();
neveridleloop.is_running();
neveridleloop.register_wake_callback(undefined as unknown as WakeCallback);
neveridleloop.start();
neveridleloop.stop();

// Call current_step
current_step(undefined as unknown as any);
// Call get_findings
get_findings(undefined as unknown as any);
// Call get_last_completion
get_last_completion(undefined as unknown as any);
// Call get_never_idle
get_never_idle();
// Call get_never_idle_status
get_never_idle_status();
// Call get_status
get_status(undefined as unknown as any);
// Call is_running
is_running(undefined as unknown as any);
// Call register_wake_callback
register_wake_callback(undefined as unknown as any, undefined as unknown as WakeCallback);
// Call start
start(undefined as unknown as any);
// Call start_never_idle
start_never_idle(0, undefined as unknown as any, undefined as unknown as any);
// Call stop
stop(undefined as unknown as any);
// Call stop_never_idle
stop_never_idle();
