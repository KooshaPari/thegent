//! Application layer - Error handling utilities.
//!
//! This layer provides utilities for working with errors
//! at the application level.

mod result;
mod error_builder;

pub use result::Result;
pub use error_builder::ErrorBuilder;
