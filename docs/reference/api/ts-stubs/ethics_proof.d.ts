// Auto-generated TypeScript declarations for ethics_proof
// Source: generate-api-docs.py

export declare class EthicalProofGenerator {
  generate(action_id: string, aligned: boolean, evidence: Array<string>): void;
}

export declare class EthicalProofVerifier {
  verify(proof: FormalEthicalProof): void;
}

export declare class FormalEthicalProof extends ProofOfAlignment {
}

export declare function generate(action_id: string, aligned: boolean, evidence: Array<string>): void;
export declare function verify(proof: FormalEthicalProof): void;
