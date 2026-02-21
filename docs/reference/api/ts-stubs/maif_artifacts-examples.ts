// Auto-generated usage examples for maif_artifacts
// Source: generate-api-docs.py

import { MAIFArtifact, sign, to_dict, verify } from "./maif_artifacts";

// Create a MAIFArtifact instance
const maifartifact = new MAIFArtifact(undefined as unknown as Record<(str, Any)>, undefined as unknown as any);
maifartifact.sign("example_private_key");
maifartifact.to_dict();
maifartifact.verify("example_public_key");

// Call sign
sign(undefined as unknown as any, "example_private_key");
// Call to_dict
to_dict(undefined as unknown as any);
// Call verify
verify(undefined as unknown as any, "example_public_key");
