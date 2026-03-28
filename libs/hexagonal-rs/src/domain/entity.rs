//! Entity trait and utilities
//!
//! Entities are objects with a distinct identity that runs through time
//! and different representations of the same conceptual thing.

use uuid::Uuid;
use chrono::{DateTime, Utc};

/// Marker trait for entities with identity
pub trait Entity: Send + Sync {
    /// Type of the entity's unique identifier
    type Id: Send + Sync + Clone + PartialEq + std::fmt::Debug + std::fmt::Display;
    
    /// Returns the unique identifier of this entity
    fn id(&self) -> &Self::Id;
    
    /// Checks if this entity is the same as another (by identity)
    fn is_same(&self, other: &dyn Entity<Id = Self::Id>) -> bool {
        self.id() == other.id()
    }
}

/// Base entity implementation with UUID
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct BaseEntity<Id> {
    id: Id,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

impl<Id> BaseEntity<Id>
where
    Id: Send + Sync + Clone + PartialEq + std::fmt::Debug + std::fmt::Display,
{
    pub fn new(id: Id) -> Self {
        let now = Utc::now();
        Self {
            id,
            created_at: now,
            updated_at: now,
        }
    }
    
    pub fn id(&self) -> &Id {
        &self.id
    }
    
    pub fn created_at(&self) -> DateTime<Utc> {
        self.created_at
    }
    
    pub fn updated_at(&self) -> DateTime<Utc> {
        self.updated_at
    }
    
    pub fn touch(&mut self) {
        self.updated_at = Utc::now();
    }
}

impl<Id> Entity for BaseEntity<Id>
where
    Id: Send + Sync + Clone + PartialEq + std::fmt::Debug + std::fmt::Display,
{
    type Id = Id;
    
    fn id(&self) -> &Self::Id {
        &self.id
    }
}

/// Typed ID wrapper for entities
#[derive(Debug, Clone, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub struct EntityId(String);

impl EntityId {
    pub fn new() -> Self {
        Self(Uuid::new_v4().to_string())
    }
    
    pub fn from_string(s: impl Into<String>) -> Self {
        Self(s.into())
    }
    
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl Default for EntityId {
    fn default() -> Self {
        Self::new()
    }
}

impl std::fmt::Display for EntityId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}
