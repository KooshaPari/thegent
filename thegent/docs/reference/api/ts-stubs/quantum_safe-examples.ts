// Auto-generated usage examples for quantum_safe
// Source: generate-api-docs.py

import { PQCSigner, sign_artifact, verify_signature } from "./quantum_safe";

// Create a PQCSigner instance
const pqcsigner = new PQCSigner("example_algorithm");
pqcsigner.sign_artifact(undefined as unknown as Uint8Array);
pqcsigner.verify_signature(undefined as unknown as Uint8Array, "example_signature", "example_public_key");

// Call sign_artifact
sign_artifact(undefined as unknown as any, undefined as unknown as Uint8Array);
// Call verify_signature
verify_signature(undefined as unknown as any, undefined as unknown as Uint8Array, "example_signature", "example_public_key");
