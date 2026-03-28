//! Data Transfer Objects (DTOs)
//!
//! DTOs are simple data structures used to transfer data between layers.

/// Marker trait for DTOs
pub trait Dto: Send + Sync + Sized {}

impl<T: Send + Sync + Sized> Dto for T {}

#[cfg(feature = "serde")]
pub mod serde {
    use serde::{Deserialize, Serialize};
    
    /// Input DTO for create operations
    pub trait CreateDto: Send + Sync + Sized + for<'de> Deserialize<'de> + Serialize {}
    
    /// Output DTO for read operations
    pub trait OutputDto: Send + Sync + Sized + Serialize {}
    
    /// Update DTO for patch operations
    pub trait UpdateDto: Send + Sync + Sized + for<'de> Deserialize<'de> + Serialize {}
}
