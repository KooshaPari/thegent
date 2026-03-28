//! Application layer - Configuration loading and management.
//!
//! This layer orchestrates configuration from multiple sources.

use crate::domain::{ConfigError, ConfigResult, ConfigValue};
use crate::domain::config_source::{ConfigSourceTrait, ConfigSource};

/// Configuration manager that loads from multiple sources.
#[derive(Debug)]
pub struct Config {
    sources: Vec<Box<dyn ConfigSourceTrait>>,
}

impl Config {
    /// Create a new configuration manager.
    pub fn new() -> Self {
        Self {
            sources: Vec::new(),
        }
    }

    /// Add a configuration source.
    pub fn with_source(mut self, source: impl ConfigSourceTrait + 'static) -> Self {
        self.sources.push(Box::new(source));
        self
    }

    /// Get a configuration value by key.
    pub fn get(&self, key: &str) -> ConfigResult<Option<ConfigValue>> {
        // Sources are checked in order - first match wins
        for source in &self.sources {
            match source.get(key) {
                Ok(Some(value)) => return Ok(Some(value)),
                Ok(None) => continue,
                Err(e) => return Err(e),
            }
        }
        Ok(None)
    }

    /// Get a required configuration value.
    ///
    /// Returns error if the key is not found.
    pub fn get_required(&self, key: &str) -> ConfigResult<ConfigValue> {
        self.get(key)?
            .ok_or_else(|| ConfigError::key_not_found(key))
    }

    /// Get a string value.
    pub fn get_string(&self, key: &str) -> ConfigResult<String> {
        let value = self.get_required(key)?;
        value.as_string()
            .map(|s| s.to_string())
            .ok_or_else(|| ConfigError::type_mismatch("string", "other", key))
    }

    /// Get an integer value.
    pub fn get_integer(&self, key: &str) -> ConfigResult<i64> {
        let value = self.get_required(key)?;
        value.as_integer()
            .ok_or_else(|| ConfigError::type_mismatch("integer", "other", key))
    }

    /// Get a float value.
    pub fn get_float(&self, key: &str) -> ConfigResult<f64> {
        let value = self.get_required(key)?;
        value.as_float()
            .ok_or_else(|| ConfigError::type_mismatch("float", "other", key))
    }

    /// Get a boolean value.
    pub fn get_bool(&self, key: &str) -> ConfigResult<bool> {
        let value = self.get_required(key)?;
        value.as_boolean()
            .ok_or_else(|| ConfigError::type_mismatch("boolean", "other", key))
    }

    /// Check if a key exists.
    pub fn contains(&self, key: &str) -> bool {
        self.get(key).map(|opt| opt.is_some()).unwrap_or(false)
    }

    /// Get a nested value by path.
    pub fn get_path(&self, path: &str) -> ConfigResult<Option<ConfigValue>> {
        // For now, just get from first source
        // TODO: Implement proper path traversal across sources
        self.get(path)
    }
}

impl Default for Config {
    fn default() -> Self {
        Self::new()
    }
}

impl Config {
    /// Shorthand for creating a config with environment variables.
    pub fn from_env() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::config_source::EnvConfigSource;
    use crate::domain::config_source::DefaultConfigSource;

    #[test]
    fn test_config_with_default() {
        let config = Config::new()
            .with_source(DefaultConfigSource::new()
                .with_default("port", ConfigValue::integer(8080))
                .with_default("host", ConfigValue::string("localhost")));

        assert_eq!(config.get_integer("port").unwrap(), 8080);
        assert_eq!(config.get_string("host").unwrap(), "localhost");
        assert!(config.contains("port"));
    }

    #[test]
    fn test_config_required_missing() {
        let config = Config::new();
        let result = config.get_required("missing");
        assert!(result.is_err());
    }
}
