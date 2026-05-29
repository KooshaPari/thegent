//! thegent-maif — MAIF (Model-Aware Information Flow) Action Artifacts
//!
//! RSA key generation, signing, and verification for action artifact integrity.

use std::collections::BTreeMap;
use std::fs;
use std::path::Path;

use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use chrono::{DateTime, Utc};
use pkcs8::{DecodePrivateKey, EncodePrivateKey, EncodePublicKey, LineEnding};
use rand::{SeedableRng, rngs::StdRng};
use rsa::{
    pkcs1::DecodeRsaPrivateKey,
    pkcs8::DecodePublicKey,
    signature::{SignatureEncoding, Signer, Verifier},
    RsaPrivateKey, RsaPublicKey,
};
use rsa::pkcs1v15::{SigningKey, VerifyingKey};
use serde::{Deserialize, Serialize};
use sha2::Sha256;
use thiserror::Error;

// ---------------------------------------------------------------------------
// Error types
// ---------------------------------------------------------------------------

#[derive(Error, Debug)]
pub enum MaifError {
    #[error("key generation failed: {0}")]
    KeyGen(String),

    #[error("signing failed: {0}")]
    Signing(String),

    #[error("verification failed: {0}")]
    Verification(String),

    #[error("payload encoding failed: {0}")]
    PayloadEncoding(String),

    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    #[error("serialization failed: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("PKCS#8 decode error")]
    Pkcs8Decode,

    #[error("PKCS#8 encode error")]
    Pkcs8Encode,

    #[error("invalid artifact: {0}")]
    InvalidArtifact(String),
}

// ---------------------------------------------------------------------------
// MAIFArtifact
// ---------------------------------------------------------------------------

/// The stable, signable portion of an artifact — excludes the signature itself.
#[derive(Debug, Serialize)]
struct SigningInput<'a> {
    action: &'a str,
    payload: &'a BTreeMap<String, serde_json::Value>,
    agent_id: &'a str,
    session_id: &'a str,
    timestamp: &'a DateTime<Utc>,
}

/// A signed, verifiable MAIF action artifact.
///
/// The payload is stored in a `BTreeMap` to guarantee deterministic ordering
/// of JSON keys — required for stable canonical representation before signing.
#[derive(Debug, Serialize, Deserialize)]
pub struct MAIFArtifact {
    pub action: String,
    pub payload: BTreeMap<String, serde_json::Value>,
    pub agent_id: String,
    pub session_id: String,
    pub timestamp: DateTime<Utc>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub signature: Option<String>,
}

impl MAIFArtifact {
    /// Construct a new artifact. Takes ownership of the payload map.
    pub fn new(
        action: String,
        payload: BTreeMap<String, serde_json::Value>,
        agent_id: String,
        session_id: String,
    ) -> Self {
        Self {
            action,
            payload,
            agent_id,
            session_id,
            timestamp: Utc::now(),
            signature: None,
        }
    }

    /// Canonical signing input — never includes the signature field.
    fn signing_input(&self) -> SigningInput<'_> {
        SigningInput {
            action: &self.action,
            payload: &self.payload,
            agent_id: &self.agent_id,
            session_id: &self.session_id,
            timestamp: &self.timestamp,
        }
    }

    /// Sign this artifact with the provided private key.
    pub fn sign(&mut self, private_key: &RsaPrivateKey) -> Result<()> {
        let signing_key = SigningKey::<Sha256>::new(private_key.clone());
        let msg = serde_json::to_string(&self.signing_input())
            .map_err(|e| MaifError::PayloadEncoding(e.to_string()))?;
        let sig = signing_key.sign(msg.as_bytes());
        self.signature = Some(URL_SAFE_NO_PAD.encode(sig.to_bytes()));
        Ok(())
    }

    /// Verify the embedded signature against the public key.
    pub fn verify(&self, public_key: &RsaPublicKey) -> Result<bool> {
        let sig = self
            .signature
            .as_ref()
            .ok_or(MaifError::InvalidArtifact("missing signature".into()))?;

        let sig_bytes = URL_SAFE_NO_PAD
            .decode(sig)
            .map_err(|_| MaifError::Verification("base64 decode failed".into()))?;

        let verifying_key = VerifyingKey::<Sha256>::new(public_key.clone());
        let sig = rsa::pkcs1v15::Signature::try_from(sig_bytes.as_ref())
            .map_err(|_| MaifError::Verification("invalid signature encoding".into()))?;
        let msg = serde_json::to_string(&self.signing_input())
            .map_err(|e| MaifError::PayloadEncoding(e.to_string()))?;
        let valid = verifying_key.verify(msg.as_bytes(), &sig).is_ok();
        Ok(valid)
    }

    /// Serialize and write the artifact to a file.
    pub fn save_to_file(&self, path: &Path) -> Result<()> {
        let json = serde_json::to_string_pretty(self)?;
        fs::write(path, json)?;
        Ok(())
    }

    /// Read and deserialize an artifact from a file.
    pub fn load_from_file(path: &Path) -> Result<Self> {
        let json = fs::read_to_string(path)?;
        let artifact: MAIFArtifact =
            serde_json::from_str(&json).map_err(|e| MaifError::InvalidArtifact(e.to_string()))?;
        Ok(artifact)
    }
}

