//! Git operations wrapper migrated from hooks/lib/git-wrapper.sh
//! Handles index.lock contention, TTL caching, lock detection, and agent passthrough
//!
//! Features:
//! - TTL-based caching for read-only operations (configurable per-operation)
//! - Lock detection (.git/index.lock) with stale lock recovery
//! - Agent passthrough metadata (agent_id, session_id) for tracing
//! - Support for agent-initiated operations (commit, push with metadata)

use std::fs;
use std::path::{PathBuf};
use std::process::{Command, Output};
#[cfg(unix)]
use std::os::unix::process::ExitStatusExt;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::collections::HashMap;
use crate::git_cache::GitCache;
use crate::utils::resolve_git_binary;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum GitOpsError {
    #[error("Git binary not found")]
    GitNotFound,
    #[error("Git command failed: {0}")]
    CommandFailed(String),
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Lock timeout: index.lock held too long")]
    LockTimeout,
    #[error("Lock detected: {0}")]
    LockDetected(String),
    #[error("Invalid metadata: {0}")]
    InvalidMetadata(String),
}

/// Agent metadata for operation tracing and cost tracking
#[derive(Debug, Clone, Default)]
pub struct AgentMetadata {
    pub agent_id: Option<String>,
    pub session_id: Option<String>,
    pub correlation_id: Option<String>,
}

impl AgentMetadata {
    /// Load from environment variables
    pub fn from_env() -> Self {
        Self {
            agent_id: std::env::var("THEGENT_AGENT_ID").ok(),
            session_id: std::env::var("SESSION_ID").ok(),
            correlation_id: std::env::var("THEGENT_CORRELATION_ID").ok(),
        }
    }

    /// Add metadata to git command as config options
    pub fn as_git_config(&self) -> Vec<String> {
        let mut config = Vec::new();
        if let Some(agent_id) = &self.agent_id {
            config.push(format!("-c"));
            config.push(format!("user.thegent_agent={}", agent_id));
        }
        if let Some(session_id) = &self.session_id {
            config.push(format!("-c"));
            config.push(format!("user.thegent_session={}", session_id));
        }
        if let Some(corr_id) = &self.correlation_id {
            config.push(format!("-c"));
            config.push(format!("user.thegent_correlation={}", corr_id));
        }
        config
    }
}

/// Git operations wrapper with mutex handling, caching, and agent passthrough
/// Equivalent to git() wrapper in git-wrapper.sh with Phase 1.5 enhancements
pub struct GitOps {
    git_bin: PathBuf,
    cache: GitCache,
    metadata: AgentMetadata,
    operation_ttls: HashMap<String, Duration>,
}

impl GitOps {
    /// Create new GitOps instance
    pub fn new() -> Result<Self, GitOpsError> {
        let git_bin = resolve_git_binary()
            .ok_or(GitOpsError::GitNotFound)?;

        let cache = GitCache::from_env()
            .map_err(|e| GitOpsError::Io(std::io::Error::new(
                std::io::ErrorKind::Other,
                format!("Failed to create git cache: {}", e)
            )))?;

        let metadata = AgentMetadata::from_env();

        Ok(Self {
            git_bin,
            cache,
            metadata,
            operation_ttls: Self::default_ttls(),
        })
    }

    /// Default TTLs for common read-only operations
    fn default_ttls() -> HashMap<String, Duration> {
        let mut ttls = HashMap::new();
        // Quick queries (5 seconds)
        ttls.insert("rev-parse".to_string(), Duration::from_secs(5));
        ttls.insert("symbolic-ref".to_string(), Duration::from_secs(5));
        ttls.insert("describe".to_string(), Duration::from_secs(5));

        // Moderate queries (15 seconds)
        ttls.insert("status".to_string(), Duration::from_secs(15));
        ttls.insert("ls-files".to_string(), Duration::from_secs(15));
        ttls.insert("branch".to_string(), Duration::from_secs(15));

        // Longer queries (30 seconds)
        ttls.insert("log".to_string(), Duration::from_secs(30));
        ttls.insert("diff".to_string(), Duration::from_secs(30));
        ttls.insert("show".to_string(), Duration::from_secs(30));

        ttls
    }

    /// Get TTL for a specific git command
    pub fn get_ttl(&self, cmd: &str) -> Duration {
        self.operation_ttls
            .get(cmd)
            .copied()
            .unwrap_or_else(|| Duration::from_secs(60))
    }

    /// Set custom TTL for a git command
    pub fn set_ttl(&mut self, cmd: impl Into<String>, ttl: Duration) {
        self.operation_ttls.insert(cmd.into(), ttl);
    }

    /// Get repository root
    fn get_repo_root(&self) -> Result<PathBuf, GitOpsError> {
        let output = Command::new(&self.git_bin)
            .arg("rev-parse")
            .arg("--show-toplevel")
            .output()?;

        if output.status.success() {
            let root = String::from_utf8_lossy(&output.stdout).trim().to_string();
            Ok(PathBuf::from(root))
        } else {
            Ok(PathBuf::from("."))
        }
    }

