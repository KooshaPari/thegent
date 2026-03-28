//! Hexagonal Architecture Library
//!
//! A comprehensive implementation of Hexagonal Architecture (Ports & Adapters)
//! with Clean Architecture principles, SOLID compliance, and domain-driven design.
//!
//! # Architecture Layers
//!
//! 1. **Domain Layer** - Pure business logic, no external dependencies
//! 2. **Ports Layer** - Abstract interfaces (input/output)
//! 3. **Application Layer** - Use cases and orchestration
//! 4. **Adapters Layer** - Infrastructure implementations

pub mod domain;
pub mod ports;
pub mod application;
pub mod adapters;

// Re-exports
pub use adapters::*;

use thiserror::Error;

/// Root error type for the hexagonal architecture
#[derive(Error, Debug)]
pub enum HexagonalError {
    #[error("Domain error: {0}")]
    Domain(String),
    
    #[error("Port error: {0}")]
    Port(String),
    
    #[error("Adapter error: {0}")]
    Adapter(String),
    
    #[error("Application error: {0}")]
    Application(String),
    
    #[error("Validation error: {0}")]
    Validation(String),
    
    #[error("Not found: {0}")]
    NotFound(String),
    
    #[error("Conflict: {0}")]
    Conflict(String),
    
    #[error("Unauthorized: {0}")]
    Unauthorized(String),
}

/// Result type alias for hexagonal operations
pub type HexagonalResult<T> = Result<T, HexagonalError>;

/// Marker trait for aggregate roots
pub trait AggregateRoot: Send + Sync {}

/// Marker trait for domain entities
pub trait Entity: Send + Sync {
    type Id: Send + Sync + Clone + std::fmt::Debug + std::fmt::Display + PartialEq;
    
    fn id(&self) -> &Self::Id;
}

/// Marker trait for value objects
pub trait ValueObject: Send + Sync + Clone + PartialEq {}

/// Marker trait for domain events
pub trait DomainEvent: Send + Sync {
    fn event_type(&self) -> &str;
    fn occurred_at(&self) -> chrono::DateTime<chrono::Utc>;
}

/// Input port marker (commands/queries from outside)
pub trait InputPort: Send + Sync {}

/// Output port marker (calls to external systems)
pub trait OutputPort: Send + Sync {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hexagonal_error_display() {
        let err = HexagonalError::NotFound("Order 123".to_string());
        assert_eq!(format!("{}", err), "Not found: Order 123");
    }
}
