//! BKM-03: sign_artifact, verify_signature, artifact_hash for thegent.
//! Expects canonical JSON bytes (sorted keys). Python uses orjson for canonical.

use hmac::{Hmac, Mac};
use sha2::{Digest, Sha256};
use base16ct::lower;

#[cfg(feature = "python")]
use pyo3::prelude::*;

type HmacSha256 = Hmac<Sha256>;

/// Compute SHA-256 hex digest of canonical JSON bytes.
#[cfg_attr(feature = "python", pyfunction)]
pub fn artifact_hash_bytes(canonical_json: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(canonical_json);
    let hash = hasher.finalize();
    let mut buf = vec![0u8; base16ct::encoded_len(&hash)];
    let encoded = lower::encode(&hash, &mut buf).unwrap();
    String::from_utf8_lossy(encoded).to_string()
}

/// HMAC-SHA256 hex signature of canonical JSON bytes.
#[cfg_attr(feature = "python", pyfunction)]
pub fn sign_artifact_bytes(canonical_json: &[u8], secret_key: &str) -> String {
    let mut mac =
        HmacSha256::new_from_slice(secret_key.as_bytes()).expect("HMAC accepts any key size");
    mac.update(canonical_json);
    let result = mac.finalize();
    let bytes = result.into_bytes();
    let mut buf = vec![0u8; base16ct::encoded_len(&bytes)];
    let encoded = lower::encode(&bytes, &mut buf).unwrap();
    String::from_utf8_lossy(encoded).to_string()
}

/// Verify HMAC-SHA256 signature. Constant-time comparison.
#[cfg_attr(feature = "python", pyfunction)]
pub fn verify_signature_bytes(
    canonical_json: &[u8],
    signature: &str,
    secret_key: &str,
) -> bool {
    use subtle::ConstantTimeEq;
    let expected = sign_artifact_bytes(canonical_json, secret_key);
    if expected.len() != signature.len() {
        return false;
    }
    expected.as_bytes().ct_eq(signature.as_bytes()).into()
}

#[cfg(feature = "python")]
#[pymodule]
fn thegent_crypto(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(artifact_hash_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(sign_artifact_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(verify_signature_bytes, m)?)?;
    Ok(())
}
