//! # Application Layer
//!
//! Contains use cases and application services.
//!
//! ## CQRS Pattern
//!
//! - **Commands**: Operations that change state
//! - **Queries**: Operations that read state without side effects

pub mod commands;
pub mod queries;
pub mod use_cases;