// ---------------------------------------------------------------------------
// Key generation
// ---------------------------------------------------------------------------

/// Generate a new RSA key pair.
pub fn generate_key_pair(bits: usize) -> Result<(RsaPrivateKey, RsaPublicKey)> {
    let mut rng = StdRng::from_entropy();
    let private_key = RsaPrivateKey::new(&mut rng, bits)
        .map_err(|e| MaifError::KeyGen(e.to_string()))?;
    let public_key = RsaPublicKey::from(&private_key);
    Ok((private_key, public_key))
}

// ---------------------------------------------------------------------------
// Key loading / saving
// ---------------------------------------------------------------------------

/// Load a private key from a PEM file (PKCS#8 or PKCS#1).
pub fn load_private_key(path: &Path) -> Result<RsaPrivateKey> {
    let pem = fs::read_to_string(path)?;
    // Try PKCS#8 first (preferred), then fall back to raw RSAPrivateKey (PKCS#1)
    RsaPrivateKey::from_pkcs8_pem(&pem)
        .or_else(|_| {
            // PKCS#1 / raw RSA private key PEM
            RsaPrivateKey::from_pkcs1_pem(&pem)
        })
        .map_err(|_| MaifError::Pkcs8Decode)
}

/// Load a public key from a PEM file (PKCS#8 subjectPublicKeyInfo).
pub fn load_public_key(path: &Path) -> Result<RsaPublicKey> {
    let pem = fs::read_to_string(path)?;
    RsaPublicKey::from_public_key_pem(&pem).map_err(|_| MaifError::Pkcs8Decode)
/// # Example
/// ```
/// use thegent_path_resolve::PathResolver;
///
/// let resolver = PathResolver::new();
/// if let Some(path) = resolver.resolve("codex") {
///     println!("Found codex at: {}", path);
/// }
/// ```
pub struct PathResolver {
    skip_dirs: Vec<PathBuf>,
}

impl PathResolver {
    /// Create a new path resolver
    pub fn new() -> Self {
        Self {
            skip_dirs: Vec::new(),
        }
    }

    /// Create with directories to skip (e.g., shim directories)
    pub fn with_skip_dirs(skip_dirs: Vec<String>) -> Self {
        Self {
            skip_dirs: skip_dirs.iter().map(PathBuf::from).collect(),
        }
    }

    /// Resolve a binary name to its full path
    ///
    /// Returns `None` if not found or if in skip directory.
    ///
    /// # Example
    /// ```
    /// let resolver = PathResolver::new();
    /// assert!(resolver.resolve("sh").is_some());
    /// assert!(resolver.resolve("nonexistent12345").is_none());
    /// ```
    pub fn resolve(&self, name: &str) -> Option<String> {
        // Build safe PATH (exclude skip_dirs)
        let safe_path = self.build_safe_path();
        let cwd = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));

        // Use which crate (fast, native, cross-platform)
        match which_in(name, Some(safe_path), &cwd) {
            Ok(path) => {
                let path_str = path.to_string_lossy().to_string();
                // Check if in skip_dirs
                if self.is_in_skip_dirs(&path_str) {
                    None
                } else {
                    Some(path_str)
                }
            }
            Err(_) => None,
        }
    }

    /// Resolve multiple binaries at once (more efficient than multiple calls)
    ///
    /// # Example
    /// ```
    /// let resolver = PathResolver::new();
    /// let results = resolver.resolve_many(&["sh", "bash", "codex"]);
    /// ```
    pub fn resolve_many(&self, names: &[&str]) -> HashMap<String, Option<String>> {
        names
            .iter()
            .map(|name| (name.to_string(), self.resolve(name)))
            .collect()
    }

    fn build_safe_path(&self) -> String {
        use std::env;
        env::var("PATH").unwrap_or_default()
    }

    fn is_in_skip_dirs(&self, path: &str) -> bool {
        if self.skip_dirs.is_empty() {
            return false;
        }

        let path_buf = PathBuf::from(path);
        self.skip_dirs.iter().any(|skip| {
            path_buf.starts_with(skip)
                || path_buf
                    .canonicalize()
                    .map_or(false, |p| p.starts_with(skip))
        })
    }
}

impl Default for PathResolver {
    fn default() -> Self {
        Self::new()
    }
}

/// Convenience function for simple use cases
///
/// # Example
/// ```
/// use thegent_path_resolve::resolve_binary;
///
/// if let Some(path) = resolve_binary("codex") {
///     println!("Found codex at: {}", path);
/// }
/// ```
pub fn resolve_binary(name: &str) -> Option<String> {
    PathResolver::new().resolve(name)
}

