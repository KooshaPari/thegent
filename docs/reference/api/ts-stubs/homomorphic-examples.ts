// Auto-generated usage examples for homomorphic
// Source: generate-api-docs.py

import { HomomorphicContext, compute_on_encrypted, decrypt_result, encrypt_context } from "./homomorphic";

// Create a HomomorphicContext instance
const homomorphiccontext = new HomomorphicContext();
homomorphiccontext.compute_on_encrypted("example_ciphertext", "example_operation");
homomorphiccontext.decrypt_result("example_ciphertext");
homomorphiccontext.encrypt_context("example_data");

// Call compute_on_encrypted
compute_on_encrypted(undefined as unknown as any, "example_ciphertext", "example_operation");
// Call decrypt_result
decrypt_result(undefined as unknown as any, "example_ciphertext");
// Call encrypt_context
encrypt_context(undefined as unknown as any, "example_data");
