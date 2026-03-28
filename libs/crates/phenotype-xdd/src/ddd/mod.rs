//! Domain-Driven Design (DDD)
//! 
//! DDD focuses on understanding the business domain and modeling it effectively.
//! 
//! ## Key Concepts
//! 
//! - **Bounded Context**: A boundary within which a particular domain model applies
//! - **Ubiquitous Language**: Common language shared by team and domain experts
//! - **Aggregates**: Clusters of related entities and value objects
//! - **Domain Events**: Significant occurrences in the domain
//! - **Repositories**: Collections of entities
//! 
//! ## DDD Building Blocks
//! 
//! ```text
//! Entities
//!   └─ Aggregate Root
//!        ├─ Entity
//!        └─ Value Objects
//! 
//! Services (Domain)
//! Events (Domain)
//! Repositories (Interfaces)
//! ```

/// Domain primitive traits
pub mod primitives {
    /// Entity with identity
    pub trait Entity: std::fmt::Debug {
        type Id: std::fmt::Debug + Clone + PartialEq;
        fn id(&self) -> &Self::Id;
    }
    
    /// Value object without identity
    pub trait ValueObject: Clone + PartialEq {
        type Value;
        fn value(&self) -> &Self::Value;
    }
    
    /// Aggregate root
    pub trait AggregateRoot: Entity {
        fn version(&self) -> u64;
    }
}

/// Bounded context
#[derive(Debug)]
pub struct BoundedContext {
    pub name: String,
    pub description: String,
    pub aggregates: Vec<String>,
}

impl BoundedContext {
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            description: String::new(),
            aggregates: Vec::new(),
        }
    }
    
    pub fn description(mut self, desc: impl Into<String>) -> Self {
        self.description = desc.into();
        self
    }
    
    pub fn add_aggregate(mut self, aggregate: impl Into<String>) -> Self {
        self.aggregates.push(aggregate.into());
        self
    }
}

/// Context map relationship types
#[derive(Debug, Clone, Copy)]
pub enum ContextRelationship {
    /// Upstream publishes, downstream subscribes
    CustomerSupplier,
    /// Upstream is independent
    Upstream,
    /// Downstream is independent
    Downstream,
    /// Shared domain model (anti-pattern)
    SharedKernel,
    /// Separate models with translation layer
    AntiCorruptionLayer,
}

/// Context mapping
#[derive(Debug)]
pub struct ContextMap {
    pub contexts: Vec<BoundedContext>,
    pub relationships: Vec<(String, String, ContextRelationship)>,
}

impl ContextMap {
    pub fn new() -> Self {
        Self {
            contexts: Vec::new(),
            relationships: Vec::new(),
        }
    }
    
    pub fn add_context(mut self, context: BoundedContext) -> Self {
        self.contexts.push(context);
        self
    }
    
    pub fn add_relationship(
        mut self,
        upstream: String,
        downstream: String,
        relationship: ContextRelationship,
    ) -> Self {
        self.relationships.push((upstream, downstream, relationship));
        self
    }
}

impl Default for ContextMap {
    fn default() -> Self {
        Self::new()
    }
}

/// Domain event
#[derive(Debug, Clone)]
pub struct DomainEvent {
    pub name: String,
    pub occurred_at: chrono::DateTime<chrono::Utc>,
    pub payload: serde_json::Value,
}

impl DomainEvent {
    pub fn new(name: impl Into<String>, payload: serde_json::Value) -> Self {
        Self {
            name: name.into(),
            occurred_at: chrono::Utc::now(),
            payload,
        }
    }
}

/// Repository interface
#[async_trait::async_trait]
pub trait Repository<E: primitives::Entity, Id: Clone> {
    type Error: std::error::Error + Send + Sync + 'static;
    
    async fn save(&self, entity: E) -> Result<(), Self::Error>;
    async fn find_by_id(&self, id: &Id) -> Result<Option<E>, Self::Error>;
    async fn delete(&self, id: &Id) -> Result<(), Self::Error>;
}
