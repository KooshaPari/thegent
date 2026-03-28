//! Value Objects
//! 
//! Objects that describe characteristics without identity.

/// Marker trait for value objects
pub trait ValueObject: Clone + PartialEq + Send + Sync {
    type Value: Send + Sync + PartialEq;
    
    fn value(&self) -> &Self::Value;
}
