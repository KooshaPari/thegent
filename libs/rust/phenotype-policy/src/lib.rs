//! Phenotype Policy Engine
//!
//! A comprehensive policy evaluation library following:
//! - Hexagonal Architecture (Ports & Adapters)
//! - Clean Architecture principles
//! - Policy-as-Code principles
//! - xDD methodologies (TDD, BDD, DDD)
//!
//! # Architecture
//!
//! ```text
//! +------------------+
//! |   Domain Layer    |  <-- Pure policy concepts (NO deps)
//! |  - Policy        |
//! |  - Rule          |
//! |  - Effect        |
//! |  - Condition     |
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |  Application     |  <-- Policy engine
//! |  - Evaluator     |
//! |  - Compiler     |
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |   Adapters       |  <-- External integrations
//! |  - OPA           |
//! |  - SQL           |
//! |  - Redis        |
//! +------------------+
//! ```
//!
//! # Example
//!
//! ```rust
//! use phenotype_policy::{Policy, PolicyEngine, Context};
//!
//! let policy = Policy::new("allow-admin", Effect::Allow)
//!     .with_condition(|ctx| ctx.role == "admin");
//!
//! let engine = PolicyEngine::new();
//! let result = engine.evaluate(&policy, &context).unwrap();
//! assert!(result.is_allowed());
//! ```

pub mod domain;
pub mod application;
pub mod sdk;

pub use domain::*;
pub use application::*;

pub mod prelude {
    pub use crate::domain::*;
    pub use crate::application::*;
}
