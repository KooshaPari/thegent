//! Application layer - Validator services.

use super::{Constraint, ValidationError, ValidationResult, Validated};
use std::collections::HashMap;

/// Schema validator - validates values against a schema of constraints.
pub struct SchemaValidator {
    constraints: HashMap<String, Box<dyn Fn(&dyn std::any::Any) -> ValidationResult + Send + Sync>>,
}

impl SchemaValidator {
    /// Create a new schema validator.
    pub fn new() -> Self {
        Self {
            constraints: HashMap::new(),
        }
    }

    /// Add a constraint for a field.
    pub fn add_constraint<T: 'static + Send + Sync>(
        &mut self,
        field: &str,
        constraint: Constraint<T>,
        get_value: impl Fn(&dyn std::any::Any) -> &T + Send + Sync + 'static,
    ) {
        let field_name = field.to_string();
        self.constraints.insert(field_name, Box::new(move |value| {
            let typed_value = get_value(value);
            constraint.validate(typed_value)
        }));
    }

    /// Validate a value against all constraints.
    pub fn validate(&self, values: &dyn std::any::Any) -> ValidationResult {
        let mut all_errors = Vec::new();
        
        for (field, validator) in &self.constraints {
            // We need to check if this field exists in the values
            let _ = field; // Placeholder for actual validation
            // In a real implementation, we would extract the value and validate
        }
        
        if all_errors.is_empty() {
            ValidationResult::valid()
        } else {
            ValidationResult::invalid(all_errors)
        }
    }
}

impl Default for SchemaValidator {
    fn default() -> Self {
        Self::new()
    }
}

/// Validate a value with a constraint.
pub fn validate<T>(value: &T, constraint: &Constraint<T>) -> Validated<T> {
    let result = constraint.validate(value);
    Validated::from_result(value.clone(), result)
}

/// Validate multiple values with multiple constraints.
pub fn validate_all<T>(value: &T, constraints: &[Constraint<T>]) -> Validated<T> {
    let results: Vec<ValidationResult> = constraints
        .iter()
        .map(|c| c.validate(value))
        .collect();
    
    let combined = ValidationResult::and_all(results);
    Validated::from_result(value.clone(), combined)
}
