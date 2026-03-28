//! Phenotype Validation Library
//!
//! A comprehensive validation library following:
//! - Hexagonal Architecture (Ports & Adapters)
//! - Clean Architecture principles
//! - xDD methodologies (TDD, BDD, DDD)

pub mod domain;
pub mod application;

pub use domain::*;
pub use application::*;

pub mod prelude {
    pub use crate::domain::*;
}
