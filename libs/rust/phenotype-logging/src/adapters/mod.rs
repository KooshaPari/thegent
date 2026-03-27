//! Adapters layer - Output adapters for log entries.
//!
//! This layer provides concrete implementations for outputting logs
//! (console, file, JSON, etc.) using external dependencies like tracing.

pub mod console;

pub use console::ConsoleAdapter;
