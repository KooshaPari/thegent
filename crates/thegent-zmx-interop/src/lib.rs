//! thegent-zmx-interop — Zig-Rust C ABI interop POC
//!
//! # Overview
//!
//! This crate demonstrates how Rust calls Zig code via the C ABI without
//! spawning a subprocess.  The design has two layers:
//!
//! ```text
//! ┌─────────────────────────────────────────────────────┐
//! │  Safe Rust API (pub fns in this module)              │
//! │  list_sessions(), attach_session(), create_session() │
//! └──────────────────────┬──────────────────────────────┘
//!                        │
//!              feature = zmx-native?
//!                   ┌───┴───┐
//!                  YES      NO
//!                   │       │
//!            ┌──────▼──┐  ┌─▼────────────────┐
//!            │ ffi mod  │  │ subprocess mod    │
//!            │ extern C │  │ Command("zmx")    │
//!            └──────────┘  └──────────────────┘
//! ```
//!
//! # Feature flags
//!
//! | Feature      | Default | Effect                                          |
//! |:-------------|:-------:|:------------------------------------------------|
//! | `zmx-native` | off     | Enables C ABI FFI; requires `libzmx` at link time |
//!
//! When `zmx-native` is **off** (the default), all public functions use a
//! subprocess fallback that shells out to the `zmx` CLI binary.  This allows
//! the crate to compile and run on any machine, whether or not zmx is
//! installed as a shared library.
//!
//! # Safety
//!
//! All `unsafe` FFI calls are contained in [`ffi`] and wrapped by the safe
//! functions exported from this module.  Callers never need `unsafe`.

#[cfg(feature = "zmx-native")]
use std::ffi::CString;

pub use error::ZmxError;

mod error;

/// Versioned ABI contract for the Zig interop surface (integer form).
pub const ABI_CONTRACT_VERSION: u32 = 1;

/// Semantic version string for the Zig ABI contract.
///
/// Must match the `"version"` field in `contracts/runtime/zig_abi_contract_v1.json`.
pub const ZMX_ABI_CONTRACT_VERSION: &str = "1.0.0";

/// Validate that the compiled-in ABI contract version matches the expected value.
///
/// Call this at startup or in CI to assert that the Rust crate and the JSON
/// contract file are in sync.
///
/// # Errors
///
/// Returns `Err(String)` when the versions do not match.
pub fn check_abi_contract_version(expected: &str) -> Result<(), String> {
    if ZMX_ABI_CONTRACT_VERSION == expected {
        Ok(())
    } else {
        Err(format!(
            "ABI contract version mismatch: compiled-in version is {:?}, expected {:?}",
            ZMX_ABI_CONTRACT_VERSION, expected
        ))
    }
}

/// C ABI declarations for the zmx Zig library.
///
/// These symbols are exported by zmx using Zig's `export fn` keyword which
/// gives them C ABI calling convention and no name mangling.
///
/// The declarations here mirror the expected zmx C ABI surface:
///
/// ```zig
/// // In zmx (Zig):
/// export fn zmx_list(buf: [*]u8, len: usize) i32 { ... }
/// export fn zmx_attach(name: [*:0]const u8) i32 { ... }
/// export fn zmx_create(name: [*:0]const u8, cmd: [*:0]const u8) i32 { ... }
/// ```
#[cfg(feature = "zmx-native")]
mod ffi {
    extern "C" {
        /// List active zmx sessions.
        ///
        /// # Parameters
        /// - `buf`: writable buffer that receives newline-delimited session names
        /// - `len`: capacity of `buf` in bytes
        ///
        /// # Returns
        /// Number of bytes written (>= 0) or a negative errno-style error code.
        pub fn zmx_list(buf: *mut u8, len: usize) -> i32;

        /// Attach to an existing zmx session by name.
        ///
        /// # Parameters
        /// - `name`: NUL-terminated session name
        ///
        /// # Returns
        /// 0 on success or a negative errno-style error code.
        pub fn zmx_attach(name: *const u8) -> i32;

        /// Create a new zmx session with an initial command.
        ///
        /// # Parameters
        /// - `name`: NUL-terminated session name
        /// - `cmd`:  NUL-terminated command string (e.g. `"bash"`)
        ///
        /// # Returns
        /// 0 on success or a negative errno-style error code.
        pub fn zmx_create(name: *const u8, cmd: *const u8) -> i32;
    }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/// List all active zmx sessions.
///
/// Returns a `Vec<String>` of session names.
///
/// # Errors
/// Returns [`ZmxError`] if the underlying call fails or the output cannot
/// be parsed as UTF-8.
pub fn list_sessions() -> Result<Vec<String>, ZmxError> {
    #[cfg(feature = "zmx-native")]
    {
        native::list_sessions()
    }
    #[cfg(not(feature = "zmx-native"))]
    {
        subprocess::list_sessions()
    }
}

/// Attach to an existing zmx session by name.
///
/// # Errors
/// Returns [`ZmxError`] if the session does not exist or the attach fails.
pub fn attach_session(name: &str) -> Result<(), ZmxError> {
    #[cfg(feature = "zmx-native")]
    {
        native::attach_session(name)
    }
    #[cfg(not(feature = "zmx-native"))]
    {
        subprocess::attach_session(name)
    }
}

/// Create a new zmx session with the given name and initial command.
///
/// # Errors
/// Returns [`ZmxError`] if the session already exists or creation fails.
pub fn create_session(name: &str, cmd: &str) -> Result<(), ZmxError> {
    #[cfg(feature = "zmx-native")]
    {
        native::create_session(name, cmd)
    }
    #[cfg(not(feature = "zmx-native"))]
    {
        subprocess::create_session(name, cmd)
    }
}

// ---------------------------------------------------------------------------
// Native (C ABI / FFI) implementation — only compiled with `zmx-native`
// ---------------------------------------------------------------------------

#[cfg(feature = "zmx-native")]
mod native {
    use super::{ZmxError, ffi};
    use std::ffi::CString;

