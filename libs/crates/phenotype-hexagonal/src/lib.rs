//! Phenotype Hexagonal Architecture Library
//! 
//! A framework for building applications following Hexagonal Architecture
//! (Ports & Adapters) principles.
//!
//! ## Core Principles
//! 
//! 1. **Domain Core**: Pure business logic with no external dependencies
//! 2. **Ports**: Interfaces that define boundaries
//! 3. **Adapters**: Implementations of ports
//!
//! ## Modules
//! 
//! - `domain`: Core domain logic (entities, value objects, services, events, ports)
//! - `application`: Use cases and command/query handlers
//! - `adapters`: Implementations of ports
//! - `infrastructure`: Configuration and wiring

pub mod domain;
pub mod application;
pub mod adapters;
pub mod infrastructure;

pub use domain::*;
