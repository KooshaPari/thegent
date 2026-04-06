//! # thegent-subprocess
//!
//! Subprocess management with hexagonal architecture.
//!
//! ## Architecture
//!
//! This crate follows **Hexagonal Architecture** (Ports & Adapters) with **Clean Architecture** layers.
//!
//! ## xDD Methodologies Applied
//!
//! - **TDD**: Tests written first in `tests/`
//! - **DDD**: Bounded contexts for process management
//! - **SOLID**: Single responsibility per module
//! - **CQRS**: Separate command and query interfaces
//! - **EDA**: Domain events for state changes

pub mod domain;
pub mod application;
pub mod ports;
pub mod adapters;
pub mod cli;

// Re-exports for convenience
pub use domain::entities::*;
pub use domain::value_objects::*;
pub use domain::events::*;
pub use ports::driven::ProcessExecutorPort;
pub use ports::driven::ProcessRegistryPort;
pub use cli::Commands;