#[cfg(all(feature = "python", not(test)))]
#[pyfunction]
fn resolve_binary(name: &str, skip_dirs: Option<Vec<String>>) -> PyResult<Option<String>> {
    let resolver = if let Some(skip) = skip_dirs {
        PathResolver::with_skip_dirs(skip)
    } else {
        PathResolver::new()
    };
    Ok(resolver.resolve(name))
}


/// Write a private key to a PEM file (PKCS#8).
pub fn save_private_key(key: &RsaPrivateKey, path: &Path) -> Result<()> {
    let pem = key
        .to_pkcs8_pem(LineEnding::LF)
        .map_err(|_| MaifError::Pkcs8Encode)?;
    fs::write(path, pem.as_str())?;
    Ok(())
}

/// Write a public key to a PEM file.
pub fn save_public_key(key: &RsaPublicKey, path: &Path) -> Result<()> {
    let pem = key
        .to_public_key_pem(LineEnding::LF)
        .map_err(|_| MaifError::Pkcs8Encode)?;
    fs::write(path, pem)?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Re-export types for library consumers
// ---------------------------------------------------------------------------


// ---------------------------------------------------------------------------
// Boilerplate
// ---------------------------------------------------------------------------

/// Shorthand for `Result<T, MaifError>`.
pub type Result<T> = std::result::Result<T, MaifError>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_raw_sign_verify() {
        use rsa::signature::{Signer, Verifier};
        use rsa::pkcs1v15::{SigningKey, VerifyingKey};
        use rsa::traits::PublicKeyParts;

        let (private_key, public_key) = generate_key_pair(2048).unwrap();
        assert!(public_key.n().bits() >= 2040);

        let msg = b"hello world";
        let signing_key = SigningKey::<Sha256>::new(private_key.clone());
        let sig = signing_key.sign(msg);
        let sig_bytes: Box<[u8]> = sig.into();

        let verifying_key = VerifyingKey::<Sha256>::new(public_key.clone());
        let loaded_sig = rsa::pkcs1v15::Signature::try_from(sig_bytes.as_ref()).unwrap();
        let ok = verifying_key.verify(msg, &loaded_sig).is_ok();
        assert!(ok, "raw RSA sign/verify should work");
    }

    #[test]
    fn test_keygen_roundtrip() {
        let (private_key, public_key) = generate_key_pair(2048).unwrap();
        use rsa::traits::PublicKeyParts;
        assert!(public_key.n().bits() >= 2040); // RSA key length check

        // Sign and verify
        let mut artifact = MAIFArtifact::new(
            "test_action".into(),
            BTreeMap::new(),
            "agent-1".into(),
            "session-1".into(),
        );
        artifact.sign(&private_key).unwrap();
        assert!(artifact.verify(&public_key).unwrap());
    }

    #[test]
    fn test_save_load_roundtrip() {
        let tmp = std::env::temp_dir();
        let (private_key, public_key) = generate_key_pair(2048).unwrap();
        let priv_path = tmp.join("maif_test_priv.pem");
        let pub_path = tmp.join("maif_test_pub.pem");
        let _ = std::fs::remove_file(&priv_path);
        let _ = std::fs::remove_file(&pub_path);

        save_private_key(&private_key, &priv_path).unwrap();
        save_public_key(&public_key, &pub_path).unwrap();

        let loaded_priv = load_private_key(&priv_path).unwrap();
        let loaded_pub = load_public_key(&pub_path).unwrap();

        let mut artifact = MAIFArtifact::new(
            "roundtrip".into(),
            BTreeMap::new(),
            "agent".into(),
            "session".into(),
        );
        artifact.sign(&loaded_priv).unwrap();
        assert!(artifact.verify(&loaded_pub).unwrap());
    }

    #[test]
    fn test_verify_wrong_key() {
        let (priv1, _pub1) = generate_key_pair(2048).unwrap();
        let (_priv2, pub2) = generate_key_pair(2048).unwrap();

        let mut artifact = MAIFArtifact::new(
            "test".into(),
            BTreeMap::new(),
            "a".into(),
            "s".into(),
        );
        artifact.sign(&priv1).unwrap();
        assert!(!artifact.verify(&pub2).unwrap()); // wrong key
    }

    #[test]
    fn test_verify_tampered() {
        let (r#priv, pub_key) = generate_key_pair(2048).unwrap();
        let mut artifact = MAIFArtifact::new(
            "test".into(),
            BTreeMap::new(),
            "a".into(),
            "s".into(),
        );
        artifact.sign(&r#priv).unwrap();

        // Tamper with the action
        artifact.action = "hacked".into();
        assert!(!artifact.verify(&pub_key).unwrap());

    }
}
