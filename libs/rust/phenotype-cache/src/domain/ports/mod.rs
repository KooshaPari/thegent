//! Ports - Interface definitions for hexagonal architecture.
//!
//! Following Hexagonal Architecture:
//! - Ports are trait definitions (interfaces)
//! - They define the contract between layers
//! - Implementation is in the adapters layer

pub mod outbound;

pub use outbound::CachePort;
