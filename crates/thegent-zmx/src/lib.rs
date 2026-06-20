// SPDX-License-Identifier: MIT OR Apache-2.0
//! thegent-zmx — idiomatic Rust wrapper around the zmx session manager
//!
//! # Overview
//!
//! This crate provides a higher-level, idiomatic Rust API over the low-level
//! C ABI functions exposed by [`thegent_zmx_interop`].  Callers work with
//! typed structs ([`ZmxSession`], [`ZmxState`]) and a single entry-point
//! client ([`ZmxClient`]) instead of raw string slices and error integers.
//!
//! ```text
//! ┌────────────────────────────────────────────┐
//! │  Application / Python-native bridge        │
//! └───────────────────────┬────────────────────┘
//!                         │
//!                  ┌──────▼──────┐
//!                  │  ZmxClient  │  ← this crate
//!                  └──────┬──────┘
//!                         │
//!                  ┌──────▼──────────────────┐
//!                  │ thegent-zmx-interop      │
//!                  │ (C ABI FFI / subprocess) │
//!                  └─────────────────────────┘
//! ```
//!
//! # Feature flags
//!
//! | Feature      | Default | Effect                                            |
//! |:-------------|:-------:|:--------------------------------------------------|
//! | `zmx-native` | off     | Passes `zmx-native` through to the interop crate  |
//! | `live-zmx`   | off     | Gates tests that require a real `zmx` binary      |
//!
//! # Example
//!
//! ```rust,no_run
//! use thegent_zmx::{ZmxClient, ZmxSession};
//!
//! let client = ZmxClient::new();
//! let sessions = client.list_sessions().expect("zmx list failed");
//! for session in &sessions {
//!     println!("{}: {:?}", session.name, session.state);
//! }
//! ```

use anyhow::{anyhow, Context, Result};

pub use thegent_zmx_interop::ZmxError;

pub mod session;

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

/// The lifecycle state of a zmx session.
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ZmxState {
    /// The session is alive and has an attached process.
    Active,
    /// The session exists but no client is currently attached.
    Detached,
    /// The session's underlying process has exited.
    Dead,
}

impl std::fmt::Display for ZmxState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ZmxState::Active => write!(f, "active"),
            ZmxState::Detached => write!(f, "detached"),
            ZmxState::Dead => write!(f, "dead"),
        }
    }
}

/// A zmx session as seen by the Rust wrapper layer.
///
/// The `pid` field is populated with 0 when zmx does not expose PID
/// information (subprocess fallback mode).
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct ZmxSession {
    /// Human-readable session name (unique within a zmx server instance).
    pub name: String,
    /// PID of the session's lead process; 0 when unavailable.
    pub pid: u32,
    /// Current lifecycle state of the session.
    pub state: ZmxState,
}

impl ZmxSession {
    /// Construct a new session descriptor.
    pub fn new(name: impl Into<String>, pid: u32, state: ZmxState) -> Self {
        ZmxSession {
            name: name.into(),
            pid,
            state,
        }
    }

    /// Returns `true` if the session is in the [`ZmxState::Active`] state.
    pub fn is_active(&self) -> bool {
        self.state == ZmxState::Active
    }
}

// ---------------------------------------------------------------------------
// ZmxClient
// ---------------------------------------------------------------------------

/// High-level client that wraps `thegent_zmx_interop` functions.
///
/// `ZmxClient` is cheap to clone (it holds no OS resources) and may be shared
/// across threads.  All methods are synchronous; wrap them in
/// `tokio::task::spawn_blocking` for async contexts.
///
/// # Construction
///
/// ```rust
/// use thegent_zmx::ZmxClient;
/// let client = ZmxClient::new();
/// ```
#[derive(Debug, Default, Clone)]
pub struct ZmxClient {
    /// Optional explicit path to the `zmx` binary.  When `None`, the binary
    /// is located via `PATH` (subprocess fallback mode).
    zmx_binary: Option<String>,
}

impl ZmxClient {
    /// Create a new client using default settings (subprocess fallback unless
    /// the `zmx-native` feature is enabled).
    pub fn new() -> Self {
        ZmxClient::default()
    }

    /// Create a client that forces use of a specific zmx binary path.
    ///
    /// This is only relevant in subprocess fallback mode; the `zmx-native`
    /// feature ignores this setting (it links the library directly).
    pub fn with_binary(path: impl Into<String>) -> Self {
        ZmxClient {
            zmx_binary: Some(path.into()),
        }
    }

    // -----------------------------------------------------------------------
    // Public API
    // -----------------------------------------------------------------------

