//! Prewarm and Cache Precomputation
//!
//! This module handles prewarming of caches and shared data structures
//! for improved hook performance. It computes expensive operations once
//! and caches the results for subsequent use.
#![allow(clippy::needless_borrows_for_generic_args, dead_code)]

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum PrewarmError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("Invalid cache directory: {0}")]
    InvalidCacheDir(String),
    #[error("Command execution failed: {0}")]
    CommandFailed(String),
}

pub type Result<T> = std::result::Result<T, PrewarmError>;

/// Metadata about prewarmed caches
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrewarmMetadata {
    /// Timestamp of when cache was generated
    pub timestamp: u64,
    /// TTL in seconds
    pub ttl_seconds: u64,
    /// Size in bytes
    pub size_bytes: u64,
    /// Component name
    pub component: String,
    /// Version
    pub version: String,
}

/// Shared project data cache
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SharedDataCache {
    /// Project root directory
    pub project_root: String,
    /// Git head SHA
    pub head_sha: String,
    /// List of all Python files
    pub python_files: Vec<String>,
    /// List of all test files
    pub test_files: Vec<String>,
    /// List of all source files
    pub source_files: Vec<String>,
    /// Metadata
    pub metadata: PrewarmMetadata,
}

/// Ruff configuration and results cache
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuffCache {
    /// Ruff version
    pub version: String,
    /// Configuration path
    pub config_path: Option<String>,
    /// Cached lint rules
    pub rules: Vec<String>,
    /// Cached format config
    pub format_config: serde_json::Value,
    /// Metadata
    pub metadata: PrewarmMetadata,
}

/// Shellcheck configuration cache
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShellcheckCache {
    /// Shellcheck version
    pub version: String,
    /// Enabled checks
    pub enabled_checks: Vec<String>,
    /// Excluded errors
    pub excluded_errors: Vec<String>,
    /// Metadata
    pub metadata: PrewarmMetadata,
}

/// System information cache
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemInfoCache {
    /// OS type
    pub os: String,
    /// Architecture
    pub arch: String,
    /// Python version
    pub python_version: String,
    /// Node version
    pub node_version: Option<String>,
    /// Rust version
    pub rust_version: Option<String>,
    /// Available tools
    pub available_tools: Vec<String>,
    /// Metadata
    pub metadata: PrewarmMetadata,
}

/// Prewarming manager
pub struct PrewarmManager {
    cache_dir: PathBuf,
}

impl PrewarmManager {
    /// Create a new prewarming manager
    pub fn new(cache_dir: impl AsRef<Path>) -> Result<Self> {
        let cache_dir = cache_dir.as_ref().to_path_buf();
        fs::create_dir_all(&cache_dir)?;
        Ok(PrewarmManager { cache_dir })
    }

    /// Get cache directory
    pub fn cache_dir(&self) -> &Path {
        &self.cache_dir
    }

    /// Prewarm all caches
    pub fn prewarm_all(&self, project_dir: &Path) -> Result<PrewarmReport> {
        let mut report = PrewarmReport::new();

        // Prewarm shared data
        match self.prewarm_shared_data(project_dir) {
            Ok(_) => report.successful.push("shared-data".to_string()),
            Err(e) => report.errors.push(format!("shared-data: {}", e)),
        }

        // Prewarm ruff
        match self.prewarm_ruff(project_dir) {
            Ok(_) => report.successful.push("ruff".to_string()),
            Err(e) => report.errors.push(format!("ruff: {}", e)),
        }

        // Prewarm shellcheck
        match self.prewarm_shellcheck(project_dir) {
            Ok(_) => report.successful.push("shellcheck".to_string()),
            Err(e) => report.errors.push(format!("shellcheck: {}", e)),
        }

        // Prewarm system info
        match self.prewarm_system_info() {
            Ok(_) => report.successful.push("system-info".to_string()),
            Err(e) => report.errors.push(format!("system-info: {}", e)),
        }

        Ok(report)
    }

