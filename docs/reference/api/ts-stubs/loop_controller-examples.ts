// Auto-generated usage examples for loop_controller
// Source: generate-api-docs.py

import { LifecycleController, LoopMode, LoopState, run_loop } from "./loop_controller";

// Create a LifecycleController instance
const lifecyclecontroller = new LifecycleController(undefined as unknown as ThegentSettings, "example_worker_agent_name", "example_checker_agent_name", undefined as unknown as LoopMode, 0, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
lifecyclecontroller.run_loop("example_initial_prompt", "example_todo_spec", undefined as unknown as any, undefined as unknown as any);

// Create a LoopMode instance
const loopmode = new LoopMode();

// Create a LoopState instance
const loopstate = new LoopState();

// Call run_loop
run_loop(undefined as unknown as any, "example_initial_prompt", "example_todo_spec", undefined as unknown as any, undefined as unknown as any);
