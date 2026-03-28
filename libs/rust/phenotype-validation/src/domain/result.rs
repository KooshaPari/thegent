//! Validation result types.

use super::ValidationError;
use std::fmt::Display;

/// Validation status.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ValidationStatus {
    Valid,
    Invalid,
}

/// Validation result - the outcome of a validation check.
#[derive(Debug, Clone)]
pub enum ValidationResult {
    Valid,
    Invalid(Vec<ValidationError>),
}

impl ValidationResult {
    /// Create a valid result.
    pub fn valid() -> Self {
        ValidationResult::Valid
    }

    /// Create an invalid result with errors.
    pub fn invalid(errors: Vec<ValidationError>) -> Self {
        ValidationResult::Invalid(errors)
    }

    /// Check if the result is valid.
    pub fn is_valid(&self) -> bool {
        matches!(self, ValidationResult::Valid)
    }

    /// Check if the result is invalid.
    pub fn is_invalid(&self) -> bool {
        matches!(self, ValidationResult::Invalid(_))
    }

    /// Get the errors if any.
    pub fn errors(&self) -> Option<Vec<ValidationError>> {
        match self {
            ValidationResult::Valid => None,
            ValidationResult::Invalid(errors) => Some(errors.clone()),
        }
    }

    /// Map errors to a new result.
    pub fn map_errors<F>(self, f: F) -> Self
    where
        F: FnOnce(Vec<ValidationError>) -> Vec<ValidationError>,
    {
        match self {
            ValidationResult::Valid => ValidationResult::Valid,
            ValidationResult::Invalid(errors) => ValidationResult::Invalid(f(errors)),
        }
    }

    /// Combine this result with another.
    pub fn and(self, other: ValidationResult) -> ValidationResult {
        match (self, other) {
            (ValidationResult::Valid, ValidationResult::Valid) => ValidationResult::Valid,
            (ValidationResult::Invalid(mut e1), ValidationResult::Invalid(e2)) => {
                e1.extend(e2);
                ValidationResult::Invalid(e1)
            }
            (ValidationResult::Invalid(e), _) => ValidationResult::Invalid(e),
            (_, ValidationResult::Invalid(e)) => ValidationResult::Invalid(e),
        }
    }

    /// Combine with multiple results.
    pub fn and_all(results: Vec<ValidationResult>) -> ValidationResult {
        results.into_iter().fold(
            ValidationResult::valid(),
            |acc, r| acc.and(r),
        )
    }
}

impl Default for ValidationResult {
    fn default() -> Self {
        ValidationResult::Valid
    }
}

/// A value that has been validated.
#[derive(Debug, Clone)]
pub struct Validated<T> {
    pub value: T,
    pub errors: Vec<ValidationError>,
}

impl<T> Validated<T> {
    /// Create a new validated value.
    pub fn new(value: T) -> Self {
        Self {
            value,
            errors: Vec::new(),
        }
    }

    /// Create from a result.
    pub fn from_result(value: T, result: ValidationResult) -> Self {
        match result {
            ValidationResult::Valid => Self {
                value,
                errors: Vec::new(),
            },
            ValidationResult::Invalid(errors) => Self { value, errors },
        }
    }

    /// Check if the value is valid.
    pub fn is_valid(&self) -> bool {
        self.errors.is_empty()
    }

    /// Check if the value is invalid.
    pub fn is_invalid(&self) -> bool {
        !self.errors.is_empty()
    }

    /// Get the first error if any.
    pub fn first_error(&self) -> Option<&ValidationError> {
        self.errors.first()
    }
}

impl<T: Display> Display for Validated<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if self.is_valid() {
            write!(f, "{}", self.value)
        } else {
            write!(f, "{} (invalid: {})", self.value, self.errors.len())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_valid_result() {
        let result = ValidationResult::valid();
        assert!(result.is_valid());
        assert!(!result.is_invalid());
        assert!(result.errors().is_none());
    }

    #[test]
    fn test_invalid_result() {
        let error = ValidationError::new("field", "ERR", "error");
        let result = ValidationResult::invalid(vec![error]);
        assert!(!result.is_valid());
        assert!(result.is_invalid());
        assert_eq!(result.errors().unwrap().len(), 1);
    }

    #[test]
    fn test_and_combination() {
        let r1 = ValidationResult::valid();
        let error = ValidationError::new("a", "ERR", "error");
        let r2 = ValidationResult::invalid(vec![error]);
        
        let combined = r1.and(r2);
        assert!(combined.is_invalid());
    }
}