    /// Prewarm shared project data
    pub fn prewarm_shared_data(&self, project_dir: &Path) -> Result<SharedDataCache> {
        // Get git head SHA
        let head_sha = self.get_git_head_sha(project_dir).unwrap_or_default();

        // Scan for file types
        let python_files = self.find_files(project_dir, &[".py"])?;
        let test_files =
            self.find_files(project_dir, &["test_", "_test.py", ".test.ts", ".test.tsx"])?;
        let source_files = self.find_files(project_dir, &[".py", ".rs", ".ts", ".tsx", ".js"])?;

        let cache = SharedDataCache {
            project_root: project_dir.to_string_lossy().to_string(),
            head_sha,
            python_files,
            test_files,
            source_files,
            metadata: self.create_metadata("shared-data", "1.0"),
        };

        // Write to cache
        self.write_cache("shared-data.json", &cache)?;

        Ok(cache)
    }

    /// Prewarm ruff configuration
    pub fn prewarm_ruff(&self, project_dir: &Path) -> Result<RuffCache> {
        let version = self.get_tool_version("ruff").unwrap_or_default();
        let config_path = self.find_config_file(project_dir, &["ruff.toml", "pyproject.toml"]);

        let cache = RuffCache {
            version,
            config_path,
            rules: vec![],
            format_config: serde_json::json!({}),
            metadata: self.create_metadata("ruff", "1.0"),
        };

        self.write_cache("ruff.json", &cache)?;
        Ok(cache)
    }

    /// Prewarm shellcheck configuration
    pub fn prewarm_shellcheck(&self, project_dir: &Path) -> Result<ShellcheckCache> {
        let version = self.get_tool_version("shellcheck").unwrap_or_default();
        let _config_path = self.find_config_file(project_dir, &[".shellcheckrc"]);

        let cache = ShellcheckCache {
            version,
            enabled_checks: vec![],
            excluded_errors: vec![],
            metadata: self.create_metadata("shellcheck", "1.0"),
        };

        self.write_cache("shellcheck.json", &cache)?;
        Ok(cache)
    }

    /// Prewarm system information
    pub fn prewarm_system_info(&self) -> Result<SystemInfoCache> {
        let cache = SystemInfoCache {
            os: std::env::consts::OS.to_string(),
            arch: std::env::consts::ARCH.to_string(),
            python_version: self.get_tool_version("python").unwrap_or_default(),
            node_version: self.get_tool_version("node").ok(),
            rust_version: self.get_tool_version("rustc").ok(),
            available_tools: self.scan_available_tools(),
            metadata: self.create_metadata("system-info", "1.0"),
        };

        self.write_cache("system-info.json", &cache)?;
        Ok(cache)
    }

    // Helper methods

    fn find_files(&self, dir: &Path, patterns: &[&str]) -> Result<Vec<String>> {
        let mut files = Vec::new();

        Self::walk_dir(dir, &mut |path: &Path| {
            let path_str = path.to_string_lossy();
            for pattern in patterns {
                if path_str.contains(pattern) {
                    files.push(path_str.to_string());
                    break;
                }
            }
        })?;

        Ok(files)
    }

    fn walk_dir<F>(dir: &Path, callback: &mut F) -> Result<()>
    where
        F: FnMut(&Path),
    {
        if !dir.is_dir() {
            return Ok(());
        }

        for entry in fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();

            // Skip common exclusions
            if let Some(name) = path.file_name().and_then(|n| n.to_str()) {
                if matches!(
                    name,
                    ".git" | "node_modules" | ".venv" | "target" | "dist" | ".pytest_cache"
                ) {
                    continue;
                }
            }

            if path.is_dir() {
                Self::walk_dir(&path, callback)?;
            } else {
                callback(&path);
            }
        }