    const LIST_BUF_SIZE: usize = 65_536; // 64 KiB — sufficient for many sessions

    pub fn list_sessions() -> Result<Vec<String>, ZmxError> {
        let mut buf = vec![0u8; LIST_BUF_SIZE];

        // SAFETY: buf is a valid, writable allocation of exactly LIST_BUF_SIZE
        // bytes.  zmx_list writes at most `len` bytes and NUL-terminates.
        let written = unsafe { ffi::zmx_list(buf.as_mut_ptr(), buf.len()) };

        if written < 0 {
            return Err(ZmxError::NativeError {
                code: written,
                context: "zmx_list".into(),
            });
        }

        let output = std::str::from_utf8(&buf[..written as usize])
            .map_err(|e| ZmxError::Utf8 { source: e })?;

        Ok(parse_session_list(output))
    }

    pub fn attach_session(name: &str) -> Result<(), ZmxError> {
        let cname = CString::new(name).map_err(|_| ZmxError::NulInName)?;

        // SAFETY: cname is a valid NUL-terminated C string whose lifetime
        // covers the duration of this call.
        let rc = unsafe { ffi::zmx_attach(cname.as_ptr() as *const u8) };

        if rc != 0 {
            Err(ZmxError::NativeError {
                code: rc,
                context: format!("zmx_attach({name})"),
            })
        } else {
            Ok(())
        }
    }

    pub fn create_session(name: &str, cmd: &str) -> Result<(), ZmxError> {
        let cname = CString::new(name).map_err(|_| ZmxError::NulInName)?;
        let ccmd = CString::new(cmd).map_err(|_| ZmxError::NulInName)?;

        // SAFETY: both CStrings are valid NUL-terminated C strings.
        let rc = unsafe {
            ffi::zmx_create(
                cname.as_ptr() as *const u8,
                ccmd.as_ptr() as *const u8,
            )
        };

        if rc != 0 {
            Err(ZmxError::NativeError {
                code: rc,
                context: format!("zmx_create({name}, {cmd})"),
            })
        } else {
            Ok(())
        }
    }
}

// ---------------------------------------------------------------------------
// Subprocess fallback implementation — compiled when `zmx-native` is absent
// ---------------------------------------------------------------------------

#[cfg(not(feature = "zmx-native"))]
mod subprocess {
    use super::ZmxError;
    use std::process::Command;

    pub fn list_sessions() -> Result<Vec<String>, ZmxError> {
        let output = Command::new("zmx")
            .arg("list")
            .output()
            .map_err(|e| ZmxError::Subprocess {
                source: e,
                context: "zmx list".into(),
            })?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr).into_owned();
            return Err(ZmxError::SubprocessFailed {
                exit_code: output.status.code(),
                stderr,
            });
        }

        let stdout = String::from_utf8(output.stdout)
            .map_err(|e| ZmxError::Utf8 { source: e.utf8_error() })?;

        Ok(super::parse_session_list(&stdout))
    }

    pub fn attach_session(name: &str) -> Result<(), ZmxError> {
        let status = Command::new("zmx")
            .args(["attach", name])
            .status()
            .map_err(|e| ZmxError::Subprocess {
                source: e,
                context: format!("zmx attach {name}"),
            })?;

        if status.success() {
            Ok(())
        } else {
            Err(ZmxError::SubprocessFailed {
                exit_code: status.code(),
                stderr: String::new(),
            })
        }
    }

    pub fn create_session(name: &str, cmd: &str) -> Result<(), ZmxError> {
        let status = Command::new("zmx")
            .args(["new", name, cmd])
            .status()
            .map_err(|e| ZmxError::Subprocess {
                source: e,
                context: format!("zmx new {name} {cmd}"),
            })?;

        if status.success() {
            Ok(())
        } else {
            Err(ZmxError::SubprocessFailed {
                exit_code: status.code(),
                stderr: String::new(),
            })
        }
    }
}

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------

