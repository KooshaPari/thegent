// Auto-generated TypeScript declarations for dna_storage
// Source: generate-api-docs.py

export declare class DNAStorageBridge {
  constructor();
  decode_from_dna(dna_sequence: string): void;
  encode_to_dna(digital_data: Uint8Array): void;
  estimate_stability(dna_sequence: string): void;
}

export declare function decode_from_dna(dna_sequence: string): void;
export declare function encode_to_dna(digital_data: Uint8Array): void;
export declare function estimate_stability(dna_sequence: string): void;
