//!
//! # Hexkit - Hexagonal Architecture Toolkit for Rust
//!
//! A lightweight library implementing Hexagonal Architecture (Ports & Adapters)
//! patterns for Rust applications.
//!
//! ## Quick Start
//!
//! ```rust,ignore
//! use hexkit::{Entity, EntityId, ValueObject};
//!
//! // Define a simple value object
//! #[derive(Debug, Clone, PartialEq, Eq, Hash)]
//! pub struct UserId(String);
//!
//! impl ValueObject for UserId {
//!     fn validate(&self) -> Result<(), String> { Ok(()) }
//! }
//!
//! impl EntityId for UserId {}
//! ```
//!
//! ## Architecture
//!
//! Hexkit provides four core layers:
//!
//! - **Domain**: Entities, Value Objects, Aggregates, Events
//! - **Ports**: Input (driving) and Output (driven) port traits
//! - **Application**: Use cases, DTOs, Mappers
//! - **Adapters**: REST, gRPC, Persistence implementations

pub mod domain;
pub mod ports;
pub mod application;
pub mod adapters;

// ============================================================================
// Core Types
// ============================================================================

use thiserror::Error;

/// Root error type for hexagonal operations
#[derive(Error, Debug)]
pub enum HexError {
    #[error("Domain violation: {0}")]
    Domain(String),
    
    #[error("Port error: {0}")]
    Port(String),
    
    #[error("Adapter error: {0}")]
    Adapter(String),
    
    #[error("Application error: {0}")]
    Application(String),
    
    #[error("Validation failed: {0}")]
    Validation(String),
    
    #[error("Not found: {0}")]
    NotFound(String),
    
    #[error("Conflict: {0}")]
    Conflict(String),
    
    #[error("Unauthorized: {0}")]
    Unauthorized(String),
}

/// Result type alias for hexagonal operations
pub type HexResult<T> = Result<T, HexError>;

// Re-exports for convenience
pub use domain::{Entity, EntityId, AggregateRoot, DomainEvent, DomainService, ValueObject};
