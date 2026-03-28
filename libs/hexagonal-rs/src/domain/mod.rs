//! Domain layer - Pure business logic with no external dependencies
//!
//! This layer contains:
//! - Entities: Objects with identity
//! - Value Objects: Objects without identity, immutable
//! - Aggregates: Clusters of related entities
//! - Domain Events: Significant business occurrences
//! - Domain Services: Operations that don't belong to a single entity

pub mod entity;
pub mod value_object;
pub mod aggregate;
pub mod event;
pub mod service;

pub use entity::*;
pub use value_object::*;
pub use aggregate::*;
pub use event::*;
pub use service::*;
