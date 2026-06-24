// SPDX-License-Identifier: MIT OR Apache-2.0
//! Supermemory integration client for thegent
//!
//! This crate provides a high-level Rust interface to Supermemory.ai,
//! enabling agents to read and write conversations, documents, and artifacts.
//! Includes multi-layer (L1-L4) memory architecture:
//! - L1: In-process LRU cache
//! - L2: File-based persistent cache
//! - L3: Supermemory knowledge graph API
//! - L4: Artifact document storage
//!
//! # Examples
//!
//! ```ignore
//! use thegent_memory::SupermemoryClient;
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

pub mod client;
pub mod error;
pub mod types;

pub mod v2;

pub use client::SupermemoryClient;
pub use error::{Error, Result};
pub use types::{
    AuthMethod, KnowledgeNode, MemoryData, MemoryId, MemoryOperation, MemoryQuery, MemoryResponse,
    MemoryResult, OperationType, QueryResult, Relationship, ResponseMetadata, SessionContext,
    SessionId,
};

/// Re-export common items
pub mod prelude {
    pub use crate::client::SupermemoryClient;
    pub use crate::error::{Error, Result};
    pub use crate::types::{
        AuthMethod, KnowledgeNode, MemoryData, MemoryId, MemoryOperation, MemoryQuery,
        MemoryResponse, MemoryResult, OperationType, QueryResult, Relationship, ResponseMetadata,
        SessionContext, SessionId,
    };
    pub use crate::v2::{
        CogneeAdapter, CompositeAdapter, LettaAdapter, Mem0Adapter, MemoryError, MemoryPort,
        MemoryProvider, MemoryQuery as V2MemoryQuery, MemoryRecord, MemoryScope, MemoryValue,
        SupermemoryAdapter,
    };
}