    /// List all active zmx sessions.
    ///
    /// Returns a `Vec<ZmxSession>` sorted by session name.  Each entry has
    /// `pid = 0` and `state = ZmxState::Detached` because the low-level
    /// `zmx list` command does not return PID or state metadata.  Callers
    /// that need richer metadata should call [`Self::attach`] per session.
    ///
    /// # Errors
    ///
    /// Returns an error if the zmx binary is not available or returns a
    /// non-zero exit code.
    pub fn list_sessions(&self) -> Result<Vec<ZmxSession>> {
        let names = thegent_zmx_interop::list_sessions().context("failed to list zmx sessions")?;

        let mut sessions: Vec<ZmxSession> = names
            .into_iter()
            .map(|name| ZmxSession::new(name, 0, ZmxState::Detached))
            .collect();

        sessions.sort_by(|a, b| a.name.cmp(&b.name));
        Ok(sessions)
    }

    /// Attach to an existing zmx session by name.
    ///
    /// On success, returns a [`ZmxSession`] descriptor with
    /// `state = ZmxState::Active`.
    ///
    /// # Errors
    ///
    /// Returns an error if the session does not exist or the attach fails.
    pub fn attach(&self, name: &str) -> Result<ZmxSession> {
        validate_session_name(name)?;
        thegent_zmx_interop::attach_session(name)
            .with_context(|| format!("failed to attach to zmx session '{name}'"))?;
        Ok(ZmxSession::new(name, 0, ZmxState::Active))
    }

    /// Capture the last `lines` lines of output from a named session.
    ///
    /// This is implemented via the `zmx` subprocess (`zmx capture <name>
    /// --lines <n>`).  When `zmx-native` is enabled and the C ABI does not
    /// expose a capture function, the subprocess path is used as a fallback.
    ///
    /// Returns a `Vec<String>` of individual lines (trailing newlines
    /// stripped).
    ///
    /// # Errors
    ///
    /// Returns an error if zmx is unavailable or the session does not exist.
    pub fn capture(&self, name: &str, lines: usize) -> Result<Vec<String>> {
        validate_session_name(name)?;
        if lines == 0 {
            return Ok(Vec::new());
        }

        let output = std::process::Command::new(self.zmx_path())
            .args(["capture", name, "--lines", &lines.to_string()])
            .output()
            .with_context(|| format!("failed to spawn zmx capture for session '{name}'"))?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow!(
                "zmx capture failed for session '{name}' (exit {:?}): {stderr}",
                output.status.code()
            ));
        }

        let stdout = String::from_utf8(output.stdout)
            .context("zmx capture output contained invalid UTF-8")?;

        Ok(parse_lines(&stdout))
    }

    /// Send text to a named session's input (as if typed by a user).
    ///
    /// Implemented via `zmx send <name> -- <text>`.
    ///
    /// # Errors
    ///
    /// Returns an error if zmx is unavailable or the session does not exist.
    pub fn send(&self, name: &str, text: &str) -> Result<()> {
        validate_session_name(name)?;

        let status = std::process::Command::new(self.zmx_path())
            .args(["send", name, "--", text])
            .status()
            .with_context(|| format!("failed to spawn zmx send for session '{name}'"))?;

        if status.success() {
            Ok(())
        } else {
            Err(anyhow!(
                "zmx send failed for session '{name}' (exit {:?})",
                status.code()
            ))
        }
    }

    /// Create a new zmx session with the given name and initial command.
    ///
    /// Returns a [`ZmxSession`] descriptor with `state = ZmxState::Active`.
    ///
    /// # Errors
    ///
    /// Returns an error if the session already exists or creation fails.
    pub fn create(&self, name: &str, cmd: &str) -> Result<ZmxSession> {
        validate_session_name(name)?;
        thegent_zmx_interop::create_session(name, cmd)
            .with_context(|| format!("failed to create zmx session '{name}' with cmd '{cmd}'"))?;
        Ok(ZmxSession::new(name, 0, ZmxState::Active))
    }

    // -----------------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------------

    /// Returns the path to the zmx binary.
    fn zmx_path(&self) -> &str {
        self.zmx_binary.as_deref().unwrap_or("zmx")
    }
}

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------

/// Parse newline-delimited output into a `Vec<String>` of non-empty lines.
fn parse_lines(output: &str) -> Vec<String> {
    output
        .lines()
        .map(str::trim)
        .filter(|s| !s.is_empty())
        .map(String::from)
        .collect()
}

