//! ThisError adapter - Compatibility with thiserror crate.
//!
//! This adapter provides utilities for working with thiserror
//! while converting to AppError.

use crate::domain::app_error::AppError;
use crate::domain::error_code::ErrorCode;
use crate::adapters::{FromAppError, IntoAppError};

/// Trait for converting thiserror types to AppError.
pub trait ThisErrorIntoAppError {
    /// Convert to AppError.
    fn into_app_error(&self) -> AppError;
}

/// Convert any thiserror into AppError.
pub fn convert_thiserror<E: ThisErrorIntoAppError>(error: &E) -> AppError {
    error.into_app_error()
}

#[cfg(test)]
mod tests {
    use super::*;
    use thiserror::Error;

    #[derive(Debug, Error)]
    enum MyError {
        #[error("Validation error: {field}")]
        Validation { field: String },
        #[error("Not found: {entity} {id}")]
        NotFound { entity: String, id: String },
    }

    impl ThisErrorIntoAppError for MyError {
        fn into_app_error(&self) -> AppError {
            match self {
                MyError::Validation { field } => {
                    AppError::new(ErrorCode::ValidationError, self.to_string())
                        .with_context("field", field)
                }
                MyError::NotFound { entity, id } => {
                    AppError::new(ErrorCode::EntityNotFound, self.to_string())
                        .with_context("entity", entity)
                        .with_context("id", id)
                }
            }
        }
    }

    #[test]
    fn test_thiserror_validation() {
        let err = MyError::Validation {
            field: "email".to_string(),
        };
        let app_error = err.into_app_error();
        assert_eq!(app_error.code(), ErrorCode::ValidationError);
    }

    #[test]
    fn test_thiserror_not_found() {
        let err = MyError::NotFound {
            entity: "User".to_string(),
            id: "123".to_string(),
        };
        let app_error = err.into_app_error();
        assert_eq!(app_error.code(), ErrorCode::EntityNotFound);
    }
}
