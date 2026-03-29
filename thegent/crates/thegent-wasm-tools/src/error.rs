//! Error types for thegent-wasm-tools.

use thiserror::Error;

/// Errors that can occur when working with Wasm tools.
#[derive(Debug, Error)]
pub enum WasmToolsError {
    /// The Wasm file was not found.
    #[error("Wasm file not found: {0}")]
    FileNotFound(String),

    /// Invalid Wasm binary format.
    #[error("Invalid Wasm binary: {0}")]
    InvalidWasm(String),

    /// Plugin initialization failed.
    #[error("Plugin initialization failed: {0}")]
    InitFailed(String),

    /// Plugin execution failed.
    #[error("Plugin execution failed: {0}")]
    ExecutionFailed(String),

    /// Resource limit exceeded.
    #[error("Resource limit exceeded: {0}")]
    ResourceLimitExceeded(String),

    /// Tool manifest is invalid.
    #[error("Invalid manifest: {0}")]
    InvalidManifest(String),

    /// Build error.
    #[error("Build error: {0}")]
    BuildError(String),

    /// Zig not found or incorrect version.
    #[error("Zig not available: {0}")]
    ZigNotAvailable(String),
}