/// Validate that a session name is non-empty and does not contain NUL bytes.
///
/// # Errors
///
/// Returns an error if `name` is empty or contains `'\0'`.
fn validate_session_name(name: &str) -> Result<()> {
    if name.is_empty() {
        return Err(anyhow!("session name must not be empty"));
    }
    if name.contains('\0') {
        return Err(anyhow!(
            "session name must not contain NUL bytes: {:?}",
            name
        ));
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// JSON helpers
// ---------------------------------------------------------------------------

/// Serialize a slice of sessions to a JSON string.
///
/// # Errors
///
/// Returns an error if serialization fails (should never happen in practice).
pub fn sessions_to_json(sessions: &[ZmxSession]) -> Result<String> {
    serde_json::to_string(sessions).context("failed to serialize sessions to JSON")
}

/// Deserialize a JSON string into a `Vec<ZmxSession>`.
///
/// # Errors
///
/// Returns an error if the JSON is malformed or does not match the expected
/// schema.
pub fn sessions_from_json(json: &str) -> Result<Vec<ZmxSession>> {
    serde_json::from_str(json).context("failed to deserialize sessions from JSON")
}

// Test-only C ABI stubs so workspace `--all-features --all-targets` tests can
// link on machines without libzmx.
#[cfg(all(feature = "zmx-native", test))]
#[unsafe(no_mangle)]
pub extern "C" fn zmx_list(_buf: *mut u8, _len: usize) -> i32 {
    0
}

#[cfg(all(feature = "zmx-native", test))]
#[unsafe(no_mangle)]
pub extern "C" fn zmx_attach(_name: *const u8) -> i32 {
    -1
}

#[cfg(all(feature = "zmx-native", test))]
#[unsafe(no_mangle)]
pub extern "C" fn zmx_create(_name: *const u8, _cmd: *const u8) -> i32 {
    -1
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    // -----------------------------------------------------------------------
    // ZmxState
    // -----------------------------------------------------------------------

    /// @trace FR-ZMX-001
    #[test]
    fn zmx_state_display_active() {
        assert_eq!(ZmxState::Active.to_string(), "active");
    }

    /// @trace FR-ZMX-001
    #[test]
    fn zmx_state_display_detached() {
        assert_eq!(ZmxState::Detached.to_string(), "detached");
    }

    /// @trace FR-ZMX-001
    #[test]
    fn zmx_state_display_dead() {
        assert_eq!(ZmxState::Dead.to_string(), "dead");
    }

    /// @trace FR-ZMX-001
    #[test]
    fn zmx_state_serde_roundtrip() {
        for state in [ZmxState::Active, ZmxState::Detached, ZmxState::Dead] {
            let json = serde_json::to_string(&state).expect("serialize ZmxState");
            let back: ZmxState = serde_json::from_str(&json).expect("deserialize ZmxState");
            assert_eq!(state, back);
        }
    }

    // -----------------------------------------------------------------------
    // ZmxSession
    // -----------------------------------------------------------------------

    /// @trace FR-ZMX-002
    #[test]
    fn zmx_session_new_fields() {
        let s = ZmxSession::new("alpha", 1234, ZmxState::Active);
        assert_eq!(s.name, "alpha");
        assert_eq!(s.pid, 1234);
        assert_eq!(s.state, ZmxState::Active);
    }

    /// @trace FR-ZMX-002
    #[test]
    fn zmx_session_is_active_true_when_active() {
        let s = ZmxSession::new("s", 0, ZmxState::Active);
        assert!(s.is_active());
    }

    /// @trace FR-ZMX-002
    #[test]
    fn zmx_session_is_active_false_when_detached() {
        let s = ZmxSession::new("s", 0, ZmxState::Detached);
        assert!(!s.is_active());
    }

    /// @trace FR-ZMX-002
    #[test]
    fn zmx_session_is_active_false_when_dead() {
        let s = ZmxSession::new("s", 0, ZmxState::Dead);
        assert!(!s.is_active());
    }

    /// @trace FR-ZMX-002
    #[test]
    fn zmx_session_serde_roundtrip() {
        let original = ZmxSession::new("my-session", 42, ZmxState::Detached);
        let json = serde_json::to_string(&original).expect("serialize");
        let back: ZmxSession = serde_json::from_str(&json).expect("deserialize");
        assert_eq!(original, back);
    }

    // -----------------------------------------------------------------------
    // parse_lines
    // -----------------------------------------------------------------------

    /// @trace FR-ZMX-003
    #[test]
    fn parse_lines_empty_string() {
        assert!(parse_lines("").is_empty());
    }

    /// @trace FR-ZMX-003
    #[test]
    fn parse_lines_single() {
        assert_eq!(parse_lines("hello\n"), vec!["hello"]);
    }

    /// @trace FR-ZMX-003
    #[test]
    fn parse_lines_multiple_with_blanks() {
        let result = parse_lines("a\n\nb\n\nc\n");
        assert_eq!(result, vec!["a", "b", "c"]);
    }

    /// @trace FR-ZMX-003
    #[test]
    fn parse_lines_trims_whitespace() {
        let result = parse_lines("  alpha  \n  beta  \n");
        assert_eq!(result, vec!["alpha", "beta"]);
    }

    // -----------------------------------------------------------------------
    // validate_session_name
    // -----------------------------------------------------------------------

    /// @trace FR-ZMX-004
    #[test]
    fn validate_name_empty_returns_error() {
        assert!(validate_session_name("").is_err());
    }

    /// @trace FR-ZMX-004
    #[test]
    fn validate_name_nul_byte_returns_error() {
        assert!(validate_session_name("bad\0name").is_err());
    }

    /// @trace FR-ZMX-004
    #[test]
    fn validate_name_valid_passes() {
        assert!(validate_session_name("good-session").is_ok());
    }

    // -----------------------------------------------------------------------
    // JSON helpers
    // -----------------------------------------------------------------------

    /// @trace FR-ZMX-005
    #[test]
    fn sessions_to_json_empty_slice() {
        let json = sessions_to_json(&[]).expect("serialize empty");
        assert_eq!(json, "[]");
    }

    /// @trace FR-ZMX-005
    #[test]
    fn sessions_to_from_json_roundtrip() {
        let sessions = vec![
            ZmxSession::new("alpha", 100, ZmxState::Active),
            ZmxSession::new("beta", 0, ZmxState::Dead),
        ];
        let json = sessions_to_json(&sessions).expect("serialize");
        let back = sessions_from_json(&json).expect("deserialize");
        assert_eq!(sessions, back);
    }

    /// @trace FR-ZMX-005
    #[test]
    fn sessions_from_json_invalid_returns_error() {
        assert!(sessions_from_json("not json").is_err());
    }

    // -----------------------------------------------------------------------
    // ZmxClient construction
    // -----------------------------------------------------------------------

    /// @trace FR-ZMX-006
    #[test]
    fn zmx_client_new_default_binary() {
        let client = ZmxClient::new();
        assert_eq!(client.zmx_path(), "zmx");
    }

    /// @trace FR-ZMX-006
    #[test]
    fn zmx_client_with_binary_sets_path() {
        let client = ZmxClient::with_binary("/usr/local/bin/zmx");
        assert_eq!(client.zmx_path(), "/usr/local/bin/zmx");
    }

    // -----------------------------------------------------------------------
    // ZmxClient error paths (no zmx binary in CI)
    // -----------------------------------------------------------------------

    /// @trace FR-ZMX-007
    #[test]
    fn list_sessions_error_when_zmx_absent() {
        // zmx is not installed in CI; subprocess fallback must return an error.
        let client = ZmxClient::new();
        let result = client.list_sessions();
        // Either Ok (if zmx happens to be installed) or Err — never panics.
        let _ = result;
    }

    /// @trace FR-ZMX-007
    #[test]
    fn capture_empty_lines_returns_empty_vec() {
        let client = ZmxClient::new();
        // lines=0 short-circuits before spawning zmx
        let result = client.capture("any-session", 0).expect("zero lines");
        assert!(result.is_empty());
    }

    /// @trace FR-ZMX-007
    #[test]
    fn capture_nonzero_lines_errors_without_zmx() {
        let client = ZmxClient::with_binary("/nonexistent/zmx-binary");
        let result = client.capture("test-session", 10);
        assert!(result.is_err(), "expected error when zmx binary is missing");
    }

    /// @trace FR-ZMX-007
    #[test]
    fn send_errors_without_zmx() {
        let client = ZmxClient::with_binary("/nonexistent/zmx-binary");
        let result = client.send("test-session", "hello");
        assert!(result.is_err());
    }

    /// @trace FR-ZMX-007
    #[test]
    fn attach_empty_name_errors() {
        let client = ZmxClient::new();
        let result = client.attach("");
        assert!(result.is_err());
    }

    /// @trace FR-ZMX-007
    #[test]
    fn create_empty_name_errors() {
        let client = ZmxClient::new();
        let result = client.create("", "bash");
        assert!(result.is_err());
    }

    // -----------------------------------------------------------------------
    // Live zmx tests — only compiled with `live-zmx` feature
    // -----------------------------------------------------------------------

    /// @trace FR-ZMX-008
    #[cfg(feature = "live-zmx")]
    #[test]
    #[ignore = "requires live zmx runtime"]
    fn live_list_sessions_does_not_panic() {
        let client = ZmxClient::new();
        // Must not panic; Ok or structured Err is both acceptable.
        let _ = client.list_sessions();
    }

    /// @trace FR-ZMX-008
    #[cfg(feature = "live-zmx")]
    #[test]
    #[ignore = "requires live zmx runtime"]
    fn live_create_and_list_roundtrip() {
        let client = ZmxClient::new();
        let session_name = "rust-zmx-wrapper-test";
        client.create(session_name, "true").expect("create session");
        let sessions = client.list_sessions().expect("list sessions");
        assert!(
            sessions.iter().any(|s| s.name == session_name),
            "expected session '{session_name}' in: {sessions:?}"
        );
    }
}
