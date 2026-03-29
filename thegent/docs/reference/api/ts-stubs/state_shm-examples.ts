// Auto-generated usage examples for state_shm
// Source: generate-api-docs.py

import { CircuitBreakerShm, XpTracker, _PurePythonBreakerStore, _PurePythonXpStore, award, clear, get_health_score, is_native, is_native_available, is_open, level, open_shm, record_failure, record_success, set_health_score, set_level, should_allow, state, state_int, total_xp } from "./state_shm";

// Create a CircuitBreakerShm instance
const circuitbreakershm = new CircuitBreakerShm(undefined as unknown as any, 0, 0, 0);
circuitbreakershm.get_health_score();
circuitbreakershm.is_native();
circuitbreakershm.is_open("example_target", "example_category");
circuitbreakershm.record_failure("example_target", "example_category");
circuitbreakershm.record_success("example_target", "example_category");
circuitbreakershm.set_health_score(0);
circuitbreakershm.should_allow("example_target", "example_category");
circuitbreakershm.state_int("example_target", "example_category");

// Create a XpTracker instance
const xptracker = new XpTracker(undefined as unknown as any);
xptracker.award(0);
xptracker.is_native();
xptracker.level();
xptracker.set_level(0);
xptracker.state();
xptracker.total_xp();

// Create a _PurePythonBreakerStore instance
const _purepythonbreakerstore = new _PurePythonBreakerStore();
_purepythonbreakerstore.clear(undefined as unknown as any);
_purepythonbreakerstore.is_open("example_target", "example_category", 0, 0, 0);
_purepythonbreakerstore.record_failure("example_target", "example_category");

// Create a _PurePythonXpStore instance
const _purepythonxpstore = new _PurePythonXpStore();
_purepythonxpstore.award(0);
_purepythonxpstore.state();

// Call award
award(undefined as unknown as any, 0);
// Call clear
clear(undefined as unknown as any, undefined as unknown as any);
// Call get_health_score
get_health_score(undefined as unknown as any);
// Call is_native
is_native(undefined as unknown as any);
// Call is_native_available
is_native_available();
// Call is_open
is_open(undefined as unknown as any, "example_target", "example_category");
// Call level
level(undefined as unknown as any);
// Call open_shm
open_shm(undefined as unknown as any);
// Call record_failure
record_failure(undefined as unknown as any, "example_target", "example_category");
// Call record_success
record_success(undefined as unknown as any, "example_target", "example_category");
// Call set_health_score
set_health_score(undefined as unknown as any, 0);
// Call set_level
set_level(undefined as unknown as any, 0);
// Call should_allow
should_allow(undefined as unknown as any, "example_target", "example_category");
// Call state
state(undefined as unknown as any);
// Call state_int
state_int(undefined as unknown as any, "example_target", "example_category");
// Call total_xp
total_xp(undefined as unknown as any);
