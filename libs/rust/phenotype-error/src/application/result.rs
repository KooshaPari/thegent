//! Result type - Rust-like Result type for error handling.
//!
//! This module provides a Result type that works with `AppError`
//! for ergonomic error handling.

use crate::domain::app_error::AppError;
use crate::domain::error_code::ErrorCode;

/// Result type alias using `AppError`.
pub type Result<T> = std::result::Result<T, AppError>;

/// Extension trait for `Result`.
pub trait ResultExt<T> {
    /// Map the Ok value.
    fn map_err_context<F>(self, f: F) -> Result<T>
    where
        F: FnOnce(AppError) -> AppError;

    /// Add context to the error.
    fn with_context<C: serde::Serialize>(self, key: &'static str, value: C) -> Result<T>;

    /// Map to a different error code.
    fn map_code(self, code: ErrorCode) -> Result<T>;

    /// Convert to an option, discarding the error.
    fn ok_or_log(self) -> Option<T>
    where
        Error: std::fmt::Debug;
}

impl<T> ResultExt<T> for Result<T> {
    fn map_err_context<F>(self, f: F) -> Result<T>
    where
        F: FnOnce(AppError) -> AppError,
    {
        self.map_err(f)
    }

    fn with_context<C: serde::Serialize>(self, key: &'static str, value: C) -> Result<T> {
        self.map_err(|e| e.with_context(key, value))
    }

    fn map_code(self, code: ErrorCode) -> Result<T> {
        self.map_err(|mut e| {
            // Note: Can't change the code after creation
            // This is a limitation - consider using `err()` instead
            e = AppError::new(code, e.message());
            e
        })
    }

    fn ok_or_log(self) -> Option<T>
    where
        Error: std::fmt::Debug,
    {
        match self {
            Ok(v) => Some(v),
            Err(e) => {
                eprintln!("Error (logged): {:?}", e);
                None
            }
        }
    }
}

/// Extension trait for `Option`.
pub trait OptionExt<T> {
    /// Convert to a Result with the given error.
    fn ok_or_error(self, code: ErrorCode, msg: &str) -> Result<T>;

    /// Convert to a Result with EntityNotFound error.
    fn ok_or_not_found(self, entity: &str, id: &str) -> Result<T>;
}

impl<T> OptionExt<T> for Option<T> {
    fn ok_or_error(self, code: ErrorCode, msg: &str) -> Result<T> {
        self.ok_or_else(|| AppError::new(code, msg))
    }

    fn ok_or_not_found(self, entity: &str, id: &str) -> Result<T> {
        self.ok_or_else(|| {
            AppError::new(ErrorCode::EntityNotFound, format!("{} with id '{}' not found", entity, id))
                .with_context("entity_type", entity)
                .with_context("entity_id", id)
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_result_with_context() {
        let result: Result<i32> = Err(AppError::new(ErrorCode::ValidationError, "Invalid"));
        let with_ctx = result.with_context("field", "email");
        assert!(with_ctx.is_err());
    }

    #[test]
    fn test_option_ok_or_error() {
        let none: Option<i32> = None;
        let result = none.ok_or_error(ErrorCode::EntityNotFound, "Not found");
        assert!(result.is_err());
    }

    #[test]
    fn test_option_ok_or_not_found() {
        let none: Option<i32> = None;
        let result = none.ok_or_not_found("User", "123");
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().code(), ErrorCode::EntityNotFound);
    }
}
