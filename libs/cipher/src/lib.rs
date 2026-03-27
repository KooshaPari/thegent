//! Cipher — Simple, safe cryptography utilities for Rust
//!
//! Provides:
//! - Encryption: AES-GCM, ChaCha20-Poly1305
//! - Hashing: SHA-256, BLAKE3, Argon2
//! - Signatures: Ed25519, ECDSA
//! - Key Derivation: HKDF, PBKDF2

pub mod core {
    //! Core functionality
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
