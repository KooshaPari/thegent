// Auto-generated usage examples for artifacts
// Source: generate-api-docs.py

import { MAIFArtifact, MAIFArtifactStore, MAIFHook, generate_signing_key, get, load_private_key, record_action, save_private_key, sign_artifact, store, verify_artifact } from "./artifacts";

// Create a MAIFArtifact instance
const maifartifact = new MAIFArtifact();

// Create a MAIFArtifactStore instance
const maifartifactstore = new MAIFArtifactStore("example_db_path");
maifartifactstore.get("example_artifact_id");
maifartifactstore.store(undefined as unknown as MAIFArtifact);

// Create a MAIFHook instance
const maifhook = new MAIFHook(undefined as unknown as MAIFArtifactStore, undefined as unknown as rsa.RSAPrivateKey, "example_agent_id", "example_session_id");
maifhook.record_action("example_action_type", undefined as unknown as Record<(str, Any)>, undefined as unknown as any);

// Call generate_signing_key
generate_signing_key();
// Call get
get(undefined as unknown as any, "example_artifact_id");
// Call load_private_key
load_private_key("example_path", undefined as unknown as any);
// Call record_action
record_action(undefined as unknown as any, "example_action_type", undefined as unknown as Record<(str, Any)>, undefined as unknown as any);
// Call save_private_key
save_private_key(undefined as unknown as rsa.RSAPrivateKey, "example_path", undefined as unknown as any);
// Call sign_artifact
sign_artifact(undefined as unknown as MAIFArtifact, undefined as unknown as rsa.RSAPrivateKey);
// Call store
store(undefined as unknown as any, undefined as unknown as MAIFArtifact);
// Call verify_artifact
verify_artifact(undefined as unknown as MAIFArtifact, undefined as unknown as rsa.RSAPublicKey);
