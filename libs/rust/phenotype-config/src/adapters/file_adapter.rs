//! File-based configuration adapter.
//!
//! This adapter loads configuration from files (JSON, TOML, YAML).

use crate::domain::config_source::ConfigSourceTrait;
use crate::domain::{ConfigError, ConfigResult, ConfigValue};
use std::collections::HashMap;
use std::fs;
use std::path::Path;

/// File-based configuration adapter.
#[derive(Debug, Clone)]
pub struct FileAdapter {
    values: HashMap<String, ConfigValue>,
    source_path: Option<String>,
}

impl FileAdapter {
    /// Create a new file adapter from a JSON file.
    pub fn from_json(path: impl AsRef<Path>) -> ConfigResult<Self> {
        let content = fs::read_to_string(path.as_ref())
            .map_err(|e| ConfigError::new(
                crate::domain::ConfigErrorCode::IoError,
                format!("failed to read file: {}", e)
            ))?;

        let value: serde_json::Value = serde_json::from_str(&content)
            .map_err(|e| ConfigError::parse_error(format!("invalid JSON: {}", e), &content))?;

        let values = Self::flatten_json(&value, String::new());
        
        Ok(Self {
            values,
            source_path: Some(path.as_ref().to_string_lossy().to_string()),
        })
    }

    /// Create a new file adapter from a TOML file.
    pub fn from_toml(path: impl AsRef<Path>) -> ConfigResult<Self> {
        let content = fs::read_to_string(path.as_ref())
            .map_err(|e| ConfigError::new(
                crate::domain::ConfigErrorCode::IoError,
                format!("failed to read file: {}", e)
            ))?;

        let value: toml::Value = toml::from_str(&content)
            .map_err(|e| ConfigError::parse_error(format!("invalid TOML: {}", e), &content))?;

        let values = Self::flatten_toml(&value, String::new());
        
        Ok(Self {
            values,
            source_path: Some(path.as_ref().to_string_lossy().to_string()),
        })
    }

    /// Flatten a JSON value into dot-separated keys.
    fn flatten_json(value: &serde_json::Value, prefix: String) -> HashMap<String, ConfigValue> {
        let mut map = HashMap::new();
        
        match value {
            serde_json::Value::Object(obj) => {
                for (key, val) in obj {
                    let new_prefix = if prefix.is_empty() {
                        key.clone()
                    } else {
                        format!("{}.{}", prefix, key)
                    };
                    
                    let nested = Self::flatten_json(val, new_prefix);
                    map.extend(nested);
                }
            }
            serde_json::Value::String(s) => {
                map.insert(prefix, ConfigValue::String(s.clone()));
            }
            serde_json::Value::Number(n) => {
                if let Some(i) = n.as_i64() {
                    map.insert(prefix, ConfigValue::Integer(i));
                } else if let Some(f) = n.as_f64() {
                    map.insert(prefix, ConfigValue::Float(f));
                }
            }
            serde_json::Value::Bool(b) => {
                map.insert(prefix, ConfigValue::Boolean(*b));
            }
            serde_json::Value::Null => {
                map.insert(prefix, ConfigValue::Null);
            }
            serde_json::Value::Array(arr) => {
                let values: Vec<ConfigValue> = arr.iter()
                    .filter_map(|v| Self::json_to_config(v))
                    .collect();
                map.insert(prefix, ConfigValue::List(values));
            }
        }
        
        map
    }

    /// Flatten a TOML value into dot-separated keys.
    fn flatten_toml(value: &toml::Value, prefix: String) -> HashMap<String, ConfigValue> {
        let mut map = HashMap::new();
        
        match value {
            toml::Value::Table(table) => {
                for (key, val) in table {
                    let new_prefix = if prefix.is_empty() {
                        key.clone()
                    } else {
                        format!("{}.{}", prefix, key)
                    };
                    
                    let nested = Self::flatten_toml(val, new_prefix);
                    map.extend(nested);
                }
            }
            toml::Value::String(s) => {
                map.insert(prefix, ConfigValue::String(s.clone()));
            }
            toml::Value::Integer(i) => {
                map.insert(prefix, ConfigValue::Integer(*i));
            }
            toml::Value::Float(f) => {
                map.insert(prefix, ConfigValue::Float(*f));
            }
            toml::Value::Boolean(b) => {
                map.insert(prefix, ConfigValue::Boolean(*b));
            }
            toml::Value::Datetime(dt) => {
                map.insert(prefix, ConfigValue::String(dt.to_string()));
            }
            toml::Value::Array(arr) => {
                let values: Vec<ConfigValue> = arr.iter()
                    .filter_map(|v| Self::toml_to_config(v))
                    .collect();
                map.insert(prefix, ConfigValue::List(values));
            }
        }
        
        map
    }

    /// Convert a JSON value to ConfigValue.
    fn json_to_config(value: &serde_json::Value) -> Option<ConfigValue> {
        match value {
            serde_json::Value::String(s) => Some(ConfigValue::String(s.clone())),
            serde_json::Value::Number(n) => {
                if let Some(i) = n.as_i64() {
                    Some(ConfigValue::Integer(i))
                } else if let Some(f) = n.as_f64() {
                    Some(ConfigValue::Float(f))
                } else {
                    None
                }
            }
            serde_json::Value::Bool(b) => Some(ConfigValue::Boolean(*b)),
            serde_json::Value::Null => Some(ConfigValue::Null),
            _ => None,
        }
    }

    /// Convert a TOML value to ConfigValue.
    fn toml_to_config(value: &toml::Value) -> Option<ConfigValue> {
        match value {
            toml::Value::String(s) => Some(ConfigValue::String(s.clone())),
            toml::Value::Integer(i) => Some(ConfigValue::Integer(*i)),
            toml::Value::Float(f) => Some(ConfigValue::Float(*f)),
            toml::Value::Boolean(b) => Some(ConfigValue::Boolean(*b)),
            _ => None,
        }
    }

    /// Create an empty adapter.
    pub fn empty() -> Self {
        Self {
            values: HashMap::new(),
            source_path: None,
        }
    }

    /// Create from a HashMap.
    pub fn from_map(map: HashMap<String, ConfigValue>) -> Self {
        Self {
            values: map,
            source_path: None,
        }
    }
}

impl ConfigSourceTrait for FileAdapter {
    fn get(&self, key: &str) -> ConfigResult<Option<ConfigValue>> {
        Ok(self.values.get(key).cloned())
    }
}
