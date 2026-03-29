//! thegent-wasm-tools — Zig SDK for building Wasm tools with Extism
//!
//! # Overview
//!
//! This crate provides a foundation for building Wasm-based tools using Zig
//! that integrate with the Extism plugin system. It demonstrates the pattern
//! for creating atomic, sandboxed tools.
//!
//! ## Tool Structure
//!
//! ```text
//! ┌─────────────────────────────────────────────────────┐
//! │  Zig Tool (compiled to Wasm)                         │
//! │  - Exports standard interface                        │
//! │  - Uses Extism host functions for capabilities       │
//! └─────────────────────────────────────────────────────┘
//!                        │
//!                        ▼
//! ┌─────────────────────────────────────────────────────┐
//! │  Extism Runtime (Python/Rust)                        │
//! │  - Manages plugin lifecycle                          │
//! │  - Enforces resource limits                          │
//! │  - Provides host functions                           │
//! └─────────────────────────────────────────────────────┘
//! ```
//!
//! # Usage
//!
//! Build your Zig tool with:
//! ```bash
//! zig build -target wasm32-wasi release
//! ```
//!
//! Then use with the Python plugin manager:
//! ```python
//! from thegent.infra.wasm_plugin import ExtismPlugin, WasmPluginMetadata
//!
//! plugin = ExtismPlugin(Path("my_tool.wasm"), metadata)
//! result = plugin.execute(input_data)
//! ```

pub use error::WasmToolsError;

mod error;

/// Plugin interface versions supported by this SDK.
pub mod version {
    /// Current SDK version.
    pub const SDK_VERSION: &str = env!("CARGO_PKG_VERSION");

    /// Minimum supported plugin interface version.
    pub const MIN_PLUGIN_VERSION: &str = "0.1.0";

    /// Maximum supported plugin interface version.
    pub const MAX_PLUGIN_VERSION: &str = "0.1.0";
}

/// Standard capabilities that tools can declare.
pub mod capability {
    /// HTTP client capability — allows making HTTP requests.
    pub const HTTP_CLIENT: &str = "http_client";

    /// File read capability — allows reading files.
    pub const FILE_READ: &str = "file_read";

    /// File write capability — allows writing files.
    pub const FILE_WRITE: &str = "file_write";

    /// Environment variable capability — allows reading env vars.
    pub const ENVIRONMENT: &str = "environment";

    /// Clock capability — allows reading system time.
    pub const CLOCK: &str = "clock";

    /// Random capability — allows generating random numbers.
    pub const RANDOM: &str = "random";
}

/// Standard function names that tools must export.
pub mod function {
    /// Main entry point function that Extism calls.
    pub const RUN: &str = "run";

    /// Optional initialization function.
    pub const INIT: &str = "init";

    /// Optional cleanup function.
    pub const CLEANUP: &str = "cleanup";

    /// Optional health check function.
    pub const HEALTH: &str = "health";
}

/// Tool manifest fields that must be included in the tool's metadata.
///
/// This is the JSON structure that tools should provide for discovery:
/// ```json
/// {
///   "name": "my-tool",
///   "version": "0.1.0",
///   "description": "My custom tool",
///   "author": "tool-author",
///   "capabilities": ["file_read"],
///   "entry_point": "run"
/// }
#[derive(Debug, Clone, PartialEq)]
pub struct ToolManifest {
    /// Tool name (must be unique).
    pub name: String,
    /// Tool version (semver).
    pub version: String,
    /// Human-readable description.
    pub description: String,
    /// Tool author.
    pub author: String,
    /// List of required capabilities.
    pub capabilities: Vec<String>,
    /// Entry point function name (default: "run").
    pub entry_point: String,
}

impl Default for ToolManifest {
    fn default() -> Self {
        Self {
            name: String::new(),
            version: "0.1.0".to_string(),
            description: String::new(),
            author: String::new(),
            capabilities: Vec::new(),
            entry_point: function::RUN.to_string(),
        }
    }
}

/// Result type for tool operations.
#[derive(Debug, Clone, PartialEq)]
pub struct ToolResult {
    /// Whether the operation was successful.
    pub success: bool,
    /// Output data (if successful).
    pub output: Option<Vec<u8>>,
    /// Error message (if failed).
    pub error: Option<String>,
    /// Execution time in milliseconds.
    pub duration_ms: u64,
}

impl ToolResult {
    /// Create a successful result.
    pub fn success(output: Vec<u8>, duration_ms: u64) -> Self {
        Self {
            success: true,
            output: Some(output),
            error: None,
            duration_ms,
        }
    }

    /// Create an error result.
    pub fn error(message: String, duration_ms: u64) -> Self {
        Self {
            success: false,
            output: None,
            error: Some(message),
            duration_ms,
        }
    }
}

/// Build configuration for Zig Wasm tools.
///
/// This defines the build targets and settings used when compiling
/// Zig code to Wasm for use with Extism.
#[derive(Debug, Clone)]
pub struct BuildConfig {
    /// Target architecture (default: wasm32-wasi).
    pub target: String,
    /// Optimization mode (default: ReleaseFast).
    pub optimization: String,
    /// Whether to include debug info.
    pub debug_info: bool,
    /// Single-threaded Wasm (for better compatibility).
    pub single_threaded: bool,
}

impl Default for BuildConfig {
    fn default() -> Self {
        Self {
            target: "wasm32-wasi".to_string(),
            optimization: "ReleaseFast".to_string(),
            debug_info: false,
            single_threaded: true,
        }
    }
}

impl BuildConfig {
    /// Get the Zig build command for this config.
    pub fn zig_build_command(&self, source_path: &str, output_path: &str) -> Vec<String> {
        let mut cmd = vec![
            "zig".to_string(),
            "build".to_string(),
            "-target".to_string(),
            self.target.clone(),
            "-O".to_string(),
            self.optimization.clone(),
            "-femit-bin=".to_string(),
            output_path.to_string(),
        ];

        if self.debug_info {
            cmd.push("-fdebug-info-native".to_string());
        }

        cmd.push(source_path.to_string());

        cmd
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tool_manifest_default() {
        let manifest = ToolManifest::default();
        assert_eq!(manifest.version, "0.1.0");
        assert_eq!(manifest.entry_point, function::RUN);
    }

    #[test]
    fn tool_result_success() {
        let result = ToolResult::success(b"hello".to_vec(), 100);
        assert!(result.success);
        assert_eq!(result.output, Some(b"hello".to_vec()));
        assert!(result.error.is_none());
        assert_eq!(result.duration_ms, 100);
    }

    #[test]
    fn tool_result_error() {
        let result = ToolResult::error("something went wrong".to_string(), 50);
        assert!(!result.success);
        assert!(result.output.is_none());
        assert_eq!(result.error, Some("something went wrong".to_string()));
        assert_eq!(result.duration_ms, 50);
    }

    #[test]
    fn build_config_default() {
        let config = BuildConfig::default();
        assert_eq!(config.target, "wasm32-wasi");
        assert_eq!(config.optimization, "ReleaseFast");
    }

    #[test]
    fn build_config_zig_command() {
        let config = BuildConfig {
            target: "wasm32-wasi".to_string(),
            optimization: "ReleaseSmall".to_string(),
            debug_info: false,
            single_threaded: true,
        };

        let cmd = config.zig_build_command("src/main.zig", "bin/tool.wasm");
        assert!(cmd.contains(&"wasm32-wasi".to_string()));
        assert!(cmd.contains(&"ReleaseSmall".to_string()));
    }
}
