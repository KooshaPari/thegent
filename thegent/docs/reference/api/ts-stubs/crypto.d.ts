// Auto-generated TypeScript declarations for crypto
// Source: generate-api-docs.py

export declare class SigningKey {
  constructor(private_key: rsa.RSAPrivateKey);
  from_pem(pem_bytes: Uint8Array): void;
  generate(): void;
  get_public_key(): void;
  sign(data: Uint8Array): void;
  to_pem(): void;
}

export declare class VerifyingKey {
  constructor(public_key: rsa.RSAPublicKey);
  from_pem(pem_bytes: Uint8Array): void;
  to_pem(): void;
  verify(data: Uint8Array, signature: Uint8Array): void;
}

export declare function from_pem(pem_bytes: Uint8Array): void;
export declare function generate(): void;
export declare function get_public_key(): void;
export declare function hash_data(data: Uint8Array): void;
export declare function sign(data: Uint8Array): void;
export declare function to_pem(): void;
export declare function verify(data: Uint8Array, signature: Uint8Array): void;
