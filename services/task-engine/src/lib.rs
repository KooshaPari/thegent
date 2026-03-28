//! Phenotype Task Engine
//!
//! Task planning and execution scheduler following:
//! - Hexagonal Architecture
//! - Clean Architecture
//! - xDD methodologies

pub mod domain;
pub mod application;
pub mod adapters;

pub use domain::*;
pub use application::*;

pub mod prelude {
    pub use crate::domain::*;
}