        Ok(())
    }

    fn get_git_head_sha(&self, project_dir: &Path) -> Result<String> {
        use std::process::Command;

        let output = Command::new("git")
            .args(&["rev-parse", "HEAD"])
            .current_dir(project_dir)
            .output()?;

        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
        } else {
            Err(PrewarmError::CommandFailed(
                "git rev-parse HEAD".to_string(),
            ))
        }
    }

    fn get_tool_version(&self, tool: &str) -> Result<String> {
        use std::process::Command;

        let output = Command::new(tool).args(&["--version"]).output()?;

        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
        } else {
            Err(PrewarmError::CommandFailed(format!("{} --version", tool)))
        }
    }

    fn find_config_file(&self, dir: &Path, candidates: &[&str]) -> Option<String> {
        for candidate in candidates {
            let config_path = dir.join(candidate);
            if config_path.exists() {
                return Some(config_path.to_string_lossy().to_string());
            }
        }
        None
    }

    fn scan_available_tools(&self) -> Vec<String> {
        let tools = vec![
            "python",
            "node",
            "cargo",
            "git",
            "ruff",
            "shellcheck",
            "jq",
            "rg",
        ];
        let mut available = Vec::new();

        for tool in tools {
            if which::which(tool).is_ok() {
                available.push(tool.to_string());
            }
        }

        available
    }

    fn create_metadata(&self, component: &str, version: &str) -> PrewarmMetadata {
        PrewarmMetadata {
            timestamp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0),
            ttl_seconds: 3600,
            size_bytes: 0,
            component: component.to_string(),
            version: version.to_string(),
        }
    }

    fn write_cache<T: Serialize>(&self, filename: &str, data: &T) -> Result<()> {
        let path = self.cache_dir.join(filename);
        let content = serde_json::to_string_pretty(data)?;
        fs::write(path, content)?;
        Ok(())
    }

    fn read_cache<T: for<'de> serde::Deserialize<'de>>(&self, filename: &str) -> Result<T> {
        let path = self.cache_dir.join(filename);
        let content = fs::read_to_string(path)?;
        Ok(serde_json::from_str(&content)?)
    }

    /// Check if cache is fresh
    pub fn is_fresh(&self, filename: &str, ttl_seconds: u64) -> bool {
        let path = self.cache_dir.join(filename);

        if !path.exists() {
            return false;
        }

        if let Ok(metadata) = fs::metadata(&path) {
            if let Ok(modified) = metadata.modified() {
                if let Ok(elapsed) = modified.elapsed() {
                    return elapsed.as_secs() < ttl_seconds;
                }
            }
        }

        false
    }
}

/// Report of prewarm operations
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrewarmReport {
    /// Successfully prewarmed components
    pub successful: Vec<String>,
    /// Errors encountered
    pub errors: Vec<String>,
}

impl PrewarmReport {
    pub fn new() -> Self {
        Self {
            successful: Vec::new(),
            errors: Vec::new(),
        }
    }

    pub fn is_success(&self) -> bool {
        self.errors.is_empty()
    }
}

impl Default for PrewarmReport {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;

    #[test]
    fn test_prewarm_metadata() {
        let metadata = PrewarmMetadata {
            timestamp: 1000000,
            ttl_seconds: 3600,
            size_bytes: 1024,
            component: "test".to_string(),
            version: "1.0".to_string(),
        };

        assert_eq!(metadata.component, "test");
        assert_eq!(metadata.ttl_seconds, 3600);
    }

    #[test]
    fn test_prewarm_report() {
        let mut report = PrewarmReport::new();
        assert!(report.is_success());

        report.successful.push("test1".to_string());
        assert!(report.is_success());

        report.errors.push("error1".to_string());
        assert!(!report.is_success());
    }

    #[test]
    fn test_shared_data_cache() {
        let cache = SharedDataCache {
            project_root: "/tmp/test".to_string(),
            head_sha: "abc123".to_string(),
            python_files: vec!["src/main.py".to_string()],
            test_files: vec!["tests/test_main.py".to_string()],
            source_files: vec!["src/main.py".to_string()],
            metadata: PrewarmMetadata {
                timestamp: 1000000,
                ttl_seconds: 3600,
                size_bytes: 0,
                component: "shared-data".to_string(),
                version: "1.0".to_string(),
            },
        };

        assert_eq!(cache.python_files.len(), 1);
        assert_eq!(cache.test_files.len(), 1);
    }
}