    /// Detect and surface lock information
    pub fn detect_lock(&self, lock_file: &PathBuf) -> Result<Option<LockInfo>, GitOpsError> {
        if !lock_file.exists() {
            return Ok(None);
        }

        let metadata = fs::metadata(lock_file)?;
        let modified = metadata.modified()?;
        let now = SystemTime::now();
        let age = now.duration_since(modified)
            .unwrap_or(Duration::from_secs(0));

        Ok(Some(LockInfo {
            path: lock_file.clone(),
            age,
            is_stale: age > Duration::from_secs(10),
        }))
    }

    /// Handle index.lock contention with improved diagnostics
    fn wait_for_lock(&self, lock_file: &PathBuf, wait_timeout: Duration) -> Result<(), GitOpsError> {
        const MAX_RETRIES: u32 = 20;
        const STALE_LOCK_AGE: u64 = 10; // seconds
        let max_wait = wait_timeout.as_secs_f64();

        for retry in 0..MAX_RETRIES {
            if !lock_file.exists() {
                return Ok(());
            }

            // Check if lock is stale (from crashed process)
            if let Ok(metadata) = fs::metadata(lock_file) {
                if let Ok(modified) = metadata.modified() {
                    if let Ok(duration) = modified.duration_since(UNIX_EPOCH) {
                        let now = SystemTime::now()
                            .duration_since(UNIX_EPOCH)
                            .unwrap()
                            .as_secs();
                        let age = now.saturating_sub(duration.as_secs());

                        if age > STALE_LOCK_AGE {
                            eprintln!("GIT-MUTEX: Stealing stale lock ({} seconds old) from crashed process...", age);
                            if let Err(e) = fs::remove_file(lock_file) {
                                eprintln!("GIT-MUTEX: Failed to remove stale lock: {}", e);
                                return Err(GitOpsError::LockDetected(
                                    format!("Could not remove stale lock (age: {} seconds): {}", age, e)
                                ));
                            }
                            return Ok(());
                        }
                    }
                }
            }

            // Wait with exponential backoff
            let sleep_time = 0.1 + (retry as f64 * 0.1);
            let elapsed = (retry as f64) * 0.1;

            if elapsed > max_wait {
                return Err(GitOpsError::LockTimeout);
            }

            eprintln!("GIT-MUTEX: Waiting {:.1}s for git index.lock (held by another agent/tenant)...", sleep_time);
            std::thread::sleep(Duration::from_secs_f64(sleep_time));
        }

        Err(GitOpsError::LockTimeout)
    }

    /// Check if command is read-only (can be cached)
    fn is_read_only(&self, cmd: &str) -> bool {
        matches!(cmd, 
            "diff" | "status" | "ls-files" | "rev-parse" | "log" | "show" | 
            "name-rev" | "symbolic-ref" | "branch" | "tag" | "remote" | 
            "config" | "ls-tree" | "cat-file" | "describe"
        )
    }

    /// Check if command modifies repository (should invalidate cache)
    fn is_write_operation(&self, cmd: &str) -> bool {
        matches!(cmd,
            "add" | "commit" | "checkout" | "reset" | "rm" | "mv" | "pull" |
            "push" | "merge" | "rebase" | "fetch" | "stash" | "am" | "apply"
        )
    }

    /// Execute git command with caching, lock handling, and agent metadata passthrough
    /// Uses operation-specific TTLs and detects/surfaces lock information
    pub fn execute(&self, cmd: &str, args: &[String]) -> Result<Output, GitOpsError> {
        // Handle read-only commands with caching
        if self.is_read_only(cmd) {
            let full_cmd = {
                let mut v = vec![cmd.to_string()];
                v.extend_from_slice(args);
                v
            };

            // Try cache first with operation-specific TTL
            if let Some(cached_output) = self.cache.get(&full_cmd) {
                // Verify TTL hasn't expired for this operation
                let ttl = self.get_ttl(cmd);
                if let Ok(cache_age) = self.cache.get_age(&full_cmd) {
                    if cache_age < ttl {
                        #[cfg(unix)]
                        let status = std::process::ExitStatus::from_raw(0);
                        #[cfg(not(unix))]
                        let status = std::process::Command::new("true").status().unwrap();

                        return Ok(Output {
                            status,
                            stdout: cached_output.into_bytes(),
                            stderr: Vec::new(),
                        });
                    }
                }
            }

            // Execute git command with agent metadata
            let mut cmd_args = self.metadata.as_git_config();
            cmd_args.push(cmd.to_string());
            cmd_args.extend_from_slice(args);

            let output = Command::new(&self.git_bin)
                .args(&cmd_args)
                .output()?;

            // Cache successful results
            if output.status.success() {
                if let Ok(stdout_str) = String::from_utf8(output.stdout.clone()) {
                    if !stdout_str.is_empty() {
                        let _ = self.cache.set(&full_cmd, &stdout_str);
                    }
                }
            }

            return Ok(output);
        }

        // Handle write operations with mutex and lock detection
        let repo_root = self.get_repo_root()?;
        let lock_file = repo_root.join(".git").join("index.lock");

        // Detect lock and surface information
        if let Ok(Some(lock_info)) = self.detect_lock(&lock_file) {
            eprintln!("GIT-LOCK-DETECTED: {} (age: {:.1}s, stale: {})",
                lock_info.path.display(),
                lock_info.age.as_secs_f64(),
                lock_info.is_stale);
        }

        // Wait for lock if needed, with configurable timeout
        let wait_timeout = Duration::from_secs(
            std::env::var("THEGENT_GIT_LOCK_TIMEOUT")
                .ok()
                .and_then(|s| s.parse().ok())
                .unwrap_or(30)
        );
        self.wait_for_lock(&lock_file, wait_timeout)?;

        // Invalidate cache on write operations
        if self.is_write_operation(cmd) {
            let _ = self.cache.invalidate_all();
        }

        // Execute git command with agent metadata
        let mut cmd_args = self.metadata.as_git_config();
        cmd_args.push(cmd.to_string());
        cmd_args.extend_from_slice(args);

        let output = Command::new(&self.git_bin)
            .args(&cmd_args)
            .output()?;

        Ok(output)
    }
}

