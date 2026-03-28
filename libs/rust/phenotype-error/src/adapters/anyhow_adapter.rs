//! Anyhow adapter - Compatibility with anyhow crate.
//!
//! This adapter provides conversion between `AppError` and `anyhow::Error`.

use crate::domain::app_error::AppError;
use crate::domain::error_code::ErrorCode;
use crate::adapters::{FromAppError, IntoAppError};

impl IntoAppError for anyhow::Error {
    fn into_app_error(self) -> AppError {
        // Try to downcast to AppError
        if let Some(app_error) = self.downcast_ref::<AppError>() {
            return app_error.clone();
        }

        // Otherwise, create a generic error
        AppError::with_source(
            ErrorCode::Unknown,
            self.to_string(),
            self,
        )
    }
}

impl FromAppError for anyhow::Error {
    fn from_app_error(error: AppError) -> Self {
        anyhow::Error::msg(error.message().to_string())
    }
}

/// Extension trait for converting anyhow to AppError.
pub trait AnyhowExt {
    /// Convert anyhow::Error to AppError.
    fn into_app_error(self) -> AppError;
}

impl AnyhowExt for anyhow::Error {
    fn into_app_error(self) -> AppError {
        IntoAppError::into_app_error(self)
    }
}

/// Extension trait for converting AppError to anyhow.
pub trait AppErrorAnyhowExt {
    /// Convert AppError to anyhow::Error.
    fn into_anyhow(self) -> anyhow::Error;
}

impl AppErrorAnyhowExt for AppError {
    fn into_anyhow(self) -> anyhow::Error {
        anyhow::Error::msg(self.message().to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::{Context, Result as AnyhowResult};

    #[test]
    fn test_anyhow_to_apperror() {
        let anyhow_err = anyhow::Error::new(std::io::Error::new(
            std::io::ErrorKind::NotFound,
            "file not found",
        ));

        let app_error = anyhow_err.into_app_error();
        assert_eq!(app_error.code(), ErrorCode::Unknown);
    }

    #[test]
    fn test_anyhow_with_context() {
        let anyhow_err: AnyhowResult<()> = Err(anyhow::Error::new(
            std::io::Error::new(std::io::ErrorKind::NotFound, "file not found"),
        ))
        .context("Additional context");

        if let Err(e) = anyhow_err {
            let app_error = e.into_app_error();
            // Should preserve the anyhow context
            assert!(!app_error.message().is_empty());
        }
    }
}
