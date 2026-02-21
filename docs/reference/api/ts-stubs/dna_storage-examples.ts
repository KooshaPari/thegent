// Auto-generated usage examples for dna_storage
// Source: generate-api-docs.py

import { DNAStorageBridge, decode_from_dna, encode_to_dna, estimate_stability } from "./dna_storage";

// Create a DNAStorageBridge instance
const dnastoragebridge = new DNAStorageBridge();
dnastoragebridge.decode_from_dna("example_dna_sequence");
dnastoragebridge.encode_to_dna(undefined as unknown as Uint8Array);
dnastoragebridge.estimate_stability("example_dna_sequence");

// Call decode_from_dna
decode_from_dna(undefined as unknown as any, "example_dna_sequence");
// Call encode_to_dna
encode_to_dna(undefined as unknown as any, undefined as unknown as Uint8Array);
// Call estimate_stability
estimate_stability(undefined as unknown as any, "example_dna_sequence");
