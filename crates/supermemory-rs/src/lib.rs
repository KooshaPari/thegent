//! Supermemory.ai Rust client library.
//!
//! This crate provides a high-level Rust interface to Supermemory.ai,
//! enabling agents to read and write conversations, documents, and artifacts.
//!
//! # Examples
//!
//! ```ignore
//! use supermemory_rs::SupermemoryClient;
//!
//! #[tokio::main]
//! async fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     let client = SupermemoryClient::from_env()?;
//!     let conversations = client.list_conversations().await?;
//!     for conv_id in conversations {
//!         println!("conversation: {}", conv_id);
//!     }
//!     Ok(())
//! }
//! ```

pub mod error;
pub mod types;

pub use error::{Result, SupermemoryError};
pub use types::{
    MemoryData, MemoryId, MemoryOperation, MemoryQuery, MemoryResponse, MemoryResult,
    OperationType, ResponseMetadata, SessionContext, SessionId,
};

use std::env;

/// Supermemory.ai client for managing conversations and memories.
#[derive(Debug, Clone)]
pub struct SupermemoryClient {
    api_key: String,
    project: Option<String>,
    base_url: String,
}

impl SupermemoryClient {
    /// Create a new Supermemory client from environment variables.
    ///
    /// Reads `SM_API_KEY` and optionally `SM_PROJECT` environment variables.
    ///
    /// # Errors
    ///
    /// Returns an error if `SM_API_KEY` is not set or invalid.
    pub fn from_env() -> Result<Self> {
        let api_key = env::var("SM_API_KEY")
            .map_err(|_| SupermemoryError::AuthError("SM_API_KEY not set".into()))?;

        if api_key.is_empty() {
            return Err(SupermemoryError::AuthError("SM_API_KEY is empty".into()));
        }
        
        let project = env::var("SM_PROJECT").ok();
        let base_url = env::var("SM_BASE_URL")
            .unwrap_or_else(|_| "https://api.supermemory.ai/v1".to_string());
        
        Ok(Self {
            api_key,
            project,
            base_url,
        })
    }

    /// Create a new client with explicit credentials.
    pub fn new(api_key: String, project: Option<String>) -> Self {
        Self {
            api_key,
            project,
            base_url: "https://api.supermemory.ai/v1".to_string(),
        }
    }

    /// List all conversations.
    pub async fn list_conversations(&self) -> Result<Vec<String>> {
        // Placeholder implementation - would use reqwest in production
        Ok(vec![])
    }

    /// Store a memory.
    pub async fn store(&self, _data: &MemoryData) -> Result<MemoryId> {
        // Placeholder - would POST to /memories
        Ok(MemoryId::new())
    }

    /// Query memories.
    pub async fn query(&self, _query: &MemoryQuery) -> Result<Vec<MemoryResponse>> {
        // Placeholder - would POST to /query
        Ok(vec![])
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;
    use std::sync::Mutex;

    /// Mutex to serialize environment-modifying tests
    static ENV_MUTEX: Mutex<()> = Mutex::new(());

    /// Test that from_env() returns an error when SM_API_KEY is not set
    #[test]
    fn test_from_env_missing_api_key() {
        let _lock = ENV_MUTEX.lock().unwrap();
        // Ensure SM_API_KEY is not set
        env::remove_var("SM_API_KEY");

        let result = SupermemoryClient::from_env();
        assert!(result.is_err());

        match result {
            Err(SupermemoryError::AuthError(msg)) => {
                assert!(msg.contains("SM_API_KEY not set"));
            }
            _ => panic!("Expected AuthError"),
        }
    }

    /// Test that from_env() returns an error when SM_API_KEY is empty
    #[test]
    fn test_from_env_empty_api_key() {
        let _lock = ENV_MUTEX.lock().unwrap();
        // Set empty API key
        env::set_var("SM_API_KEY", "");

        let result = SupermemoryClient::from_env();

        // Clean up
        env::remove_var("SM_API_KEY");

        assert!(result.is_err());
        match result {
            Err(SupermemoryError::AuthError(msg)) => {
                assert!(msg.contains("SM_API_KEY is empty"));
            }
            _ => panic!("Expected AuthError"),
        }
    }

    /// Test that from_env() succeeds with valid API key
    #[test]
    fn test_from_env_success() {
        let _lock = ENV_MUTEX.lock().unwrap();
        env::set_var("SM_API_KEY", "test-api-key-12345");

        let result = SupermemoryClient::from_env();

        // Clean up
        env::remove_var("SM_API_KEY");

        assert!(result.is_ok());
        let client = result.unwrap();
        assert_eq!(client.api_key, "test-api-key-12345");
        assert_eq!(client.base_url, "https://api.supermemory.ai/v1");
        assert!(client.project.is_none());
    }

    /// Test that from_env() reads optional environment variables
    #[test]
    fn test_from_env_with_project() {
        let _lock = ENV_MUTEX.lock().unwrap();
        env::set_var("SM_API_KEY", "test-key");
        env::set_var("SM_PROJECT", "my-project");

        let result = SupermemoryClient::from_env();

        // Clean up
        env::remove_var("SM_API_KEY");
        env::remove_var("SM_PROJECT");

        assert!(result.is_ok());
        let client = result.unwrap();
        assert_eq!(client.project, Some("my-project".to_string()));
    }

    /// Test that from_env() reads custom base URL
    #[test]
    fn test_from_env_custom_base_url() {
        let _lock = ENV_MUTEX.lock().unwrap();
        env::set_var("SM_API_KEY", "test-key");
        env::set_var("SM_BASE_URL", "https://custom.api.com/v2");

        let result = SupermemoryClient::from_env();

        // Clean up
        env::remove_var("SM_API_KEY");
        env::remove_var("SM_BASE_URL");

        assert!(result.is_ok());
        let client = result.unwrap();
        assert_eq!(client.base_url, "https://custom.api.com/v2");
    }

    /// Test client creation with new()
    #[test]
    fn test_client_new() {
        let client = SupermemoryClient::new("my-api-key".to_string(), Some("project".to_string()));
        assert_eq!(client.api_key, "my-api-key");
        assert_eq!(client.project, Some("project".to_string()));
        assert_eq!(client.base_url, "https://api.supermemory.ai/v1");
    }

    /// Test Clone trait implementation
    #[test]
    fn test_client_clone() {
        let client = SupermemoryClient::new("key".to_string(), None);
        let cloned = client.clone();
        assert_eq!(client.api_key, cloned.api_key);
    }
}
