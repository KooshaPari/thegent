//! Domain entities

use crate::value_objects::{ConfigValue, Namespace};
use chrono::{DateTime, Utc};
use uuid::Uuid;

/// Configuration entry - the core entity
#[derive(Debug, Clone, PartialEq)]
pub struct ConfigEntry {
    id: Uuid,
    key: String,
    value: ConfigValue,
    version: u32,
    namespace: Namespace,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
    created_by: Option<String>,
    updated_by: Option<String>,
    metadata: std::collections::HashMap<String, String>,
}

impl ConfigEntry {
    /// Create a new config entry
    pub fn new(
        key: String,
        value: ConfigValue,
        namespace: Namespace,
        created_by: Option<String>,
    ) -> Result<Self, ConfigError> {
        Self::validate_key(&key)?;

        let now = Utc::now();
        Ok(Self {
            id: Uuid::new_v4(),
            key,
            value,
            version: 1,
            namespace,
            created_at: now,
            updated_at: now,
            created_by,
            updated_by: None,
            metadata: std::collections::HashMap::new(),
        })
    }

    /// Create a new config entry with metadata
    pub fn with_metadata(mut self, key: String, value: String) -> Self {
        self.metadata.insert(key, value);
        self
    }

    /// Validate the key
    fn validate_key(key: &str) -> Result<(), ConfigError> {
        if key.is_empty() {
            return Err(ConfigError::InvalidKey("Key cannot be empty".to_string()));
        }
        if key.len() > 256 {
            return Err(ConfigError::InvalidKey("Key exceeds maximum length of 256".to_string()));
        }
        if key.starts_with('.') {
            return Err(ConfigError::InvalidKey("Key cannot start with '.'".to_string()));
        }
        Ok(())
    }

    /// Get the entry ID
    pub fn id(&self) -> Uuid {
        self.id
    }

    /// Get the key
    pub fn key(&self) -> &str {
        &self.key
    }

    /// Get the value
    pub fn value(&self) -> &ConfigValue {
        &self.value
    }

    /// Get the version
    pub fn version(&self) -> u32 {
        self.version
    }

    /// Get the namespace
    pub fn namespace(&self) -> &Namespace {
        &self.namespace
    }

    /// Get created timestamp
    pub fn created_at(&self) -> DateTime<Utc> {
        self.created_at
    }

    /// Get updated timestamp
    pub fn updated_at(&self) -> DateTime<Utc> {
        self.updated_at
    }

    /// Get metadata
    pub fn metadata(&self) -> &std::collections::HashMap<String, String> {
        &self.metadata
    }

    /// Update the value (creates new version)
    pub fn update_value(&self, new_value: ConfigValue, updated_by: Option<String>) -> Self {
        let now = Utc::now();
        Self {
            id: self.id,
            key: self.key.clone(),
            value: new_value,
            version: self.version + 1,
            namespace: self.namespace.clone(),
            created_at: self.created_at,
            updated_at: now,
            created_by: self.created_by.clone(),
            updated_by,
            metadata: self.metadata.clone(),
        }
    }
}

/// Import error type for use in this module
use crate::ConfigError;
