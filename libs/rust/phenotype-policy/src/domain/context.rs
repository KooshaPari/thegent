//! Policy Context - Data passed to policy evaluation.
//!
//! The context contains all the information needed to evaluate policies.

use std::collections::HashMap;

/// Policy context - Provides access to attributes for policy evaluation.
///
/// The context contains:
/// - Subject attributes (who is making the request)
/// - Resource attributes (what is being accessed)
/// - Action attributes (what action is being performed)
/// - Environment attributes (when/where the request is made)
pub trait PolicyContext: Send + Sync {
    /// Get an attribute value.
    fn get(&self, key: &str) -> Option<String>;

    /// Get all attributes as a map.
    fn all(&self) -> HashMap<String, String>;

    /// Check if an attribute exists.
    fn has(&self, key: &str) -> bool {
        self.get(key).is_some()
    }

    /// Get a boolean attribute.
    fn get_bool(&self, key: &str) -> Option<bool> {
        self.get(key).map(|v| v.parse().unwrap_or(false))
    }

    /// Get an integer attribute.
    fn get_int(&self, key: &str) -> Option<i64> {
        self.get(key).and_then(|v| v.parse().ok())
    }
}

/// Simple context implementation using a HashMap.
#[derive(Debug, Clone, Default)]
pub struct SimpleContext {
    attributes: HashMap<String, String>,
}

impl SimpleContext {
    /// Create a new empty context.
    pub fn new() -> Self {
        Self::default()
    }

    /// Create from a HashMap.
    pub fn from_map(attributes: HashMap<String, String>) -> Self {
        Self { attributes }
    }

    /// Add an attribute.
    pub fn with(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.attributes.insert(key.into(), value.into());
        self
    }

    /// Add subject attributes.
    pub fn with_subject(mut self, subject_id: &str, role: &str) -> Self {
        self.attributes.insert("subject.id".to_string(), subject_id.to_string());
        self.attributes.insert("subject.role".to_string(), role.to_string());
        self
    }

    /// Add resource attributes.
    pub fn with_resource(mut self, resource_type: &str, resource_id: &str) -> Self {
        self.attributes.insert("resource.type".to_string(), resource_type.to_string());
        self.attributes.insert("resource.id".to_string(), resource_id.to_string());
        self
    }

    /// Add action attributes.
    pub fn with_action(mut self, action: &str) -> Self {
        self.attributes.insert("action".to_string(), action.to_string());
        self
    }
}

impl PolicyContext for SimpleContext {
    fn get(&self, key: &str) -> Option<String> {
        // Support nested keys like "subject.role"
        let parts: Vec<&str> = key.split('.').collect();
        
        if parts.len() == 1 {
            self.attributes.get(key).cloned()
        } else {
            let mut current = &self.attributes;
            for (i, part) in parts.iter().enumerate() {
                if i == parts.len() - 1 {
                    return current.get(*part).cloned();
                }
                // For nested lookups, we'd need recursive handling
                // This is a simplified version
                if i == 0 {
                    if let Some(prefix) = current.get(*part) {
                        let suffix = parts[i+1..].join(".");
                        let full_key = format!("{}.{}", prefix, suffix);
                        return self.attributes.get(&full_key).cloned();
                    }
                }
            }
            None
        }
    }

    fn all(&self) -> HashMap<String, String> {
        self.attributes.clone()
    }
}
