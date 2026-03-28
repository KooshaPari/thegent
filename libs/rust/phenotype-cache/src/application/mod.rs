//! Application layer - Use cases and services.
//!
//! This layer orchestrates domain logic.
//! It depends on domain ports (interfaces).

pub mod cache_service;
pub mod builder;

pub use cache_service::CacheService;
pub use builder::CacheBuilder;
