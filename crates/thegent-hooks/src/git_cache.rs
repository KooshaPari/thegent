//! Git operation caching migrated from hooks/lib/git-cache.sh
//! Provides TTL-based caching for git operations (70% reduction in git calls)

use std::fs;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use dashmap::DashMap;
use serde::{Deserialize, Serialize};
use thiserror::Error;
use blake3;
use base16ct::lower;

#[derive(Error, Debug)]
pub enum GitCacheError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Cache directory error: {0}")]
    CacheDir(String),
}

/// Git cache with TTL support
/// Equivalent to git_cached() in git-cache.sh
pub struct GitCache {
    cache_dir: PathBuf,
    ttl: Duration,
    memory_cache: DashMap<String, CachedResult>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct CachedResult {
    output: String,
    cached_at: u64,
}

impl GitCache {
    /// Create a new GitCache
    pub fn new(cache_dir: impl AsRef<Path>, ttl_seconds: u64) -> Result<Self, GitCacheError> {
        let cache_dir = cache_dir.as_ref().to_path_buf();
        fs::create_dir_all(&cache_dir)
            .map_err(|e| GitCacheError::CacheDir(format!("Failed to create cache dir: {}", e)))?;

        Ok(Self {
            cache_dir,
            ttl: Duration::from_secs(ttl_seconds),
            memory_cache: DashMap::new(),
        })
    }

    /// Get cache directory from environment or default
    pub fn from_env() -> Result<Self, GitCacheError> {
        let cache_dir = std::env::var("CLAUDE_HOME")
            .or_else(|_| std::env::var("HOME"))
            .unwrap_or_else(|_| ".".to_string());

        let cache_path = PathBuf::from(cache_dir).join(".git-cache");
        let ttl = std::env::var("GIT_CACHE_TTL")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(60);

        Self::new(cache_path, ttl)
    }

    /// Generate cache key from git command and context
    fn cache_key(&self, cmd: &[String]) -> String {
        let mut hasher = blake3::Hasher::new();

        // Include command
        for arg in cmd {
            hasher.update(arg.as_bytes());
            hasher.update(b"|");
        }

        // Include session ID if available
        if let Ok(session_id) = std::env::var("SESSION_ID") {
            hasher.update(session_id.as_bytes());
            hasher.update(b"|");
        }

        // Include .git/config mtime if available
        if let Ok(repo_root) = self.get_repo_root() {
            let config_path = repo_root.join(".git").join("config");
            if let Ok(metadata) = fs::metadata(&config_path) {
                if let Ok(modified) = metadata.modified() {
                    if let Ok(duration) = modified.duration_since(UNIX_EPOCH) {
                        hasher.update(duration.as_secs().to_string().as_bytes());
                    }
                }
            }
        }

        let hash = hasher.finalize();
        let hash_bytes = hash.as_bytes();
        // Use first 16 bytes for shorter key (32 hex chars)
        let key_len = 16.min(hash_bytes.len());
        let mut buf = vec![0u8; key_len * 2];
        let encoded = lower::encode(&hash_bytes[..key_len], &mut buf).unwrap();
        String::from_utf8_lossy(encoded).to_string()
    }

    /// Get repository root
    fn get_repo_root(&self) -> Result<PathBuf, GitCacheError> {
        use std::process::Command;

        let git_bin = crate::utils::resolve_git_binary()
            .ok_or_else(|| GitCacheError::CacheDir("git not found".to_string()))?;

        let output = Command::new(git_bin)
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

    /// Check if cache entry is valid
    fn is_valid(&self, cached_at: u64) -> bool {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        let age = now.saturating_sub(cached_at);
        age < self.ttl.as_secs()
    }

    /// Get the age of a cache entry
    pub fn get_age(&self, cmd: &[String]) -> Result<Duration, GitCacheError> {
        let key = self.cache_key(cmd);
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        // Check memory cache first
        if let Some(cached) = self.memory_cache.get(&key) {
            let age = now.saturating_sub(cached.cached_at);
            return Ok(Duration::from_secs(age));
        }

        // Check disk cache
        let cache_file = self.cache_dir.join(&key);
        if let Ok(metadata) = fs::metadata(&cache_file) {
            if let Ok(modified) = metadata.modified() {
                if let Ok(duration) = modified.duration_since(UNIX_EPOCH) {
                    let cached_at = duration.as_secs();
                    let age = now.saturating_sub(cached_at);
                    return Ok(Duration::from_secs(age));
                }
            }
        }

        Err(GitCacheError::CacheDir("Cache entry not found".to_string()))
    }

    /// Read from cache (memory or disk)
    pub fn get(&self, cmd: &[String]) -> Option<String> {
        let key = self.cache_key(cmd);

        // Check memory cache first
        if let Some(cached) = self.memory_cache.get(&key) {
            if self.is_valid(cached.cached_at) {
                return Some(cached.output.clone());
            } else {
                self.memory_cache.remove(&key);
            }
        }

        // Check disk cache
        let cache_file = self.cache_dir.join(&key);
        if let Ok(metadata) = fs::metadata(&cache_file) {
            if let Ok(modified) = metadata.modified() {
                if let Ok(duration) = modified.duration_since(UNIX_EPOCH) {
                    let cached_at = duration.as_secs();
                    if self.is_valid(cached_at) {
                        if let Ok(content) = fs::read_to_string(&cache_file) {
                            // Update memory cache
                            self.memory_cache.insert(key.clone(), CachedResult {
                                output: content.clone(),
                                cached_at,
                            });
                            return Some(content);
                        }
                    }
                }
            }
        }

        None
    }

    /// Write to cache (memory and disk)
    pub fn set(&self, cmd: &[String], output: &str) -> Result<(), GitCacheError> {
        let key = self.cache_key(cmd);
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        // Update memory cache
        self.memory_cache.insert(key.clone(), CachedResult {
            output: output.to_string(),
            cached_at: now,
        });

        // Write to disk atomically
        let cache_file = self.cache_dir.join(&key);
        let temp_file = self.cache_dir.join(format!("{}.tmp", key));
        fs::write(&temp_file, output)?;
        fs::rename(&temp_file, &cache_file)?;

        Ok(())
    }

    /// Invalidate all cache entries
    pub fn invalidate_all(&self) -> Result<(), GitCacheError> {
        self.memory_cache.clear();

        if self.cache_dir.exists() {
            for entry in fs::read_dir(&self.cache_dir)? {
                let entry = entry?;
                let path = entry.path();
                if path.is_file() && path.extension().is_none() {
                    fs::remove_file(path)?;
                }
            }
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_git_cache() {
        let temp_dir = TempDir::new().unwrap();
        let cache = GitCache::new(temp_dir.path(), 60).unwrap();

        let cmd = vec!["status".to_string(), "--porcelain".to_string()];

        // Should be empty initially
        assert!(cache.get(&cmd).is_none());

        // Set cache
        cache.set(&cmd, "test output").unwrap();

        // Should retrieve from cache
        assert_eq!(cache.get(&cmd), Some("test output".to_string()));
    }
}
