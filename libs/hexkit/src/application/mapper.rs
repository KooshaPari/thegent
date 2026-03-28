//! Mapper - Conversion Between Domain and DTOs
//!
//! Mappers convert between domain objects and DTOs.

/// Simple mapper that transforms A to B
pub trait Mapper<A, B>: Send + Sync {
    fn to(&self, from: A) -> B;
}
