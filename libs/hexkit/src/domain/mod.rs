//! Domain Layer - Core Business Logic
//!
//! The domain layer contains pure business logic with no external dependencies.

pub mod entity;
pub mod value_object;
pub mod aggregate;
pub mod event;
pub mod service;

// Re-exports for convenience
pub use entity::{Entity, EntityId};
pub use value_object::{ValueObject, ValueObjectError};
pub use aggregate::AggregateRoot;
pub use event::DomainEvent;
pub use service::DomainService;