/// Information about a detected git lock file
#[derive(Debug, Clone)]
pub struct LockInfo {
    pub path: PathBuf,
    pub age: Duration,
    pub is_stale: bool,
}

impl Default for GitOps {
    fn default() -> Self {
        Self::new().expect("Failed to create GitOps")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_read_only() {
        let ops = GitOps::new().unwrap();
        assert!(ops.is_read_only("status"));
        assert!(ops.is_read_only("diff"));
        assert!(!ops.is_read_only("add"));
    }

    #[test]
    fn test_is_write_operation() {
        let ops = GitOps::new().unwrap();
        assert!(ops.is_write_operation("add"));
        assert!(ops.is_write_operation("commit"));
        assert!(!ops.is_write_operation("status"));
    }

    #[test]
    fn test_agent_metadata_from_env() {
        // Save current env
        let orig_agent = std::env::var("THEGENT_AGENT_ID").ok();
        let orig_session = std::env::var("SESSION_ID").ok();

        // Set test values
        std::env::set_var("THEGENT_AGENT_ID", "agent-1");
        std::env::set_var("SESSION_ID", "session-123");

        let metadata = AgentMetadata::from_env();
        assert_eq!(metadata.agent_id, Some("agent-1".to_string()));
        assert_eq!(metadata.session_id, Some("session-123".to_string()));

        // Restore
        if let Some(v) = orig_agent {
            std::env::set_var("THEGENT_AGENT_ID", v);
        } else {
            std::env::remove_var("THEGENT_AGENT_ID");
        }
        if let Some(v) = orig_session {
            std::env::set_var("SESSION_ID", v);
        } else {
            std::env::remove_var("SESSION_ID");
        }
    }

    #[test]
    fn test_agent_metadata_as_git_config() {
        let metadata = AgentMetadata {
            agent_id: Some("agent-1".to_string()),
            session_id: Some("session-123".to_string()),
            correlation_id: Some("corr-456".to_string()),
        };

        let config = metadata.as_git_config();
        assert!(config.contains(&"-c".to_string()));
        assert!(config.iter().any(|c| c.contains("agent=")));
        assert!(config.iter().any(|c| c.contains("session=")));
        assert!(config.iter().any(|c| c.contains("correlation=")));
    }

    #[test]
    fn test_default_ttls() {
        let ops = GitOps::new().unwrap();

        // Verify some default TTLs
        assert_eq!(ops.get_ttl("rev-parse"), Duration::from_secs(5));
        assert_eq!(ops.get_ttl("status"), Duration::from_secs(15));
        assert_eq!(ops.get_ttl("log"), Duration::from_secs(30));

        // Unknown command gets default
        assert_eq!(ops.get_ttl("unknown"), Duration::from_secs(60));
    }

    #[test]
    fn test_set_custom_ttl() {
        let mut ops = GitOps::new().unwrap();
        ops.set_ttl("status", Duration::from_secs(5));
        assert_eq!(ops.get_ttl("status"), Duration::from_secs(5));
    }

    #[test]
    fn test_lock_info_creation() {
        use tempfile::TempDir;

        let temp = TempDir::new().unwrap();
        let lock_file = temp.path().join(".git").join("index.lock");
        fs::create_dir_all(lock_file.parent().unwrap()).unwrap();
        fs::write(&lock_file, "").unwrap();

        let ops = GitOps::new().unwrap();
        let lock_info = ops.detect_lock(&lock_file).unwrap();

        assert!(lock_info.is_some());
        let info = lock_info.unwrap();
        assert!(info.age.as_secs() < 1); // Just created
        assert!(!info.is_stale);
    }
}
