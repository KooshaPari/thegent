//! Phenotype Cache Library
//!
//! A comprehensive cache library following:
//! - Hexagonal Architecture (Ports & Adapters)
//! - Clean Architecture principles
//! - SOLID principles
//! - xDD methodologies (TDD, BDD, DDD)
//!
//! # Architecture
//!
//! ```text
//! +------------------+
//! |   Domain Layer   |  <-- Pure cache concepts (no external deps)
//! |  - CacheEntry    |
//! |  - EvictionPolicy|
//! |  - CachePort     |
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |  Application     |  <-- Cache services
//! |  - CacheService  |
//! |  - Registry      |
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |   Adapters       |  <-- Storage adapters
//! |  - InMemory      |
//! |  - Redis         |
//! +------------------+
//! ```
//!
//! # Usage
//!
//! ```rust
//! use phenotype_cache::{CachePort, InMemoryCache};
//!
//! let cache = InMemoryCache::new();
//! cache.set("key", "value").await?;
//! let value = cache.get("key").await?;
//! ```

pub mod domain;
pub mod application;
pub mod adapters;

pub use domain::*;
pub use application::*;
pub use adapters::*;

pub mod prelude {
    pub use crate::domain::*;
    pub use crate::application::*;
}
