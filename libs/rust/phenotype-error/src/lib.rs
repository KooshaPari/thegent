//! Phenotype Error Library
//!
//! A comprehensive error handling library following:
//! - Hexagonal Architecture (Ports & Adapters)
//! - Clean Architecture principles
//! - SOLID principles
//! - xDD methodologies (TDD, BDD, DDD)
//!
//! # Architecture
//!
//! ```text
//! +------------------+
//! |   Domain Layer   |  <-- Pure error types (no deps)
//! |  - AppError      |
//! |  - ErrorCode     |
//! |  - ErrorKind     |
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |  Application     |  <-- Error services
//! |  - Result        |
//! |  - ErrorContext  |
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |   Adapters       |  <-- Error adapters
//! |  - AnyhowAdapter |
//! |  - ThisErrorAdapter |
//! +------------------+
//! ```
//!
//! # Usage
//!
//! ```rust
//! use phenotype_error::{AppError, ErrorCode, Result, Ok, Err};
//!
//! fn divide(a: i32, b: i32) -> Result<i32, AppError> {
//!     if b == 0 {
//!         return Err(AppError::new(
//!             ErrorCode::DivisionByZero,
//!             "Cannot divide by zero",
//!         ));
//!     }
//!     Ok(a / b)
//! }
//! ```

#![forbid(unsafe_code)]
#![warn(missing_docs, missing_debug_implementations)]
#![deny(rust_2018_idioms)]

pub mod domain;
pub mod application;
pub mod adapters;

pub use domain::*;
pub use application::*;
pub use adapters::*;

pub mod prelude {
    pub use crate::domain::*;
    pub use crate::application::*;
}