/// Parse newline-delimited session output into a `Vec<String>`.
///
/// Empty lines are ignored.  Trailing whitespace is stripped from each name.
fn parse_session_list(output: &str) -> Vec<String> {
    output
        .lines()
        .map(str::trim)
        .filter(|s| !s.is_empty())
        .map(String::from)
        .collect()
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    // --- parse_session_list ------------------------------------------------

    #[test]
    fn parse_empty_string_returns_empty_vec() {
        assert!(parse_session_list("").is_empty());
    }

    #[test]
    fn parse_single_session() {
        let result = parse_session_list("my-session\n");
        assert_eq!(result, vec!["my-session"]);
    }

    #[test]
    fn parse_multiple_sessions() {
        let result = parse_session_list("alpha\nbeta\ngamma\n");
        assert_eq!(result, vec!["alpha", "beta", "gamma"]);
    }

    #[test]
    fn parse_filters_blank_lines() {
        let result = parse_session_list("alpha\n\nbeta\n\n");
        assert_eq!(result, vec!["alpha", "beta"]);
    }

    #[test]
    fn parse_trims_whitespace() {
        let result = parse_session_list("  alpha  \n  beta  \n");
        assert_eq!(result, vec!["alpha", "beta"]);
    }

    #[test]
    fn abi_contract_version_is_non_zero() {
        assert!(ABI_CONTRACT_VERSION > 0);
    }

    // --- WL-132 B90-W2-B3: ZMX_ABI_CONTRACT_VERSION string assertions ------

    #[test]
    fn test_zmx_abi_contract_version_is_semver_string() {
        // Must be a non-empty string in X.Y.Z form.
        let parts: Vec<&str> = ZMX_ABI_CONTRACT_VERSION.split('.').collect();
        assert_eq!(
            parts.len(),
            3,
            "ZMX_ABI_CONTRACT_VERSION must be X.Y.Z; got {:?}",
            ZMX_ABI_CONTRACT_VERSION
        );
        for part in &parts {
            assert!(
                part.parse::<u32>().is_ok(),
                "Each part must be a non-negative integer; got {:?}",
                part
            );
        }
    }

    #[test]
    fn test_abi_version_matches_contract() {
        // The version embedded in the binary must match what the JSON contract
        // declares.  In CI the contract file is at
        // contracts/runtime/zig_abi_contract_v1.json with "version": "1.0.0".
        let expected = "1.0.0";
        assert_eq!(
            check_abi_contract_version(expected),
            Ok(()),
            "ZMX_ABI_CONTRACT_VERSION does not match the expected contract version {expected:?}"
        );
    }

    #[test]
    fn test_check_abi_contract_version_ok_on_match() {
        assert!(check_abi_contract_version(ZMX_ABI_CONTRACT_VERSION).is_ok());
    }

    #[test]
    fn test_check_abi_contract_version_err_on_mismatch() {
        let result = check_abi_contract_version("9.9.9");
        assert!(result.is_err(), "Expected Err on version mismatch");
        let msg = result.unwrap_err();
        assert!(
            msg.contains("9.9.9"),
            "Error message should mention the expected version"
        );
    }

    // --- subprocess fallback (only when zmx-native is NOT enabled) ---------

    #[cfg(not(feature = "zmx-native"))]
    #[test]
    fn list_sessions_returns_error_when_zmx_missing() {
        // zmx is not installed in CI / dev environments.
        // The subprocess path must return an error, not panic.
        let result = list_sessions();
        assert!(
            result.is_err(),
            "expected error when zmx binary is unavailable"
        );
    }

    #[cfg(not(feature = "zmx-native"))]
    #[test]
    fn attach_session_returns_error_when_zmx_missing() {
        let result = attach_session("nonexistent");
        assert!(result.is_err());
    }

    #[cfg(not(feature = "zmx-native"))]
    #[test]
    fn create_session_returns_error_when_zmx_missing() {
        let result = create_session("test-session", "bash");
        assert!(result.is_err());
    }

    // --- native FFI tests (only when zmx-native IS enabled) ----------------
    //
    // These are integration tests that require libzmx to be available.
    // Run with: cargo test --features zmx-native
    //
    // They are gated behind #[ignore] so they do not block CI when zmx is
    // unavailable.  Remove #[ignore] in environments where zmx is installed.

    #[cfg(feature = "zmx-native")]
    #[test]
    #[ignore = "requires libzmx installed; run with --include-ignored in zmx environments"]
    fn native_list_sessions_does_not_panic() {
        // If zmx-native is enabled AND zmx is present, list_sessions must
        // return Ok or a structured ZmxError — never panic.
        let _ = list_sessions(); // result may be Ok or Err
    }

    #[cfg(feature = "zmx-native")]
    #[test]
    #[ignore = "requires libzmx installed"]
    fn native_create_and_list_roundtrip() {
        // Create a session named "rust-poc-test", list sessions, assert it appears.
        create_session("rust-poc-test", "true").expect("create_session failed");
        let sessions = list_sessions().expect("list_sessions failed");
        assert!(
            sessions.iter().any(|s| s == "rust-poc-test"),
            "session 'rust-poc-test' not found in: {sessions:?}"
        );
    }
}
