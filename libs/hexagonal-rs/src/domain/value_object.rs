//! Value Object implementation
//!
//! Value Objects are objects that describe some characteristic or attribute
//! but carry no conceptual identity.

/// Marker trait for value objects
/// Value objects should be:
/// - Immutable
/// - Compared by value, not identity
/// - Self-validating
pub trait ValueObject: Send + Sync + Clone + PartialEq {}

/// Value object with validation
pub trait ValidatedValueObject<V>: ValueObject {
    /// Validate the value
    fn validate(value: &V) -> Result<(), String>;
}

/// Email value object example
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct Email(String);

impl Email {
    pub fn new(value: impl Into<String>) -> Result<Self, String> {
        let email = value.into();
        if email.contains('@') && email.len() >= 3 {
            Ok(Self(email))
        } else {
            Err("Invalid email format".to_string())
        }
    }
    
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl ValueObject for Email {}

impl std::fmt::Display for Email {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

/// Non-empty string value object
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct NonEmptyString(String);

impl NonEmptyString {
    pub fn new(value: impl Into<String>) -> Result<Self, String> {
        let s = value.into();
        if s.trim().is_empty() {
            Err("String cannot be empty".to_string())
        } else {
            Ok(Self(s))
        }
    }
    
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl ValueObject for NonEmptyString {}

impl std::fmt::Display for NonEmptyString {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}
