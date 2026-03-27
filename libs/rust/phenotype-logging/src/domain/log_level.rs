//! LogLevel - Domain concept for log severity levels.
//!
//! Pure domain type with no external dependencies.

use std::fmt;

/// Log severity levels following RFC 5424 syslog conventions.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum LogLevel {
    /// System is unusable - emergency level
    Emergency,
    /// Action must be taken immediately - alert level
    Alert,
    /// Critical conditions - critical level
    Critical,
    /// Error conditions - error level
    Error,
    /// Warning conditions - warning level
    Warning,
    /// Normal but significant conditions - notice level
    Notice,
    /// Informational - info level
    Info,
    /// Debug-level messages - debug level
    Debug,
    /// Trace-level messages - lowest priority
    Trace,
}

impl LogLevel {
    /// Convert LogLevel to numeric syslog value (RFC 5424).
    pub fn to_syslog(&self) -> u8 {
        match self {
            LogLevel::Emergency => 0,
            LogLevel::Alert => 1,
            LogLevel::Critical => 2,
            LogLevel::Error => 3,
            LogLevel::Warning => 4,
            LogLevel::Notice => 5,
            LogLevel::Info => 6,
            LogLevel::Debug => 7,
            LogLevel::Trace => 8,
        }
    }

    /// Parse LogLevel from string.
    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "emergency" | "emerg" => Some(LogLevel::Emergency),
            "alert" => Some(LogLevel::Alert),
            "critical" | "crit" => Some(LogLevel::Critical),
            "error" | "err" => Some(LogLevel::Error),
            "warning" | "warn" => Some(LogLevel::Warning),
            "notice" => Some(LogLevel::Notice),
            "info" | "information" => Some(LogLevel::Info),
            "debug" | "dbg" => Some(LogLevel::Debug),
            "trace" | "trce" => Some(LogLevel::Trace),
            _ => None,
        }
    }

    /// Check if this level should be logged based on minimum level.
    /// Returns true if this level's severity is at or above the minimum level.
    pub fn should_log(&self, min_level: LogLevel) -> bool {
        *self <= min_level
    }
}

impl Default for LogLevel {
    fn default() -> Self {
        LogLevel::Info
    }
}

impl fmt::Display for LogLevel {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            LogLevel::Emergency => write!(f, "EMERGENCY"),
            LogLevel::Alert => write!(f, "ALERT"),
            LogLevel::Critical => write!(f, "CRITICAL"),
            LogLevel::Error => write!(f, "ERROR"),
            LogLevel::Warning => write!(f, "WARNING"),
            LogLevel::Notice => write!(f, "NOTICE"),
            LogLevel::Info => write!(f, "INFO"),
            LogLevel::Debug => write!(f, "DEBUG"),
            LogLevel::Trace => write!(f, "TRACE"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_log_level_ordering() {
        assert!(LogLevel::Error < LogLevel::Warning);
        assert!(LogLevel::Info < LogLevel::Debug);
        assert!(LogLevel::Trace >= LogLevel::Debug);
    }

    #[test]
    fn test_syslog_conversion() {
        assert_eq!(LogLevel::Error.to_syslog(), 3);
        assert_eq!(LogLevel::Info.to_syslog(), 6);
    }

    #[test]
    fn test_parse_from_string() {
        assert_eq!(LogLevel::from_str("error"), Some(LogLevel::Error));
        assert_eq!(LogLevel::from_str("WARN"), Some(LogLevel::Warning));
        assert_eq!(LogLevel::from_str("invalid"), None);
    }

    #[test]
    fn test_should_log() {
        assert!(LogLevel::Error.should_log(LogLevel::Warning));
        assert!(!LogLevel::Debug.should_log(LogLevel::Warning));
    }
}
