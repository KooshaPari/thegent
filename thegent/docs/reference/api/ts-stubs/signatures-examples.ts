// Auto-generated usage examples for signatures
// Source: generate-api-docs.py

import { ArtifactSigner, create_signed_artifact, generate_artifact_hash, sign_artifact, verify_envelope, verify_signature } from "./signatures";

// Create a ArtifactSigner instance
const artifactsigner = new ArtifactSigner(undefined as unknown as any);
artifactsigner.create_signed_artifact("example_artifact_type", undefined as unknown as Record<(str, Any)>);
artifactsigner.verify_envelope(undefined as unknown as Record<(str, Any)>);

// Call create_signed_artifact
create_signed_artifact(undefined as unknown as any, "example_artifact_type", undefined as unknown as Record<(str, Any)>);
// Call generate_artifact_hash
generate_artifact_hash(undefined as unknown as Record<(str, Any)>);
// Call sign_artifact
sign_artifact(undefined as unknown as Record<(str, Any)>, "example_secret_key");
// Call verify_envelope
verify_envelope(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call verify_signature
verify_signature(undefined as unknown as Record<(str, Any)>, "example_signature", "example_secret_key");
