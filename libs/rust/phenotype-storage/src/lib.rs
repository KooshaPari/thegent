//! Phenotype Storage Library
//!
//! A comprehensive storage abstraction library following:
//! - Hexagonal Architecture (Ports & Adapters)
//! - Clean Architecture principles
//! - Repository Pattern
//! - Unit of Work Pattern
//!
//! # Architecture
//!
//! ```text
//! +------------------+
//! |   Domain Layer    |  <-- Entities, Value Objects (NO deps)
//! |  - Repository    |      Ports (interfaces)
//! |  - UnitOfWork    |
//! |  - Aggregate     |
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |  Application     |  <-- Use Cases
//! |  - TxManager     |      Repository implementations
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |   Adapters       |  <-- Infrastructure
//! |  - Postgres      |      In-memory, Redis, etc.
//! |  - MongoDB       |
//! |  - DynamoDB      |
//! +------------------+
//! ```

pub mod domain;
pub mod application;
pub mod adapters;

pub use domain::*;
pub use application::*;

pub mod prelude {
    pub use crate::domain::*;
    pub use crate::application::*;
}
