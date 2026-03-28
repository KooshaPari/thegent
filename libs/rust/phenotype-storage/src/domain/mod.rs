//! Domain layer - Pure storage concepts with ZERO external dependencies.
//!
//! Following ADR-001 dependency rule:
//! - domain/ contains ZERO external dependencies
//! - Only Rust standard library + async-trait allowed

mod repository;
mod aggregate_root;
mod entity;
mod error;
mod value_objects;

pub use repository::*;
pub use aggregate_root::*;
pub use entity::*;
pub use error::*;
pub use value_objects::*;
