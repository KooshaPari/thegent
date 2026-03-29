// Auto-generated usage examples for artifact_generator
// Source: generate-api-docs.py

import { MAIFArtifactGenerator, create_artifact, get_last_hash, reset_session } from "./artifact_generator";

// Create a MAIFArtifactGenerator instance
const maifartifactgenerator = new MAIFArtifactGenerator(undefined as unknown as SigningKey);
maifartifactgenerator.create_artifact(undefined as unknown as ActionType, "example_agent_id", "example_session_id", undefined as unknown as Uint8Array, undefined as unknown as Uint8Array, undefined as unknown as any);
maifartifactgenerator.get_last_hash("example_session_id");
maifartifactgenerator.reset_session("example_session_id");

// Call create_artifact
create_artifact(undefined as unknown as any, undefined as unknown as ActionType, "example_agent_id", "example_session_id", undefined as unknown as Uint8Array, undefined as unknown as Uint8Array, undefined as unknown as any);
// Call get_last_hash
get_last_hash(undefined as unknown as any, "example_session_id");
// Call reset_session
reset_session(undefined as unknown as any, "example_session_id");
