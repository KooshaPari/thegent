// Auto-generated usage examples for hash_chain
// Source: generate-api-docs.py

import { HashChainValidator, get_chain_head, has_chain_head, reset_session, verify_artifact, verify_chain, verify_chain_from_head } from "./hash_chain";

// Create a HashChainValidator instance
const hashchainvalidator = new HashChainValidator(undefined as unknown as VerifyingKey);
hashchainvalidator.get_chain_head("example_session_id");
hashchainvalidator.has_chain_head("example_session_id");
hashchainvalidator.reset_session("example_session_id");
hashchainvalidator.verify_artifact(undefined as unknown as MAIFArtifact);
hashchainvalidator.verify_chain(undefined as unknown as Array<MAIFArtifact>);
hashchainvalidator.verify_chain_from_head("example_session_id", undefined as unknown as Array<MAIFArtifact>);

// Call get_chain_head
get_chain_head(undefined as unknown as any, "example_session_id");
// Call has_chain_head
has_chain_head(undefined as unknown as any, "example_session_id");
// Call reset_session
reset_session(undefined as unknown as any, "example_session_id");
// Call verify_artifact
verify_artifact(undefined as unknown as any, undefined as unknown as MAIFArtifact);
// Call verify_chain
verify_chain(undefined as unknown as any, undefined as unknown as Array<MAIFArtifact>);
// Call verify_chain_from_head
verify_chain_from_head(undefined as unknown as any, "example_session_id", undefined as unknown as Array<MAIFArtifact>);
