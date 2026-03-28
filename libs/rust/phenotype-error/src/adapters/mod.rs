//! Adapters layer - Compatibility adapters for anyhow and thiserror.
//!
//! This layer provides adapters to convert between `AppError`
//! and other error types like `anyhow::Error` and `thiserror`.

mod anyhow_adapter;
mod thiserror_adapter;

pub use anyhow_adapter::AnyhowAdapter;
pub use thiserror_adapter::ThisErrorAdapter;

/// Trait for converting to `AppError`.
pub trait IntoAppError {
    /// Convert to `AppError`.
    fn into_app_error(self) -> crate::domain::AppError;
}

/// Trait for converting from `AppError`.
pub trait FromAppError: Sized {
    /// Convert from `AppError`.
    fn from_app_error(error: crate::domain::AppError) -> Self;
}

impl IntoAppError for crate::domain::AppError {
    fn into_app_error(self) -> crate::domain::AppError {
        self
    }
}

impl FromAppError for crate::domain::AppError {
    fn from_app_error(error: crate::domain::AppError) -> Self {
        error
    }
}
