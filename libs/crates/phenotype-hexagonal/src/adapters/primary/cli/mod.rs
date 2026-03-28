//! CLI Adapter
//! 
//! Command-line interface adapter implementation.

/// CLI command trait
pub trait CliCommand: Send + Sync {
    /// Command name
    fn name(&self) -> &str;
    
    /// Command description
    fn description(&self) -> &str;
    
    /// Execute the command
    fn execute(&self, args: Vec<String>) -> Result<(), CliError>;
}

/// CLI error type
#[derive(Debug)]
pub struct CliError {
    pub message: String,
}

impl CliError {
    pub fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }
}

impl std::fmt::Display for CliError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "CLI Error: {}", self.message)
    }
}

impl std::error::Error for CliError {}
