// Auto-generated usage examples for breaker
// Source: generate-api-docs.py

import { BreakerSubcommands, check, record, reset } from "./breaker";

// Create a BreakerSubcommands instance
const breakersubcommands = new BreakerSubcommands();
breakersubcommands.check("example_breaker_id");
breakersubcommands.record("example_breaker_id", false);
breakersubcommands.reset("example_breaker_id");

// Call check
check(undefined as unknown as any, "example_breaker_id");
// Call record
record(undefined as unknown as any, "example_breaker_id", false);
// Call reset
reset(undefined as unknown as any, "example_breaker_id");
