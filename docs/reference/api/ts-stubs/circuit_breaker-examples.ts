// Auto-generated usage examples for circuit_breaker
// Source: generate-api-docs.py

import { is_open, should_allow, trip } from "./circuit_breaker";

// Call is_open
is_open("example_session_dir", "example_target", "example_category");
// Call should_allow
should_allow("example_session_dir", "example_target", "example_category");
// Call trip
trip("example_session_dir", "example_target", "example_category");
