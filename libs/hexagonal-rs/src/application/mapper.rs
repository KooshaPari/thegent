//! Mapper implementations
//!
//! Mappers convert between domain objects, DTOs, and persistence models.

/// Trait for mapping between domain and DTO
pub trait DtoMapper<D, T>: Send + Sync {
    fn to_dto(&self, domain: D) -> T;
    fn to_domain(&self, dto: T) -> D;
}

/// Trait for mapping between domain and persistence
pub trait PersistenceMapper<D, P>: Send + Sync {
    fn to_persistence(&self, domain: D) -> P;
    fn to_domain(&self, persistence: P) -> D;
}

/// Trait for mapping between DTO and persistence
pub trait DtoPersistenceMapper<T, P>: Send + Sync {
    fn to_persistence(&self, dto: T) -> P;
    fn to_dto(&self, persistence: P) -> T;
}

/// Generic mapper that maps between three types
pub trait FullMapper<D, T, P>: Send + Sync {
    fn domain_to_dto(&self, domain: D) -> T;
    fn dto_to_domain(&self, dto: T) -> D;
    fn domain_to_persistence(&self, domain: D) -> P;
    fn persistence_to_domain(&self, persistence: P) -> D;
    fn dto_to_persistence(&self, dto: T) -> P;
    fn persistence_to_dto(&self, persistence: P) -> T;
}

/// Null mapper that passes through without transformation
pub struct PassThroughMapper;

impl<T> DtoMapper<T, T> for PassThroughMapper {
    fn to_dto(&self, domain: T) -> T { domain }
    fn to_domain(&self, dto: T) -> T { dto }
}

impl<T> PersistenceMapper<T, T> for PassThroughMapper {
    fn to_persistence(&self, domain: T) -> T { domain }
    fn to_domain(&self, persistence: T) -> T { persistence }
}
