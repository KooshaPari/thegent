//! Application layer - Error handling patterns and utilities

use crate::{Error, ErrorKind, ContextEntry, ContextValue};

/// Context builder for fluent error creation
pub struct ErrorBuilder {
    kind: ErrorKind,
    message: String,
    context: Vec<ContextEntry>,
}

impl ErrorBuilder {
    /// Create a new error builder
    pub fn new(kind: ErrorKind, message: impl Into<String>) -> Self {
        Self {
            kind,
            message: message.into(),
            context: Vec::new(),
        }
    }

    /// Add context
    pub fn context<C: Into<ContextValue>>(mut self, key: impl Into<String>, value: C) -> Self {
        self.context.push(ContextEntry {
            key: key.into(),
            value: value.into(),
        });
        self
    }

    /// Build the error
    pub fn build(self) -> Error {
        let mut err = Error::new(self.kind, self.message);
        for entry in self.context {
            err = err.with_context(entry.key, entry.value);
        }
        err
    }
}

/// Error extension traits for Result type
pub trait ResultExt<T> {
    /// Map the error kind
    fn map_err_kind(self, kind: ErrorKind) -> Result<T, Error>;

    /// Add context to error
    fn with_context<C: Into<ContextValue>>(self, key: impl Into<String>, value: C) -> Result<T, Error>;

    /// Map to internal error
    fn internal(self) -> Result<T, Error>;

    /// Map to not found error
    fn not_found(self) -> Result<T, Error>;

    /// Map to validation error
    fn validation(self) -> Result<T, Error>;
}

impl<T, E: Into<Error>> ResultExt<T> for Result<T, E> {
    fn map_err_kind(self, kind: ErrorKind) -> Result<T, Error> {
        self.map_err(|e| {
            let err: Error = e.into();
            Error::new(kind, err.message()).with_context("original_kind", err.kind().code())
        })
    }

    fn with_context<C: Into<ContextValue>>(self, key: impl Into<String>, value: C) -> Result<T, Error> {
        self.map_err(|e| {
            let err: Error = e.into();
            err.with_context(key, value)
        })
    }

    fn internal(self) -> Result<T, Error> {
        self.map_err_kind(ErrorKind::Internal)
    }

    fn not_found(self) -> Result<T, Error> {
        self.map_err_kind(ErrorKind::NotFound)
    }

    fn validation(self) -> Result<T, Error> {
        self.map_err_kind(ErrorKind::Validation)
    }
}

/// Macro for creating errors with context
#[macro_export]
macro_rules! error_context {
    ($kind:expr, $msg:expr; $($key:expr => $value:expr),* $(,)?) => {{
        let mut err = $crate::Error::new($kind, $msg);
        $(err = err.with_context($key, $value);)*
        err
    }};
}

/// Macro for error chaining
#[macro_export]
macro_rules! error_chain {
    ($kind:expr, $msg:expr) => {{
        $crate::Error::new($kind, $msg)
    }};
    ($kind:expr, $msg:expr; $($prev:expr),* $(,)?) => {{
        let mut err = $crate::Error::new($kind, $msg);
        $(err = err.cause($prev);)*
        err
    }};
}
