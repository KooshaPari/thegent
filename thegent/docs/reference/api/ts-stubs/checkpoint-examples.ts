// Auto-generated usage examples for checkpoint
// Source: generate-api-docs.py

import { create, get, list_checkpoints } from "./checkpoint";

// Call create
create("example_session_dir", "example_reason", "example_dag_content", "example_owner");
// Call get
get("example_session_dir", "example_checkpoint_id");
// Call list_checkpoints
list_checkpoints("example_session_dir", 0);
