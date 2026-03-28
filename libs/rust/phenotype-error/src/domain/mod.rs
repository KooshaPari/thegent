//! Domain layer - Pure error types with ZERO external dependencies.
//!
//! Following ADR-001 dependency rule:
//! - domain/ contains ZERO external dependencies
//! - Only Rust standard library allowed

pub mod app_error;
pub mod error_code;
pub mod error_kind;
pub mod error_context;

pub use app_error::AppError;
pub use error_code::ErrorCode;
pub use error_kind::ErrorKind;
pub use error_context::ErrorContext;
