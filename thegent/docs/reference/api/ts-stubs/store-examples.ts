// Auto-generated usage examples for store
// Source: generate-api-docs.py

import { MAIFArtifactStore, get, list_by_session, store } from "./store";

// Create a MAIFArtifactStore instance
const maifartifactstore = new MAIFArtifactStore("example_db_path");
maifartifactstore.get("example_artifact_id");
maifartifactstore.list_by_session("example_session_id");
maifartifactstore.store(undefined as unknown as MAIFArtifact);

// Call get
get(undefined as unknown as any, "example_artifact_id");
// Call list_by_session
list_by_session(undefined as unknown as any, "example_session_id");
// Call store
store(undefined as unknown as any, undefined as unknown as MAIFArtifact);
