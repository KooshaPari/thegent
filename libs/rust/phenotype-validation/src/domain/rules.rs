//! Validation rule trait.

use super::{ValidationError, ValidationResult};

/// Validation rule - a single validation check.
pub trait ValidationRule<T> {
    /// Validate a value.
    fn validate(&self, value: &T) -> ValidationResult;
}

/// Validation rule that returns an error on failure.
pub trait StrictValidationRule<T>: ValidationRule<T> {
    /// Validate and return error on failure.
    fn validate_strict(&self, value: &T) -> Result<(), ValidationError>;
}

/// Common validation rule implementations.
pub mod rules {
    use super::*;
    use std::net::IpAddr;
    use regex::Regex;

    /// Required value validation.
    pub struct Required;

    impl<T> ValidationRule<Option<T>> for Required {
        fn validate(&self, value: &Option<T>) -> ValidationResult {
            match value {
                Some(_) => ValidationResult::valid(),
                None => ValidationResult::invalid(vec![ValidationError::new(
                    "value", "REQUIRED", "Value is required",
                )]),
            }
        }
    }

    /// Minimum length validation.
    pub struct MinLength(pub usize);

    impl ValidationRule<String> for MinLength {
        fn validate(&self, value: &String) -> ValidationResult {
            if value.len() >= self.0 {
                ValidationResult::valid()
            } else {
                ValidationResult::invalid(vec![ValidationError::new(
                    "value", "MIN_LENGTH",
                    &format!("Minimum length is {}", self.0),
                )])
            }
        }
    }

    /// Maximum length validation.
    pub struct MaxLength(pub usize);

    impl ValidationRule<String> for MaxLength {
        fn validate(&self, value: &String) -> ValidationResult {
            if value.len() <= self.0 {
                ValidationResult::valid()
            } else {
                ValidationResult::invalid(vec![ValidationError::new(
                    "value", "MAX_LENGTH",
                    &format!("Maximum length is {}", self.0),
                )])
            }
        }
    }

    /// Email format validation.
    pub struct Email;

    impl ValidationRule<String> for Email {
        fn validate(&self, value: &String) -> ValidationResult {
            let email_regex = Regex::new(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            ).unwrap();

            if email_regex.is_match(value) {
                ValidationResult::valid()
            } else {
                ValidationResult::invalid(vec![ValidationError::new(
                    "email", "INVALID_EMAIL",
                    "Invalid email format",
                )])
            }
        }
    }

    /// IP address validation.
    pub struct IpAddress;

    impl ValidationRule<String> for IpAddress {
        fn validate(&self, value: &String) -> ValidationResult {
            match value.parse::<IpAddr>() {
                Ok(_) => ValidationResult::valid(),
                Err(_) => ValidationResult::invalid(vec![ValidationError::new(
                    "ip_address", "INVALID_IP",
                    "Invalid IP address format",
                )]),
            }
        }
    }

    /// Range validation for numeric types.
    pub struct Range<T> {
        pub min: T,
        pub max: T,
    }

    impl<T: PartialOrd> ValidationRule<T> for Range<T> {
        fn validate(&self, value: &T) -> ValidationResult {
            if value >= &self.min && value <= &self.max {
                ValidationResult::valid()
            } else {
                ValidationResult::invalid(vec![ValidationError::new(
                    "value", "OUT_OF_RANGE",
                    &format!("Value must be between {} and {}", self.min, self.max),
                )])
            }
        }
    }

    /// Pattern matching validation.
    pub struct Pattern(pub Regex);

    impl ValidationRule<String> for Pattern {
        fn validate(&self, value: &String) -> ValidationResult {
            if self.0.is_match(value) {
                ValidationResult::valid()
            } else {
                ValidationResult::invalid(vec![ValidationError::new(
                    "value", "PATTERN_MISMATCH",
                    "Value does not match required pattern",
                )])
            }
        }
    }

    /// Custom validation with closure.
    pub struct Custom<F> {
        pub validator: F,
        pub error: ValidationError,
    }

    impl<T, F: Fn(&T) -> bool> ValidationRule<T> for Custom<F> {
        fn validate(&self, value: &T) -> ValidationResult {
            if (self.validator)(value) {
                ValidationResult::valid()
            } else {
                ValidationResult::invalid(vec![self.error.clone()])
            }
        }
    }
}
