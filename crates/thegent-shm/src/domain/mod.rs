//! # Domain Layer
//!
//! Contains core business logic with no external dependencies.
//!
//! ## DDD Principles Applied
//!
//! - **Entities**: Objects with identity (CircuitBreaker, CommandLock)
//! - **Value Objects**: Immutable objects defined by attributes (CircuitState, LockStatus)
//! - **Domain Events**: Immutable events representing state changes

pub mod entities;
pub mod value_objects;
pub mod events;
