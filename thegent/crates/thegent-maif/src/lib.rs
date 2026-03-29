use base64::{engine::general_purpose, Engine as _};
use chrono::{DateTime, Utc};
use rsa::{
    pkcs1v15::{SigningKey, VerifyingKey},
    signature::{SignatureEncoding, Signer, Verifier},
    RsaPrivateKey, RsaPublicKey,
};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::Sha256;
use std::collections::BTreeMap;
use std::fs;
use std::path::Path;
use thiserror::Error;
use uuid::Uuid;

#[derive(Error, Debug)]
pub enum MAIFError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("RSA error: {0}")]
    Rsa(#[from] rsa::Error),
    #[error("Signature error: {0}")]
    Signature(String),
    #[error("Base64 error: {0}")]
    Base64(#[from] base64::DecodeError),
    #[error("Verification failed")]
    VerificationFailed,
    #[error("Key error: {0}")]
    KeyError(String),
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MAIFArtifact {
    pub artifact_id: String,
    pub action_type: String,
    pub payload: BTreeMap<String, Value>,
    pub signature: Option<String>,
    pub timestamp: DateTime<Utc>,
    pub agent_id: String,
    pub session_id: String,
    pub chain_of_thought: Option<String>,
    pub verification_key_id: Option<String>,
    pub previous_artifact_id: Option<String>,
}

impl MAIFArtifact {
    pub fn new(
        action_type: String,
        payload: BTreeMap<String, Value>,
        agent_id: String,
        session_id: String,
    ) -> Self {
        Self {
            artifact_id: Uuid::new_v4().to_string(),
            action_type,
            payload,
            signature: None,
            timestamp: Utc::now(),
            agent_id,
            session_id,
            chain_of_thought: None,
            verification_key_id: None,
            previous_artifact_id: None,
        }
    }

    pub fn get_canonical_data(&self) -> Result<String, MAIFError> {
        let mut data = BTreeMap::new();
        data.insert("artifact_id", Value::String(self.artifact_id.clone()));
        data.insert("action_type", Value::String(self.action_type.clone()));
        data.insert(
            "payload",
            Value::Object(
                self.payload
                    .iter()
                    .map(|(k, v)| (k.clone(), v.clone()))
                    .collect(),
            ),
        );
        data.insert("timestamp", Value::String(self.timestamp.to_rfc3339()));
        data.insert("agent_id", Value::String(self.agent_id.clone()));
        data.insert("session_id", Value::String(self.session_id.clone()));

        if let Some(ref cot) = self.chain_of_thought {
            data.insert("chain_of_thought", Value::String(cot.clone()));
        }
        if let Some(ref vkid) = self.verification_key_id {
            data.insert("verification_key_id", Value::String(vkid.clone()));
        }
        if let Some(ref paid) = self.previous_artifact_id {
            data.insert("previous_artifact_id", Value::String(paid.clone()));
        }

        Ok(serde_json::to_string(&data)?)
    }

    pub fn sign(&mut self, private_key: &RsaPrivateKey) -> Result<(), MAIFError> {
        let canonical_data = self.get_canonical_data()?;
        let signing_key = SigningKey::<Sha256>::new(private_key.clone());
        let signature = signing_key.sign(canonical_data.as_bytes());
        self.signature = Some(general_purpose::STANDARD.encode(signature.to_bytes()));
        Ok(())
    }

    pub fn verify(&self, public_key: &RsaPublicKey) -> Result<bool, MAIFError> {
        let signature_str = self
            .signature
            .as_ref()
            .ok_or_else(|| MAIFError::Signature("No signature found".to_string()))?;
        let signature_bytes = general_purpose::STANDARD.decode(signature_str)?;
        let canonical_data = self.get_canonical_data()?;

        let verifying_key = VerifyingKey::<Sha256>::new(public_key.clone());
        let signature = rsa::pkcs1v15::Signature::try_from(signature_bytes.as_slice())
            .map_err(|e| MAIFError::Signature(format!("Invalid signature format: {}", e)))?;

        verifying_key
            .verify(canonical_data.as_bytes(), &signature)
            .map(|_| true)
            .or(Ok(false))
    }

    pub fn save_to_file(&self, path: &Path) -> Result<(), MAIFError> {
        let json = serde_json::to_string_pretty(self)?;
        fs::write(path, json)?;
        Ok(())
    }

    pub fn load_from_file(path: &Path) -> Result<Self, MAIFError> {
        let json = fs::read_to_string(path)?;
        let artifact: Self = serde_json::from_str(&json)?;
        Ok(artifact)
    }
}

pub fn generate_key_pair(bits: usize) -> Result<(RsaPrivateKey, RsaPublicKey), MAIFError> {
    let mut rng = rand::thread_rng();
    let private_key = RsaPrivateKey::new(&mut rng, bits)?;
    let public_key = RsaPublicKey::from(&private_key);
    Ok((private_key, public_key))
}

pub fn load_private_key(path: &Path) -> Result<RsaPrivateKey, MAIFError> {
    use rsa::pkcs8::DecodePrivateKey;
    let pem = fs::read_to_string(path)?;
    RsaPrivateKey::from_pkcs8_pem(&pem).map_err(|e| MAIFError::KeyError(e.to_string()))
}

pub fn load_public_key(path: &Path) -> Result<RsaPublicKey, MAIFError> {
    use rsa::pkcs8::DecodePublicKey;
    let pem = fs::read_to_string(path)?;
    RsaPublicKey::from_public_key_pem(&pem).map_err(|e| MAIFError::KeyError(e.to_string()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_artifact_creation() {
        let mut payload = BTreeMap::new();
        payload.insert("test_key".to_string(), json!("test_value"));

        let artifact = MAIFArtifact::new(
            "test_action".to_string(),
            payload,
            "test_agent".to_string(),
            "test_session".to_string(),
        );

        assert_eq!(artifact.action_type, "test_action");
        assert_eq!(artifact.agent_id, "test_agent");
        assert_eq!(artifact.session_id, "test_session");
        assert!(artifact.signature.is_none());
    }

    #[test]
    fn test_artifact_signing_and_verification() -> Result<(), MAIFError> {
        let (private_key, public_key) = generate_key_pair(2048)?;

        let mut payload = BTreeMap::new();
        payload.insert("test_key".to_string(), json!("test_value"));

        let mut artifact = MAIFArtifact::new(
            "test_action".to_string(),
            payload,
            "test_agent".to_string(),
            "test_session".to_string(),
        );

        artifact.sign(&private_key)?;
        assert!(artifact.signature.is_some());

        let verified = artifact.verify(&public_key)?;
        assert!(verified);

        Ok(())
    }

    #[test]
    fn test_invalid_signature() -> Result<(), MAIFError> {
        let (private_key, _public_key) = generate_key_pair(2048)?;
        let (_other_private, other_public) = generate_key_pair(2048)?;

        let mut payload = BTreeMap::new();
        payload.insert("test_key".to_string(), json!("test_value"));

        let mut artifact = MAIFArtifact::new(
            "test_action".to_string(),
            payload,
            "test_agent".to_string(),
            "test_session".to_string(),
        );

        artifact.sign(&private_key)?;

        // Verification with wrong public key should fail
        let verified = artifact.verify(&other_public)?;
        assert!(!verified);

        Ok(())
    }
}
