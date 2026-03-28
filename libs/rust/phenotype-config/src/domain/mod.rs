//! Domain layer - Pure configuration concepts with ZERO external dependencies.
//!
//! Following ADR-001 dependency rule:
//! - domain/ contains ZERO external dependencies
//! - Only Rust standard library allowed

pub mod config_value;
pub mod config_error;
pub mod config_source;

pub use config_value::*;
pub use config_error::*;
pub use config_source::*;
