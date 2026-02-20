//! Supermemory integration client for thegent
//! 
//! Provides multi-layer (L1-L4) memory architecture:
//! - L1: In-process LRU cache
//! - L2: File-based persistent cache
//! - L3: Supermemory knowledge graph API
//! - L4: Artifact document storage

pub mod client;
pub mod error;
pub mod types;
pub mod cache;

pub use client::SupermemoryClient;
pub use error::{Error, Result};
pub use types::{KnowledgeNode, Relationship, AuthMethod};

/// Re-export common items
pub mod prelude {
    pub use crate::client::SupermemoryClient;
    pub use crate::error::{Error, Result};
    pub use crate::types::{KnowledgeNode, Relationship, AuthMethod};
}
