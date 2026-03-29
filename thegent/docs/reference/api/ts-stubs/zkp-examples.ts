// Auto-generated usage examples for zkp
// Source: generate-api-docs.py

import { ZKGovernor, ZKProof, generate_proof, verify_proof } from "./zkp";

// Create a ZKGovernor instance
const zkgovernor = new ZKGovernor("example_agent_id");
zkgovernor.generate_proof("example_secret_context", "example_challenge");
zkgovernor.verify_proof(undefined as unknown as ZKProof, "example_known_commitment");

// Create a ZKProof instance
const zkproof = new ZKProof();

// Call generate_proof
generate_proof(undefined as unknown as any, "example_secret_context", "example_challenge");
// Call verify_proof
verify_proof(undefined as unknown as any, undefined as unknown as ZKProof, "example_known_commitment");
