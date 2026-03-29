// Auto-generated TypeScript declarations for homomorphic
// Source: generate-api-docs.py

export declare class HomomorphicContext {
  constructor();
  compute_on_encrypted(ciphertext: string, operation: string): void;
  decrypt_result(ciphertext: string): void;
  encrypt_context(data: string): void;
}

export declare function compute_on_encrypted(ciphertext: string, operation: string): void;
export declare function decrypt_result(ciphertext: string): void;
export declare function encrypt_context(data: string): void;
