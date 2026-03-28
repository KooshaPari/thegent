//! CLI error types.

use core::fmt;

/// Error codes for CLI errors.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CliErrorCode {
    /// Argument parsing error.
    ParseError,
    /// Required argument missing.
    MissingRequired,
    /// Invalid argument value.
    InvalidValue,
    /// Argument not found.
    ArgumentNotFound,
    /// Subcommand not found.
    SubcommandNotFound,
    /// Command not found.
    CommandNotFound,
    /// IO error.
    IoError,
    /// User cancelled.
    Cancelled,
    /// Unknown error.
    Unknown,
}

impl CliErrorCode {
    /// Convert to string.
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::ParseError => "PARSE_ERROR",
            Self::MissingRequired => "MISSING_REQUIRED",
            Self::InvalidValue => "INVALID_VALUE",
            Self::ArgumentNotFound => "ARGUMENT_NOT_FOUND",
            Self::SubcommandNotFound => "SUBCOMMAND_NOT_FOUND",
            Self::CommandNotFound => "COMMAND_NOT_FOUND",
            Self::IoError => "IO_ERROR",
            Self::Cancelled => "CANCELLED",
            Self::Unknown => "UNKNOWN",
        }
    }
}

/// CLI error type.
#[derive(Debug)]
pub struct CliError {
    code: CliErrorCode,
    message: String,
    exit_code: i32,
    context: Vec<(String, String)>,
}

impl CliError {
    /// Create a new CLI error.
    pub fn new(code: CliErrorCode, message: impl Into<String>) -> Self {
        let exit_code = match code {
            CliErrorCode::ParseError => 1,
            CliErrorCode::MissingRequired => 2,
            CliErrorCode::InvalidValue => 3,
            CliErrorCode::ArgumentNotFound => 4,
            CliErrorCode::SubcommandNotFound => 5,
            CliErrorCode::CommandNotFound => 6,
            CliErrorCode::IoError => 7,
            CliErrorCode::Cancelled => 130,
            CliErrorCode::Unknown => 1,
        };
        
        Self {
            code,
            message: message.into(),
            exit_code,
            context: Vec::new(),
        }
    }

    /// Add context.
    #[must_use]
    pub fn with_context(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.context.push((key.into(), value.into()));
        self
    }

    /// Set exit code.
    #[must_use]
    pub fn exit_code(mut self, code: i32) -> Self {
        self.exit_code = code;
        self
    }

    /// Get error code.
    pub fn code(&self) -> CliErrorCode {
        self.code
    }

    /// Get exit code.
    pub fn exit_code(&self) -> i32 {
        self.exit_code
    }

    /// Get message.
    pub fn message(&self) -> &str {
        &self.message
    }

    /// Create a parse error.
    pub fn parse_error(message: impl Into<String>) -> Self {
        Self::new(CliErrorCode::ParseError, message)
    }

    /// Create a missing required argument error.
    pub fn missing_required(arg: &str) -> Self {
        Self::new(
            CliErrorCode::MissingRequired,
            format!("required argument '{}' is missing", arg),
        )
    }

    /// Create an invalid value error.
    pub fn invalid_value(arg: &str, value: &str, expected: Option<&str>) -> Self {
        let message = match expected {
            Some(e) => format!("invalid value '{}' for argument '{}': expected {}", value, arg, e),
            None => format!("invalid value '{}' for argument '{}'", value, arg),
        };
        Self::new(CliErrorCode::InvalidValue, message)
    }

    /// Create a command not found error.
    pub fn command_not_found(cmd: &str) -> Self {
        Self::new(
            CliErrorCode::CommandNotFound,
            format!("command '{}' not found", cmd),
        )
    }

    /// Create a subcommand not found error.
    pub fn subcommand_not_found(cmd: &str, subcmd: &str) -> Self {
        Self::new(
            CliErrorCode::SubcommandNotFound,
            format!("subcommand '{}' not found for command '{}'", subcmd, cmd),
        )
    }
}

impl fmt::Display for CliError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.code.as_str(), self.message)?;
        if !self.context.is_empty() {
            write!(f, " (")?;
            for (i, (k, v)) in self.context.iter().enumerate() {
                if i > 0 {
                    write!(f, ", ")?;
                }
                write!(f, "{}: {}", k, v)?;
            }
            write!(f, ")")?;
        }
        Ok(())
    }
}

impl core::error::Error for CliError {}
