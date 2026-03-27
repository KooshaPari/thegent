//! Phenotype Logging Library
//!
//! A comprehensive structured logging library following:
//! - Hexagonal Architecture (Ports & Adapters)
//! - Clean Architecture principles
//! - SOLID principles
//! - xDD methodologies (TDD, BDD, DDD)
//!
//! # Architecture
//!
//! ```text
//! +------------------+
//! |   Domain Layer   |  <-- Pure logging concepts (no external deps)
//! |  - LogLevel      |
//! |  - LogEntry      |
//! |  - LogContext    |
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |  Application     |  <-- Logging services
//! |  - Logger        |
//! |  - SpanBuilder   |
//! +------------------+
//!          |
//!          v
//! +------------------+
//! |   Adapters       |  <-- Output adapters
//! |  - Console       |
//! |  - File          |
//! |  - Json          |
//! +------------------+
//! ```
//!
//! # Usage
//!
//! ```rust
//! use phenotype_logging::{LogContext, Logger};
//!
//! let ctx = LogContext::new("my-service")
//!     .with_field("request_id", "12345");
//!
//! let logger = Logger::new(ctx);
//! logger.info("Processing request");
//! logger.error("Failed to process");
//! ```

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
