// Auto-generated usage examples for rust_manager
// Source: generate-api-docs.py

import { RustMAIFManager, create_artifact, ensure_keys, verify_artifact } from "./rust_manager";

// Create a RustMAIFManager instance
const rustmaifmanager = new RustMAIFManager("example_binary_path", "example_private_key_path", "example_public_key_path");
rustmaifmanager.create_artifact("example_action", undefined as unknown as Record<(str, Any)>, "example_agent", "example_session", "example_output_path");
rustmaifmanager.ensure_keys(0);
rustmaifmanager.verify_artifact("example_artifact_path");

// Call create_artifact
create_artifact(undefined as unknown as any, "example_action", undefined as unknown as Record<(str, Any)>, "example_agent", "example_session", "example_output_path");
// Call ensure_keys
ensure_keys(undefined as unknown as any, 0);
// Call verify_artifact
verify_artifact(undefined as unknown as any, "example_artifact_path");
