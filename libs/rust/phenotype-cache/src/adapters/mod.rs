//! Adapters layer - Infrastructure implementations.
//!
//! This layer contains concrete implementations of domain ports.
//! Following Hexagonal Architecture:
//! - adapters/ implements ports defined in domain/

pub mod in_memory;

pub use in_memory::{InMemoryCache, InMemoryCacheConfig};
