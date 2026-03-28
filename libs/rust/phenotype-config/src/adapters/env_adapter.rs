//! Environment variable adapter.
//!
//! This adapter loads configuration from environment variables.

use crate::domain::config_source::{ConfigSourceTrait, ConfigSource};
use crate::domain::{ConfigError, ConfigResult, ConfigValue};

/// Environment variable configuration adapter.
#[derive(Debug, Clone)]
pub struct EnvAdapter {
    prefix: Option<String>,
    separator: String,
}

impl EnvAdapter {
    /// Create a new environment adapter.
    pub fn new() -> Self {
        Self {
            prefix: None,
            separator: "_".to_string(),
        }
    }

    /// Set a prefix for environment variable names.
    pub fn with_prefix(mut self, prefix: impl Into<String>) -> Self {
        self.prefix = Some(prefix.into());
        self
    }

    /// Set a separator for nested keys.
    pub fn with_separator(mut self, separator: impl Into<String>) -> Self {
        self.separator = separator.into();
        self
    }

    /// Convert a config key to an environment variable name.
    fn to_env_name(&self, key: &str) -> String {
        let key = key.replace('.', &self.separator)
            .replace('-', &self.separator)
            .to_uppercase();
        
        match &self.prefix {
            Some(p) if !p.is_empty() => format!("{}_{}", p, key),
            _ => key,
        }
    }

    /// Convert an environment variable name back to a config key.
    fn from_env_name(&self, env_name: &str) -> String {
        let name = match &self.prefix {
            Some(p) if env_name.starts_with(&format!("{}_", p.to_uppercase())) => {
                env_name.strip_prefix(&format!("{}_", p.to_uppercase())).unwrap_or(env_name)
            }
            _ => env_name,
        };
        
        name.replace(&self.separator, ".")
            .replace('_', ".")
            .to_lowercase()
    }

    /// Parse a boolean value from string.
    fn parse_bool(s: &str) -> bool {
        matches!(
            s.to_lowercase().as_str(),
            "true" | "1" | "yes" | "on" | "t" | "y"
        )
    }

    /// Parse an integer value from string.
    fn parse_integer(s: &str) -> Option<i64> {
        s.parse().ok()
    }

    /// Parse a float value from string.
    fn parse_float(s: &str) -> Option<f64> {
        s.parse().ok()
    }

    /// Coerce a string value to ConfigValue.
    fn coerce_value(&self, s: &str) -> ConfigValue {
        // Try boolean
        if let Ok(b) = s.parse::<bool>() {
            return ConfigValue::Boolean(b);
        }
        
        // Try integer
        if let Ok(i) = s.parse::<i64>() {
            return ConfigValue::Integer(i);
        }
        
        // Try float
        if let Ok(f) = s.parse::<f64>() {
            return ConfigValue::Float(f);
        }
        
        // Fall back to string
        ConfigValue::String(s.to_string())
    }
}

impl Default for EnvAdapter {
    fn default() -> Self {
        Self::new()
    }
}

impl ConfigSourceTrait for EnvAdapter {
    fn get(&self, key: &str) -> ConfigResult<Option<ConfigValue>> {
        let env_name = self.to_env_name(key);
        
        match std::env::var(&env_name) {
            Ok(value) => Ok(Some(self.coerce_value(&value))),
            Err(std::env::VarError::NotPresent) => Ok(None),
            Err(e) => Err(ConfigError::new(
                crate::domain::ConfigErrorCode::IoError, 
                format!("failed to read env var {}: {}", env_name, e)
            )),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_env_adapter_basic() {
        std::env::set_var("TEST_PORT", "8080");
        
        let adapter = EnvAdapter::new();
        let value = adapter.get("test.port").unwrap();
        
        // Environment variables are uppercase with underscores
        // So TEST_PORT maps to test.port
        std::env::remove_var("TEST_PORT");
    }

    #[test]
    fn test_env_adapter_with_prefix() {
        std::env::set_var("APP_DATABASE_HOST", "localhost");
        
        let adapter = EnvAdapter::new().with_prefix("APP");
        let value = adapter.get("database.host").unwrap();
        
        assert!(value.is_some());
        
        std::env::remove_var("APP_DATABASE_HOST");
    }

    #[test]
    fn test_coerce_value() {
        let adapter = EnvAdapter::new();
        
        assert!(matches!(adapter.coerce_value("true"), ConfigValue::Boolean(true)));
        assert!(matches!(adapter.coerce_value("1"), ConfigValue::Integer(1)));
        assert!(matches!(adapter.coerce_value("3.14"), ConfigValue::Float(f) if (f - 3.14).abs() < 0.001));
        assert!(matches!(adapter.coerce_value("hello"), ConfigValue::String(s) if s == "hello"));
    }
}
