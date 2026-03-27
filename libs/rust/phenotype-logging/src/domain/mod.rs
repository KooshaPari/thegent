//! Domain layer - Pure logging concepts with ZERO external dependencies.
//!
//! Following ADR-001 dependency rule:
//! - domain/ contains ZERO external dependencies
//! - Only Rust standard library allowed

mod log_level;
mod log_entry;
mod log_context;
mod log_metadata;

pub use log_level::LogLevel;
pub use log_entry::LogEntry;
pub use log_context::LogContext;
pub use log_metadata::LogMetadata;
