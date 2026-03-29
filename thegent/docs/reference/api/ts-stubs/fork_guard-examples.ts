// Auto-generated usage examples for fork_guard
// Source: generate-api-docs.py

import { ForkContext, ForkExplosionGuard, get_stats, register_run } from "./fork_guard";

// Create a ForkContext instance
const forkcontext = new ForkContext();

// Create a ForkExplosionGuard instance
const forkexplosionguard = new ForkExplosionGuard();
forkexplosionguard.get_stats("example_run_id");
forkexplosionguard.register_run("example_run_id", undefined as unknown as any);

// Call get_stats
get_stats(undefined as unknown as any, "example_run_id");
// Call register_run
register_run(undefined as unknown as any, "example_run_id", undefined as unknown as any);
