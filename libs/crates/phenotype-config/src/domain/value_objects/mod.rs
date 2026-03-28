//! Value objects

use std::fmt;
use std::str::FromStr;
use serde::{Serialize, Deserialize};

/// Configuration value types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ValueType {
    /// String value
    String,
    /// Integer value
    Integer,
    /// Float/double value
    Float,
    /// Boolean value
    Boolean,
    /// JSON object/array
    Json,
    /// Secret (encrypted string)
    Secret,
}

impl ValueType {
    /// Get the type name
    pub fn as_str(&self) -> &'static str {
        match self {
            ValueType::String => "string",
            ValueType::Integer => "integer",
            ValueType::Float => "float",
            ValueType::Boolean => "boolean",
            ValueType::Json => "json",
            ValueType::Secret => "secret",
        }
    }
}

impl fmt::Display for ValueType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

impl FromStr for ValueType {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "string" => Ok(ValueType::String),
            "integer" | "int" => Ok(ValueType::Integer),
            "float" | "double" => Ok(ValueType::Float),
            "boolean" | "bool" => Ok(ValueType::Boolean),
            "json" | "object" => Ok(ValueType::Json),
            "secret" | "password" => Ok(ValueType::Secret),
            _ => Err(format!("Unknown value type: {}", s)),
        }
    }
}

/// Configuration value with type safety
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ConfigValue {
    #[serde(flatten)]
    inner: ConfigValueInner,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(untagged)]
enum ConfigValueInner {
    String(String),
    Integer(i64),
    Float(f64),
    Boolean(bool),
    Json(serde_json::Value),
    Secret {
        #[serde(rename = "_secret")]
        value: String,
    },
}

impl ConfigValue {
    /// Create a string value
    pub fn string(value: impl Into<String>) -> Self {
        Self { inner: ConfigValueInner::String(value.into()) }
    }

    /// Create an integer value
    pub fn integer(value: i64) -> Self {
        Self { inner: ConfigValueInner::Integer(value) }
    }

    /// Create a float value
    pub fn float(value: f64) -> Self {
        Self { inner: ConfigValueInner::Float(value) }
    }

    /// Create a boolean value
    pub fn boolean(value: bool) -> Self {
        Self { inner: ConfigValueInner::Boolean(value) }
    }

    /// Create a JSON value
    pub fn json(value: serde_json::Value) -> Self {
        Self { inner: ConfigValueInner::Json(value) }
    }

    /// Create a secret value
    pub fn secret(value: impl Into<String>) -> Self {
        Self { inner: ConfigValueInner::Secret { value: value.into() } }
    }

    /// Get the value type
    pub fn value_type(&self) -> ValueType {
        match &self.inner {
            ConfigValueInner::String(_) => ValueType::String,
            ConfigValueInner::Integer(_) => ValueType::Integer,
            ConfigValueInner::Float(_) => ValueType::Float,
            ConfigValueInner::Boolean(_) => ValueType::Boolean,
            ConfigValueInner::Json(_) => ValueType::Json,
            ConfigValueInner::Secret { .. } => ValueType::Secret,
        }
    }

    /// Get the value as a string (for display)
    pub fn as_string(&self) -> String {
        match &self.inner {
            ConfigValueInner::String(s) => s.clone(),
            ConfigValueInner::Integer(i) => i.to_string(),
            ConfigValueInner::Float(f) => f.to_string(),
            ConfigValueInner::Boolean(b) => b.to_string(),
            ConfigValueInner::Json(j) => j.to_string(),
            ConfigValueInner::Secret { .. } => "***SECRET***".to_string(),
        }
    }
}

/// Namespace for organizing configurations
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Namespace {
    path: String,
}

impl Namespace {
    /// Create a root namespace
    pub fn root() -> Self {
        Self { path: String::new() }
    }

    /// Create a namespaced path
    pub fn new(path: &str) -> Self {
        Self { path: path.to_string() }
    }

    /// Get the path
    pub fn path(&self) -> &str {
        &self.path
    }

    /// Check if this is the root namespace
    pub fn is_root(&self) -> bool {
        self.path.is_empty()
    }

    /// Get parent namespace
    pub fn parent(&self) -> Option<Namespace> {
        if self.is_root() {
            return None;
        }
        let parts: Vec<&str> = self.path.rsplitn(2, '.').collect();
        if parts.len() == 2 {
            Some(Namespace::new(parts[1]))
        } else {
            Some(Namespace::root())
        }
    }
}

impl Default for Namespace {
    fn default() -> Self {
        Self::root()
    }
}

impl fmt::Display for Namespace {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.path)
    }
}
