// Phenotype Shared Logging Interface
//
// This module defines the shared logging interface for all Phenotype ecosystem crates.
// Implementations should provide structured logging with correlation ID support.

pub use log::{debug, error, info, trace, warn, Level, LevelFilter, Metadata, Record};

/// Configuration for a logger implementation
#[derive(Debug, Clone)]
pub struct LoggerConfig {
    /// Minimum log level to capture
    pub level: Level,
    /// Include timestamps in logs
    pub include_timestamps: bool,
    /// Include file and line information
    pub include_location: bool,
    /// Correlation ID for tracing requests
    pub correlation_id: Option<String>,
}

impl Default for LoggerConfig {
    fn default() -> Self {
        Self {
            level: Level::Info,
            include_timestamps: true,
            include_location: true,
            correlation_id: None,
        }
    }
}

/// Initialize a logger with the given configuration
pub fn init(config: LoggerConfig);

/// Structured logging macro for JSON-formatted logs
#[macro_export]
macro_rules! log_json {
    ($level:expr, $($key:tt = $value:expr),+ $(,)?) => {
        {
            use serde_json::json;
            let obj = json!({ $($key: $value),+ });
            log::log!($level, "{}", obj);
        }
    };
}

/// Context wrapper for correlation ID tracking
pub struct LogContext {
    pub correlation_id: String,
}

impl LogContext {
    pub fn new(id: Option<String>) -> Self {
        Self {
            correlation_id: id.unwrap_or_else(|| uuid::Uuid::new_v4().to_string()),
        }
    }
}

/// Trait for logging backends
pub trait LoggingBackend: Send + Sync {
    fn log(&self, level: Level, message: &str, metadata: Option<&LogMetadata>) -> Result<(), LogError>;
}

/// Metadata attached to log entries
#[derive(Debug, Clone)]
pub struct LogMetadata {
    pub correlation_id: Option<String>,
    pub user_id: Option<String>,
    pub request_id: Option<String>,
    pub span_id: Option<String>,
}

/// Error type for logging operations
#[derive(Debug)]
pub enum LogError {
    BackendError(String),
    SerializationError(String),
    IoError(String),
}

impl std::fmt::Display for LogError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            LogError::BackendError(s) => write!(f, "Backend error: {}", s),
            LogError::SerializationError(s) => write!(f, "Serialization error: {}", s),
            LogError::IoError(s) => write!(f, "IO error: {}", s),
        }
    }
}

impl std::error::Error for LogError {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_logger_config_default() {
        let config = LoggerConfig::default();
        assert_eq!(config.level, Level::Info);
        assert!(config.include_timestamps);
        assert!(config.include_location);
    }

    #[test]
    fn test_log_context_generation() {
        let ctx = LogContext::new(None);
        assert!(!ctx.correlation_id.is_empty());
    }

    #[test]
    fn test_log_context_with_id() {
        let ctx = LogContext::new(Some("test-123".to_string()));
        assert_eq!(ctx.correlation_id, "test-123");
    }
}
