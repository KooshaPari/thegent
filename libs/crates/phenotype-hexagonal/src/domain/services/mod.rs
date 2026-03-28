//! Domain Services - Domain operations that don't belong to a single entity
//! 
//! Domain services are used when an operation conceptually belongs to a service
//! rather than an entity or value object. They encapsulate complex business
//! logic that involves multiple domain objects.

/// Marker trait for domain services
pub trait DomainService: Send + Sync {
    // Domain services contain business logic
    // They are stateless and orchestrate domain objects
}
