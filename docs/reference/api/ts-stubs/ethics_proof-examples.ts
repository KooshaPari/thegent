// Auto-generated usage examples for ethics_proof
// Source: generate-api-docs.py

import { EthicalProofGenerator, EthicalProofVerifier, FormalEthicalProof, generate, verify } from "./ethics_proof";

// Create a EthicalProofGenerator instance
const ethicalproofgenerator = new EthicalProofGenerator();
ethicalproofgenerator.generate("example_action_id", false, undefined as unknown as Array<string>);

// Create a EthicalProofVerifier instance
const ethicalproofverifier = new EthicalProofVerifier();
ethicalproofverifier.verify(undefined as unknown as FormalEthicalProof);

// Create a FormalEthicalProof instance
const formalethicalproof = new FormalEthicalProof();

// Call generate
generate(undefined as unknown as any, "example_action_id", false, undefined as unknown as Array<string>);
// Call verify
verify(undefined as unknown as any, undefined as unknown as FormalEthicalProof);
