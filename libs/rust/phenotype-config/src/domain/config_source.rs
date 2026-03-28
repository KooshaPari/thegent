//! Configuration source types.
//!
//! This module defines where configuration values come from.

use crate::domain::{ConfigError, ConfigResult, ConfigValue};

/// Represents a source of configuration values.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ConfigSource {
    /// Environment variables (ENV_VAR_NAME)
    Environment,
    /// Command line arguments (--arg-name)
    CommandLine,
    /// JSON file
    Json(&'static str),
    /// YAML file
    Yaml(&'static str),
    /// TOML file
    Toml(&'static str),
    /// Environment-specific file (.env, .env.local, etc.)
    EnvFile(&'static str),
    /// Default value
    Default,
    /// Unknown source
    Unknown,
}

impl ConfigSource {
    /// Get the source name for debugging.
    pub fn name(&self) -> &'static str {
        match self {
            Self::Environment => "environment",
            Self::CommandLine => "command_line",
            Self::Json(path) => path,
            Self::Yaml(path) => path,
            Self::Toml(path) => path,
            Self::EnvFile(path) => path,
            Self::Default => "default",
            Self::Unknown => "unknown",
        }
    }
}

/// Trait for configuration sources.
///
/// Implement this trait to add new configuration sources.
pub trait ConfigSourceTrait: Send + Sync {
    /// Get a configuration value by key.
    fn get(&self, key: &str) -> ConfigResult<Option<ConfigValue>>;

    /// Check if a key exists.
    fn contains(&self, key: &str) -> bool {
        self.get(key).map(|opt| opt.is_some()).unwrap_or(false)
    }
}

/// Environment variable configuration source.
#[derive(Debug, Clone)]
pub struct EnvConfigSource {
    prefix: Option<String>,
}

impl EnvConfigSource {
    /// Create a new environment configuration source.
    pub fn new() -> Self {
        Self { prefix: None }
    }

    /// Create with a prefix (e.g., "APP_" for APP_DATABASE_URL).
    pub fn with_prefix(prefix: impl Into<String>) -> Self {
        Self {
            prefix: Some(prefix.into()),
        }
    }

    /// Convert a config key to an environment variable name.
    fn to_env_key(key: &str, prefix: &Option<String>) -> String {
        let key = key.replace('.', "_").replace('-', "_").to_uppercase();
        match prefix {
            Some(p) => format!("{}_{}", p, key),
            None => key,
        }
    }
}

impl Default for EnvConfigSource {
    fn default() -> Self {
        Self::new()
    }
}

impl ConfigSourceTrait for EnvConfigSource {
    fn get(&self, key: &str) -> ConfigResult<Option<ConfigValue>> {
        let env_key = Self::to_env_key(key, &self.prefix);

        match std::env::var(&env_key) {
            Ok(value) => Ok(Some(ConfigValue::string(value))),
            Err(std::env::VarError::NotPresent) => Ok(None),
            Err(e) => Err(ConfigError::new(crate::domain::ConfigErrorCode::IoError, e)),
        }
    }
}

/// Default configuration source.
#[derive(Debug, Clone)]
pub struct DefaultConfigSource {
    defaults: Vec<(String, ConfigValue)>,
}

impl DefaultConfigSource {
    /// Create a new default configuration source.
    pub fn new() -> Self {
        Self {
            defaults: Vec::new(),
        }
    }

    /// Add a default value.
    pub fn with_default(mut self, key: impl Into<String>, value: ConfigValue) -> Self {
        self.defaults.push((key.into(), value));
        self
    }

    /// Add multiple default values.
    pub fn with_defaults(mut self, defaults: impl IntoIterator<Item = (String, ConfigValue)>) -> Self {
        self.defaults.extend(defaults);
        self
    }
}

impl Default for DefaultConfigSource {
    fn default() -> Self {
        Self::new()
    }
}

impl ConfigSourceTrait for DefaultConfigSource {
    fn get(&self, key: &str) -> ConfigResult<Option<ConfigValue>> {
        Ok(self.defaults.iter().find(|(k, _)| k == key).map(|(_, v)| v.clone()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_env_config_source_default() {
        let source = EnvConfigSource::new();
        let env_key = source.to_env_key("database.host", &None);
        assert_eq!(env_key, "DATABASE_HOST");
    }

    #[test]
    fn test_env_config_source_with_prefix() {
        let source = EnvConfigSource::with_prefix("APP");
        let env_key = source.to_env_key("database.host", &source.prefix);
        assert_eq!(env_key, "APP_DATABASE_HOST");
    }

    #[test]
    fn test_default_config_source() {
        let source = DefaultConfigSource::new()
            .with_default("port", ConfigValue::integer(8080))
            .with_default("host", ConfigValue::string("localhost"));

        assert_eq!(
            source.get("port").unwrap(),
            Some(ConfigValue::integer(8080))
        );
        assert_eq!(
            source.get("host").unwrap(),
            Some(ConfigValue::string("localhost"))
        );
        assert_eq!(source.get("missing").unwrap(), None);
    }
}
