//! Phenotype xDD Best Practices Library
//! 
//! A comprehensive library for implementing xDD (eXtreme Development Driven) methodologies.
//! 
//! ## Included Methodologies
//! 
//! - **TDD**: Test-Driven Development
//! - **BDD**: Behavior-Driven Development
//! - **SDD**: Specification-Driven Development
//! - **DDD**: Domain-Driven Design
//! - **ADD**: Attribute-Driven Design
//! - **CQRS**: Command Query Responsibility Segregation
//! - **Event Sourcing**: Store events, not state
//!
//! ## Quick Start
//! 
//! ```rust,ignore
//! use phenotype_xdd::tdd::*;
//! use phenotype_xdd::ddd::*;
//! 
//! // TDD: Red -> Green -> Refactor
//! #[test]
//! fn test_order_total_calculation() {
//!     let order = Order::new();
//!     order.add_item(Item::new("Widget", 10.00), 2);
//!     assert_eq!(order.total(), 20.00);
//! }
//! ```

pub mod tdd;
pub mod bdd;
pub mod sdd;
pub mod ddd;
pub mod add;
pub mod cqrs;
pub mod event_sourcing;

// Re-exports for convenience
pub use tdd::*;
pub use bdd::*;
pub use sdd::*;
pub use ddd::*;
pub use add::*;
pub use cqrs::*;
pub use event_sourcing::*;
