//! # thegent-plugin-host
//!
//! Plugin host and loader for thegent agent system.
//!
//! ## Architecture
//!
//! This crate follows **Hexagonal Architecture** (Ports & Adapters) with **Clean Architecture** layers.
//!
//! ## xDD Methodologies Applied
//!
//! - **TDD**: Tests written first
//! - **DDD**: Bounded contexts for plugin management
//! - **SOLID**: Single responsibility per module
//! - **CQRS**: Separate command and query interfaces
//! - **EDA**: Domain events for state changes
//! - **SpecDD**: Formal specifications in `specs/` module

// Plugin host keeps hexagonal API modules ahead of adapter wiring.
#[allow(dead_code)]
pub mod domain;
#[allow(dead_code)]
pub mod application;
#[allow(dead_code)]
pub mod ports;
#[allow(dead_code)]
pub mod adapters;

// Re-exports for convenience
pub use domain::entities::*;
pub use domain::value_objects::*;
pub use domain::events::*;
pub use application::commands::*;
pub use application::queries::*;
pub use application::use_cases::*;
