//! Domain services

use crate::domain::entities::ConfigEntry;
use crate::value_objects::ConfigValue;
use crate::ConfigError;

/// Service for validating configurations
pub struct ConfigValidator;

impl ConfigValidator {
    /// Validate a config key
    pub fn validate_key(key: &str) -> Result<(), ConfigError> {
        if key.is_empty() {
            return Err(ConfigError::InvalidKey("Key cannot be empty".to_string()));
        }
        if key.len() > 256 {
            return Err(ConfigError::InvalidKey("Key exceeds maximum length".to_string()));
        }
        if key.starts_with('.') {
            return Err(ConfigError::InvalidKey("Key cannot start with '.'".to_string()));
        }
        if key.ends_with('.') {
            return Err(ConfigError::InvalidKey("Key cannot end with '.'".to_string()));
        }
        Ok(())
    }

    /// Validate a config value against its declared type
    pub fn validate_value(value: &ConfigValue) -> Result<(), ConfigError> {
        match value.value_type() {
            crate::value_objects::ValueType::String => Ok(()),
            crate::value_objects::ValueType::Integer => Ok(()),
            crate::value_objects::ValueType::Float => Ok(()),
            crate::value_objects::ValueType::Boolean => Ok(()),
            crate::value_objects::ValueType::Json => {
                // Would validate JSON structure here
                Ok(())
            }
            crate::value_objects::ValueType::Secret => {
                // Would validate secret format here
                Ok(())
            }
        }
    }
}

/// Service for resolving config keys with interpolation
pub struct ConfigResolver;

impl ConfigResolver {
    /// Resolve a key with variable interpolation
    pub fn resolve(key: &str, entries: &[ConfigEntry]) -> Option<String> {
        let mut result = key.to_string();
        let mut changed = true;

        while changed {
            changed = false;
            for entry in entries {
                let pattern = format!("${{{}}}", entry.key());
                if result.contains(&pattern) {
                    result = result.replace(&pattern, &entry.value().as_string());
                    changed = true;
                }
            }
        }

        Some(result)
    }
}
