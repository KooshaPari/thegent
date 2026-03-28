//! Phenotype Clean Architecture Library
//! 
//! A framework for building applications following Clean Architecture principles.
//!
//! ## Architecture Layers
//! 
//! 1. **Enterprise Business Rules**: Entities, business rules
//! 2. **Application Business Rules**: Use cases, interactors
//! 3. **Interface Adapters**: Controllers, presenters, gateways
//! 4. **Frameworks & Drivers**: Database, web, external interfaces
//!
//! ## Dependency Rule
//! 
//! Source code dependencies only point inward.
//! Outer layers depend on inner layers, never the reverse.

pub mod enterprise_rules;
pub mod application;
pub mod interface_adapters;
pub mod frameworks_drivers;

pub use enterprise_rules::*;
pub use application::*;
pub use interface_adapters::*;
pub use frameworks_drivers::*;
