//! Logging integration for errors

use crate::Error;
use log::{Level, Record};

/// Error log format
pub struct ErrorLog;

impl ErrorLog {
    /// Log an error with full context
    pub fn log(error: &Error, level: Level) {
        let ctx: Vec<String> = error.context()
            .iter()
            .map(|c| format!("{}={:?}", c.key, c.value))
            .collect();

        let ctx_str = if ctx.is_empty() {
            String::new()
        } else {
            format!(" [{}]", ctx.join(", "))
        };

        let msg = format!(
            "[{}] {}: {}{}",
            error.code(),
            error.kind().code(),
            error.message(),
            ctx_str
        );

        // Use logging facade
        log::logger().log(&Record::builder()
            .args(format_args!("{}", msg))
            .level(level)
            .target("helix_errors")
            .build());
    }
}

impl Default for ErrorLog {
    fn default() -> Self {
        Self
    }
}
