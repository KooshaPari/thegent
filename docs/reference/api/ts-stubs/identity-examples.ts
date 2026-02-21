// Auto-generated usage examples for identity
// Source: generate-api-docs.py

import { AgentDIDDocument, AgentIdentity, VerifiableCredential, get_did_document, sign, verify } from "./identity";

// Create a AgentDIDDocument instance
const agentdiddocument = new AgentDIDDocument();

// Create a AgentIdentity instance
const agentidentity = new AgentIdentity("example_agent_name", "example_swarm_id");
agentidentity.get_did_document();
agentidentity.sign("example_data");
agentidentity.verify("example_data", "example_signature");

// Create a VerifiableCredential instance
const verifiablecredential = new VerifiableCredential();

// Call get_did_document
get_did_document(undefined as unknown as any);
// Call sign
sign(undefined as unknown as any, "example_data");
// Call verify
verify(undefined as unknown as any, "example_data", "example_signature");
