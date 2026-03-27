//! ConsoleAdapter - Output logs to standard output/error.

use crate::domain::LogEntry;

/// Outputs log entries to console (stdout/stderr).
#[derive(Debug, Clone)]
pub struct ConsoleAdapter;

impl ConsoleAdapter {
    /// Create a new console adapter.
    pub fn new() -> Self {
        Self
    }

    /// Write a log entry to console.
    pub fn write(&self, entry: &LogEntry) {
        match entry.level {
            crate::domain::LogLevel::Error
            | crate::domain::LogLevel::Critical
            | crate::domain::LogLevel::Alert
            | crate::domain::LogLevel::Emergency => {
                eprintln!("[{}] {}", entry.level, entry.message);
            }
            _ => {
                println!("[{}] {}", entry.level, entry.message);
            }
        }
    }
}

impl Default for ConsoleAdapter {
    fn default() -> Self {
        Self::new()
    }
}
