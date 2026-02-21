// Auto-generated usage examples for proof_carrying
// Source: generate-api-docs.py

import { PCCVerifier, Proof, register_proof, verify_tool } from "./proof_carrying";

// Create a PCCVerifier instance
const pccverifier = new PCCVerifier();
pccverifier.register_proof("example_tool_id", "example_property_id", "example_signature", "example_proof_type");
pccverifier.verify_tool("example_tool_id", "example_tool_code");

// Create a Proof instance
const proof = new Proof();

// Call register_proof
register_proof(undefined as unknown as any, "example_tool_id", "example_property_id", "example_signature", "example_proof_type");
// Call verify_tool
verify_tool(undefined as unknown as any, "example_tool_id", "example_tool_code");
