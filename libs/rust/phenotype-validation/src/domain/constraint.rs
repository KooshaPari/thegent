//! Constraint types for validation.

use super::{ValidationError, ValidationResult};
use super::rules::ValidationRule;
use std::marker::PhantomData;

/// A constraint is a named validation rule with a field path.
pub struct Constraint<T> {
    pub name: String,
    pub field: String,
    pub rule: Box<dyn ValidationRule<T>>,
}

impl<T> Constraint<T> {
    /// Create a new constraint.
    pub fn new(name: &str, field: &str, rule: impl ValidationRule<T> + 'static) -> Self {
        Self {
            name: name.to_string(),
            field: field.to_string(),
            rule: Box::new(rule),
        }
    }

    /// Validate a value with this constraint.
    pub fn validate(&self, value: &T) -> ValidationResult {
        let result = self.rule.validate(value);
        result.map_errors(|errors| {
            errors.into_iter()
                .map(|e| ValidationError {
                    field: format!("{}.{}", self.field, e.field),
                    code: format!("{}_{}", self.name, e.code),
                    message: e.message,
                    context: e.context,
                })
                .collect()
        })
    }
}

/// Constraint builder for fluent API.
pub struct ConstraintBuilder<T> {
    field: String,
    constraints: Vec<Box<dyn ValidationRule<T>>>,
}

impl<T> ConstraintBuilder<T> {
    /// Start building a constraint for a field.
    pub fn for_field(field: &str) -> Self {
        Self {
            field: field.to_string(),
            constraints: Vec::new(),
        }
    }

    /// Add a rule.
    pub fn rule<R: ValidationRule<T> + 'static>(mut self, rule: R) -> Self {
        self.constraints.push(Box::new(rule));
        self
    }

    /// Build the constraint.
    pub fn build(self, name: &str) -> Constraint<T> {
        let rules = self.constraints;
        let field = self.field;
        Constraint::new(name, &field, Rules(rules))
    }
}

struct Rules<T>(Vec<Box<dyn ValidationRule<T>>>);

impl<T> ValidationRule<T> for Rules<T> {
    fn validate(&self, value: &T) -> ValidationResult {
        let mut errors = Vec::new();
        for rule in &self.0 {
            let result = rule.validate(value);
            if let Some(e) = result.errors() {
                errors.extend(e);
            }
        }
        if errors.is_empty() {
            ValidationResult::Valid
        } else {
            ValidationResult::Invalid(errors)
        }
    }
}

/// Common constraint factory.
pub mod factories {
    use super::*;

    /// Create a required constraint.
    pub fn required<T>() -> Constraint<Option<T>> {
        use super::super::rules::Required;
        Constraint::new("required", "value", Required)
    }

    /// Create a min length constraint.
    pub fn min_length(min: usize) -> Constraint<String> {
        use super::super::rules::MinLength;
        Constraint::new("min_length", "value", MinLength(min))
    }

    /// Create a max length constraint.
    pub fn max_length(max: usize) -> Constraint<String> {
        use super::super::rules::MaxLength;
        Constraint::new("max_length", "value", MaxLength(max))
    }

    /// Create an email constraint.
    pub fn email() -> Constraint<String> {
        use super::super::rules::Email;
        Constraint::new("email", "value", Email)
    }

    /// Create an IP address constraint.
    pub fn ip_address() -> Constraint<String> {
        use super::super::rules::IpAddress;
        Constraint::new("ip_address", "value", IpAddress)
    }

    /// Create a range constraint.
    pub fn range<T: Clone>(min: T, max: T) -> Constraint<T> {
        use super::super::rules::Range;
        Constraint::new("range", "value", Range { min, max })
    }

    /// Create a pattern constraint.
    pub fn pattern(regex: &str) -> Constraint<String> {
        use super::super::rules::Pattern;
        use regex::Regex;
        let re = Regex::new(regex).expect("Invalid regex");
        Constraint::new("pattern", "value", Pattern(re))
    }
}
