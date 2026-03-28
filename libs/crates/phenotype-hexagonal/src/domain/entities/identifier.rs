//! Identifier types for entities
//! 
//! Identifiers provide unique identification for entities.
//! They are value objects that should be compared by their inner value.

use std::fmt;
use uuid::Uuid;

/// Trait for entity identifiers
pub trait Identifier: Clone + PartialEq + Send + Sync {
    /// Returns true if this is a transient (new) identifier
    fn is_transient(&self) -> bool;
    
    /// Returns the underlying value as a string
    fn to_string(&self) -> String;
}

/// UUID-based identifier
#[derive(Clone, PartialEq, Eq, Hash)]
pub struct UuidId(Uuid);

impl UuidId {
    /// Create a new transient (placeholder) ID
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }
    
    /// Create from an existing UUID
    pub fn from_uuid(id: Uuid) -> Self {
        Self(id)
    }
    
    /// Create from a string (panics if invalid)
    pub fn from_string(s: &str) -> Self {
        Self(Uuid::parse_str(s).expect("Invalid UUID string"))
    }
    
    /// Get the inner UUID
    pub fn as_uuid(&self) -> &Uuid {
        &self.0
    }
}

impl Default for UuidId {
    fn default() -> Self {
        Self::new()
    }
}

impl Identifier for UuidId {
    fn is_transient(&self) -> bool {
        // In a real implementation, you'd track this separately
        false
    }
    
    fn to_string(&self) -> String {
        self.0.to_string()
    }
}

impl fmt::Debug for UuidId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "UuidId({})", self.0)
    }
}

impl fmt::Display for UuidId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}
