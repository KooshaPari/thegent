//! Command types for CLI applications.

use crate::domain::argument::Argument;
use core::fmt;

/// Command for CLI applications.
///
/// A command represents a single action that can be performed by the CLI.
/// Commands can have arguments, options, and subcommands.
#[derive(Debug, Clone)]
pub struct Command {
    name: String,
    about: Option<String>,
    long_about: Option<String>,
    version: Option<String>,
    args: Vec<Argument>,
    subcommands: Vec<Command>,
    examples: Vec<Example>,
    aliases: Vec<String>,
    hidden: bool,
}

impl Command {
    /// Create a new command.
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            about: None,
            long_about: None,
            version: None,
            args: Vec::new(),
            subcommands: Vec::new(),
            examples: Vec::new(),
            aliases: Vec::new(),
            hidden: false,
        }
    }

    /// Set the short description.
    pub fn about(mut self, about: impl Into<String>) -> Self {
        self.about = Some(about.into());
        self
    }

    /// Set the long description.
    pub fn long_about(mut self, about: impl Into<String>) -> Self {
        self.long_about = Some(about.into());
        self
    }

    /// Set the version.
    pub fn version(mut self, version: impl Into<String>) -> Self {
        self.version = Some(version.into());
        self
    }

    /// Add an argument.
    pub fn arg(mut self, arg: Argument) -> Self {
        self.args.push(arg);
        self
    }

    /// Add multiple arguments.
    pub fn args(mut self, args: impl IntoIterator<Item = Argument>) -> Self {
        self.args.extend(args);
        self
    }

    /// Add a subcommand.
    pub fn subcommand(mut self, subcommand: Command) -> Self {
        self.subcommands.push(subcommand);
        self
    }

    /// Add an example.
    pub fn example(mut self, example: Example) -> Self {
        self.examples.push(example);
        self
    }

    /// Add an alias.
    pub fn alias(mut self, alias: impl Into<String>) -> Self {
        self.aliases.push(alias.into());
        self
    }

    /// Hide the command from help.
    pub fn hidden(mut self) -> Self {
        self.hidden = true;
        self
    }

    /// Get the command name.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Get the short description.
    pub fn about(&self) -> Option<&str> {
        self.about.as_deref()
    }

    /// Get the long description.
    pub fn long_about(&self) -> Option<&str> {
        self.long_about.as_deref()
    }

    /// Get the version.
    pub fn version(&self) -> Option<&str> {
        self.version.as_deref()
    }

    /// Get arguments.
    pub fn args(&self) -> &[Argument] {
        &self.args
    }

    /// Get subcommands.
    pub fn subcommands(&self) -> &[Command] {
        &self.subcommands
    }

    /// Get examples.
    pub fn examples(&self) -> &[Example] {
        &self.examples
    }

    /// Get aliases.
    pub fn aliases(&self) -> &[String] {
        &self.aliases
    }

    /// Check if hidden.
    pub fn is_hidden(&self) -> bool {
        self.hidden
    }

    /// Check if command has subcommands.
    pub fn has_subcommands(&self) -> bool {
        !self.subcommands.is_empty()
    }
}

/// Example usage of a command.
#[derive(Debug, Clone)]
pub struct Example {
    description: String,
    command: String,
    output: Option<String>,
}

impl Example {
    /// Create a new example.
    pub fn new(description: impl Into<String>, command: impl Into<String>) -> Self {
        Self {
            description: description.into(),
            command: command.into(),
            output: None,
        }
    }

    /// Set the expected output.
    pub fn output(mut self, output: impl Into<String>) -> Self {
        self.output = Some(output.into());
        self
    }

    /// Get description.
    pub fn description(&self) -> &str {
        &self.description
    }

    /// Get command.
    pub fn command(&self) -> &str {
        &self.command
    }

    /// Get output.
    pub fn output(&self) -> Option<&str> {
        self.output.as_deref()
    }
}

impl fmt::Display for Command {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.name)?;
        if let Some(version) = &self.version {
            write!(f, " v{}", version)?;
        }
        if let Some(about) = &self.about {
            write!(f, "\n  {}", about)?;
        }
        Ok(())
    }
}
