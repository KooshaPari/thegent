//! CLI context for command execution.

use crate::domain::argument::ArgValue;
use core::fmt;

/// CLI context passed to command handlers.
#[derive(Debug)]
pub struct CliContext {
    values: std::collections::HashMap<String, ArgValue>,
    flags: std::collections::HashMap<String, bool>,
    positional: Vec<ArgValue>,
}

impl CliContext {
    /// Create a new CLI context.
    pub fn new() -> Self {
        Self {
            values: std::collections::HashMap::new(),
            flags: std::collections::HashMap::new(),
            positional: Vec::new(),
        }
    }

    /// Set a value.
    pub fn set(&mut self, name: &str, value: ArgValue) {
        self.values.insert(name.to_string(), value);
    }

    /// Set a flag.
    pub fn set_flag(&mut self, name: &str, value: bool) {
        self.flags.insert(name.to_string(), value);
    }

    /// Add a positional argument.
    pub fn add_positional(&mut self, value: ArgValue) {
        self.positional.push(value);
    }

    /// Get a string value.
    pub fn get_string(&self, name: &str) -> Option<&str> {
        self.values.get(name)
            .and_then(|v| v.as_str())
    }

    /// Get an integer value.
    pub fn get_integer(&self, name: &str) -> Option<i64> {
        self.values.get(name)
            .and_then(|v| v.as_integer())
    }

    /// Get a float value.
    pub fn get_float(&self, name: &str) -> Option<f64> {
        self.values.get(name)
            .and_then(|v| v.as_float())
    }

    /// Get a boolean value.
    pub fn get_bool(&self, name: &str) -> bool {
        self.flags.get(name).copied().unwrap_or(false)
    }

    /// Get positional argument by index.
    pub fn get_positional(&self, index: usize) -> Option<&ArgValue> {
        self.positional.get(index)
    }

    /// Get all positional arguments.
    pub fn positional_args(&self) -> &[ArgValue] {
        &self.positional
    }

    /// Check if a flag is set.
    pub fn is_flag_set(&self, name: &str) -> bool {
        self.flags.get(name).copied().unwrap_or(false)
    }
}

impl Default for CliContext {
    fn default() -> Self {
        Self::new()
    }
}

impl fmt::Debug for CliContext {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("CliContext")
            .field("values", &self.values)
            .field("flags", &self.flags)
            .field("positional", &self.positional)
            .finish()
    }
}
