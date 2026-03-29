// Auto-generated usage examples for dlq
// Source: generate-api-docs.py

import { is_poison_pill, list_pending, resolve } from "./dlq";

// Call is_poison_pill
is_poison_pill("example_session_dir", "example_run_id", 0);
// Call list_pending
list_pending("example_session_dir", 0);
// Call resolve
resolve("example_session_dir", "example_run_id", "example_resolution");
