//! Domain Value Object - Immutable Objects Without Identity
//!
//! Value objects are immutable objects that are defined by their attributes
//! rather than a unique identity. Two value objects with the same attributes
//! are considered equal.
//!
//! ## Key Characteristics
//!
//! - **Immutability**: Value objects cannot be modified after creation
//! - **Equality**: Two value objects are equal if all their attributes are equal
//! - **No Identity**: Value objects have no unique identifier
//! - **Side-Effect-Free**: Operations return new value objects
//!
//! ## Example
//! ## Example
//!
//! ```rust,ignore
//! use hexkit::domain::value_object::ValueObject;
//!
//! #[derive(Debug, Clone, PartialEq)]
//! pub struct Email(String);
//!
//! impl ValueObject for Email {
//!     fn validate(&self) -> Result<(), String> {
//!         if self.0.contains('@') {
//!             Ok(())
//!         } else {
//!             Err("Invalid email format".to_string())
//!         }
//!     }
//! }
//! ```

/// Error type for value object validation
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValueObjectError(pub String);

impl std::fmt::Display for ValueObjectError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "ValueObjectError: {}", self.0)
    }
}

impl std::error::Error for ValueObjectError {}

/// Marker trait for value objects
pub trait ValueObject: Send + Sync + Clone + PartialEq {
    /// Validate the value object's invariants
    fn validate(&self) -> Result<(), ValueObjectError>;
}

/// Extension trait for value object operations
pub trait ValueObjectExt: ValueObject {
    /// Create a new instance with modified attributes
    fn with<F: FnOnce(&Self) -> Self>(&self, f: F) -> Self {
        f(self)
    }
}

impl<T: ValueObject> ValueObjectExt for T {}

/// Base implementation for simple value objects
#[macro_export]
macro_rules! impl_value_object {
    ($type:ty) => {
        impl $crate::domain::ValueObject for $type {
            fn validate(&self) -> Result<(), $crate::domain::ValueObjectError> {
                Ok(())
            }
        }
    };
}

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Debug, Clone, PartialEq)]
    struct TestMoney {
        amount: f64,
        currency: String,
    }

    impl ValueObject for TestMoney {
        fn validate(&self) -> Result<(), ValueObjectError> {
            if self.amount < 0.0 {
                return Err(ValueObjectError("Amount cannot be negative".to_string()));
            }
            Ok(())
        }
    }

    #[test]
    fn test_value_object_equality() {
        let money1 = TestMoney {
            amount: 100.0,
            currency: "USD".to_string(),
        };

        let money2 = TestMoney {
            amount: 100.0,
            currency: "USD".to_string(),
        };

        let money3 = TestMoney {
            amount: 50.0,
            currency: "USD".to_string(),
        };

        assert_eq!(money1, money2);
        assert_ne!(money1, money3);
    }

    #[test]
    fn test_value_object_validation() {
        let valid = TestMoney { amount: 100.0, currency: "USD".to_string() };
        assert!(valid.validate().is_ok());

        let invalid = TestMoney { amount: -100.0, currency: "USD".to_string() };
        assert!(invalid.validate().is_err());
    }
}
