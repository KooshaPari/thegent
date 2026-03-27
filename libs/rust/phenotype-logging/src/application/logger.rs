//! Logger - Core application service for structured logging.

use crate::domain::{LogContext, LogEntry, LogLevel};

/// Main logging service that processes log entries.
#[derive(Debug, Clone)]
pub struct Logger {
    #[allow(dead_code)]
    context: LogContext,
}

impl Logger {
    /// Create a new logger with given context.
    pub fn new(context: LogContext) -> Self {
        Self { context }
    }

    /// Log a message at the specified level.
    pub fn log(&self, message: impl Into<String>, level: LogLevel) {
        let entry = LogEntry::new(message, level);
        self.process_entry(entry);
    }

    /// Log at info level.
    pub fn info(&self, message: impl Into<String>) {
        self.log(message, LogLevel::Info);
    }

    /// Log at error level.
    pub fn error(&self, message: impl Into<String>) {
        self.log(message, LogLevel::Error);
    }

    /// Log at warning level.
    pub fn warn(&self, message: impl Into<String>) {
        self.log(message, LogLevel::Warning);
    }

    /// Log at debug level.
    pub fn debug(&self, message: impl Into<String>) {
        self.log(message, LogLevel::Debug);
    }

    fn process_entry(&self, entry: LogEntry) {
        // Placeholder for actual logging output
        // This will be implemented by adapters in the adapters layer
        let _ = entry;
    }
}
