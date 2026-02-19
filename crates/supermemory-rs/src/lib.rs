//! Supermemory.ai Rust client library.
//!
//! This crate provides a high-level Rust interface to Supermemory.ai,
//! enabling agents to read and write conversations, documents, and artifacts.
//!
//! # Examples
//!
//! ```no_run
//! use supermemory_rs::SupermemoryClient;
//!
//! #[tokio::main]
//! async fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     let client = SupermemoryClient::from_env()?;
//!     let conversations = client.list_conversations().await?;
//!     for conv in conversations {
//!         println!("{}: {}", conv.id, conv.title);
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

// Re-export common types (stub for now)
#[derive(Debug, Clone)]
pub struct SupermemoryClient;

impl SupermemoryClient {
    /// Create a new Supermemory client from environment variables.
    ///
    /// Reads `SM_API_KEY` and optionally `SM_PROJECT` environment variables.
    ///
    /// # Errors
    ///
    /// Returns an error if `SM_API_KEY` is not set or invalid.
    pub fn from_env() -> Result<Self> {
        todo!("Implement from_env in auth module")
    }

    /// List all conversations.
    pub async fn list_conversations(&self) -> Result<Vec<String>> {
        todo!("Implement list_conversations in api::conversations")
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn test_client_creation() {
        // Stub test - will be replaced with actual client tests
    }
}
