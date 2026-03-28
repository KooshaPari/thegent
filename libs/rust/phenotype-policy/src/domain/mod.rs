//! Domain layer - Pure policy concepts with ZERO external dependencies.
//!
//! Following ADR-001 dependency rule:
//! - domain/ contains ZERO external dependencies
//! - Only Rust standard library allowed

mod effect;
mod condition;
mod policy;
mod rule;
mod context;
mod result;
mod error;

pub use effect::Effect;
pub use condition::Condition;
pub use policy::Policy;
pub use rule::Rule;
pub use context::PolicyContext;
pub use result::{EvaluationResult, Decision};
pub use error::{PolicyError, PolicyResult};
