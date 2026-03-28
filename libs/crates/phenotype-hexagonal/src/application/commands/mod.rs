//! Application Commands
//! 
//! Commands represent operations that modify state.

/// Marker trait for commands
pub trait Command: Send + Sync {
    // Commands carry the data needed to perform an operation
}

/// Command result type
pub type CommandResult<T> = Result<T, CommandError>;

/// Command error type
#[derive(Debug)]
pub struct CommandError {
    pub code: String,
    pub message: String,
}

impl CommandError {
    pub fn new(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            message: message.into(),
        }
    }
}

impl std::fmt::Display for CommandError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

impl std::error::Error for CommandError {}
