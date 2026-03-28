//! Domain layer - Pure validation concepts with ZERO external dependencies.

mod rule;
mod constraint;
mod error;
mod result;

pub use rule::ValidationRule;
pub use constraint::Constraint;
pub use error::ValidationError;
pub use result::{ValidationResult, Validated, ValidationStatus};
