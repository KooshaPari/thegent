//! Value Object trait and helpers
//! 
//! A value object is an immutable domain object that is defined by
//! its attributes rather than a unique identity.

/// Marker trait for value objects
pub trait ValueObject: Clone + Send + Sync + PartialEq {
    /// Type of the value
    type Value: Send + Sync + PartialEq;
    
    /// Get the underlying value
    fn value(&self) -> &Self::Value;
    
    /// Create a new value object from a value
    fn from_value(value: Self::Value) -> Self
    where
        Self: Sized,
    {
        Self::new(value)
    }
    
    /// Create a new value object (implement this in concrete types)
    fn new(value: Self::Value) -> Self;
}
