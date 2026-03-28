//! Command runner for CLI applications.

use crate::domain::{CliContext, CliError, Command};

/// Command handler function type.
pub type CommandHandler = fn(ctx: &CliContext) -> Result<(), CliError>;

/// Command runner for executing CLI commands.
#[derive(Debug)]
pub struct CommandRunner {
    commands: Vec<Command>,
}

impl CommandRunner {
    /// Create a new command runner.
    pub fn new() -> Self {
        Self {
            commands: Vec::new(),
        }
    }

    /// Add a command.
    pub fn command(mut self, cmd: Command) -> Self {
        self.commands.push(cmd);
        self
    }

    /// Run a command by name.
    pub fn run(&self, name: &str, ctx: &CliContext) -> Result<(), CliError> {
        self.commands
            .iter()
            .find(|c| c.name() == name)
            .ok_or_else(|| CliError::command_not_found(name))?;
        
        Ok(())
    }

    /// Get all commands.
    pub fn commands(&self) -> &[Command] {
        &self.commands
    }
}

impl Default for CommandRunner {
    fn default() -> Self {
        Self::new()
    }
}
