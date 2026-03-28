//! Policy errors.

use thiserror::Error;

/// Result type for policy operations.
pub type PolicyResult<T> = Result<T, PolicyError>;

/// Errors that can occur during policy operations.
#[derive(Debug, Error)]
pub enum PolicyError {
    #[error("Policy not found: {name}")]
    PolicyNotFound { name: String },

    #[error("Rule not found: {name} in policy {policy}")]
    RuleNotFound { name: String, policy: String },

    #[error("Invalid policy: {message}")]
    InvalidPolicy { message: String },

    #[error("Invalid rule: {message}")]
    InvalidRule { message: String },

    #[error("Evaluation error: {message}")]
    EvaluationError { message: String },

    #[error("Parse error: {message}")]
    ParseError { message: String },

    #[error("Serialization error: {message}")]
    SerializationError { message: String },

    #[error("Context error: {message}")]
    ContextError { message: String },

    #[error("Registry error: {message}")]
    RegistryError { message: String },
}

impl PolicyError {
    /// Create a PolicyNotFound error.
    pub fn policy_not_found(name: impl Into<String>) -> Self {
        PolicyError::PolicyNotFound { name: name.into() }
    }

    /// Create a RuleNotFound error.
    pub fn rule_not_found(name: impl Into<String>, policy: impl Into<String>) -> Self {
        PolicyError::RuleNotFound { 
            name: name.into(), 
            policy: policy.into() 
        }
    }

    /// Create an InvalidPolicy error.
    pub fn invalid_policy(message: impl Into<String>) -> Self {
        PolicyError::InvalidPolicy { message: message.into() }
    }

    /// Create an EvaluationError.
    pub fn evaluation_error(message: impl Into<String>) -> Self {
        PolicyError::EvaluationError { message: message.into() }
    }
}
