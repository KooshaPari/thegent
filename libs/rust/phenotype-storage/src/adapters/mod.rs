//! Adapters layer - Infrastructure implementations.
//!
//! This layer contains concrete implementations of the domain ports:
//! - In-memory repository (for testing)
//! - PostgreSQL adapter
//! - Redis cache adapter
//! - etc.

pub mod in_memory;
pub mod postgres;

#[cfg(feature = "redis")]
pub mod redis;

pub use in_memory::*;
pub use postgres::*;

#[cfg(feature = "redis")]
pub use redis::*;
