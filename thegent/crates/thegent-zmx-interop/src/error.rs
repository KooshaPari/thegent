//! Error types for the zmx interop crate.

use std::str::Utf8Error;
use thiserror::Error;

/// All errors that can be returned by the zmx interop layer.
#[derive(Debug, Error)]
pub enum ZmxError {
    /// Returned by the native FFI path: zmx returned a non-zero error code.
    #[error("zmx native call failed in '{context}' with code {code}")]
    NativeError {
        /// Errno-style negative error code returned by the zmx C function.
        code: i32,
        /// Human-readable context (function name + arguments).
        context: String,
    },

    /// The session name or command contained a NUL byte, which is invalid
    /// in a C string.
    #[error("session name or command contained a NUL byte, which is invalid for C ABI")]
    NulInName,

    /// The subprocess could not be spawned (e.g. `zmx` not in PATH).
    #[error("failed to spawn zmx subprocess for '{context}': {source}")]
    Subprocess {
        #[source]
        source: std::io::Error,
        context: String,
    },

    /// The subprocess exited with a non-zero status code.
    #[error("zmx subprocess exited with code {exit_code:?}: {stderr}")]
    SubprocessFailed {
        /// Process exit code (`None` if killed by a signal).
        exit_code: Option<i32>,
        /// Captured stderr from the subprocess.
        stderr: String,
    },

    /// The output buffer from zmx contained invalid UTF-8.
    #[error("zmx output contained invalid UTF-8: {source}")]
    Utf8 {
        #[source]
        source: Utf8Error,
    },
}
