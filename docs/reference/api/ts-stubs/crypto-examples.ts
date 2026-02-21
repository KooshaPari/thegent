// Auto-generated usage examples for crypto
// Source: generate-api-docs.py

import { SigningKey, VerifyingKey, from_pem, generate, get_public_key, hash_data, sign, to_pem, verify } from "./crypto";

// Create a SigningKey instance
const signingkey = new SigningKey(undefined as unknown as rsa.RSAPrivateKey);
signingkey.from_pem(undefined as unknown as Uint8Array);
signingkey.generate();
signingkey.get_public_key();
signingkey.sign(undefined as unknown as Uint8Array);
signingkey.to_pem();

// Create a VerifyingKey instance
const verifyingkey = new VerifyingKey(undefined as unknown as rsa.RSAPublicKey);
verifyingkey.from_pem(undefined as unknown as Uint8Array);
verifyingkey.to_pem();
verifyingkey.verify(undefined as unknown as Uint8Array, undefined as unknown as Uint8Array);

// Call from_pem
from_pem(undefined as unknown as any, undefined as unknown as Uint8Array);
// Call generate
generate(undefined as unknown as any);
// Call get_public_key
get_public_key(undefined as unknown as any);
// Call hash_data
hash_data(undefined as unknown as Uint8Array);
// Call sign
sign(undefined as unknown as any, undefined as unknown as Uint8Array);
// Call to_pem
to_pem(undefined as unknown as any);
// Call verify
verify(undefined as unknown as any, undefined as unknown as Uint8Array, undefined as unknown as Uint8Array);
