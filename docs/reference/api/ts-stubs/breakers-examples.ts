// Auto-generated usage examples for breakers
// Source: generate-api-docs.py

import { CircuitBreaker, check_spike, is_tripped, trip } from "./breakers";

// Create a CircuitBreaker instance
const circuitbreaker = new CircuitBreaker("example_session_dir");
circuitbreaker.check_spike(0);
circuitbreaker.is_tripped();
circuitbreaker.trip("example_reason", 0);

// Call check_spike
check_spike(undefined as unknown as any, 0);
// Call is_tripped
is_tripped(undefined as unknown as any);
// Call trip
trip(undefined as unknown as any, "example_reason", 0);
