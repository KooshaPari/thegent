//! Entities - Enterprise business rules
//! 
//! Entities are enterprise-wide business rules.
//! They are objects that have a distinct identity.

use uuid::Uuid;

/// Base entity trait
pub trait Entity: std::fmt::Debug {
    type Id: std::fmt::Debug + Clone + PartialEq;
    
    fn id(&self) -> &Self::Id;
    fn equals(&self, other: &Self) -> bool;
}

/// UUID-based entity
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EntityId(Uuid);

impl EntityId {
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }
    
    pub fn from_string(s: &str) -> Self {
        Self(Uuid::parse_str(s).unwrap_or_else(|_| Uuid::new_v4()))
    }
}

impl Default for EntityId {
    fn default() -> Self {
        Self::new()
    }
}

/// Base aggregate trait
pub trait Aggregate: Entity {
    fn version(&self) -> u64;
}
