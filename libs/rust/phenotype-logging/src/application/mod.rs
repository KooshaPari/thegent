//! Application layer - Logging services and use cases.
//!
//! This layer implements the core logging services using domain concepts.
//! It orchestrates domain objects and may use external dependencies (tracing, etc).

pub mod logger;

pub use logger::Logger;
