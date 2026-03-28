//! Domain layer - Pure cache concepts with ZERO external dependencies.
//!
//! Following ADR-001 dependency rule:
//! - domain/ contains ZERO external dependencies
//! - Only Rust standard library allowed

mod cache_entry;
mod cache_key;
mod eviction_policy;
mod error;
mod ports;

pub use cache_entry::CacheEntry;
pub use cache_key::CacheKey;
pub use eviction_policy::EvictionPolicy;
pub use error::{CacheError, Result};
pub use ports::*;
