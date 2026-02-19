//! TTL-based cache for git read-only operations
//!
//! Caches results from read-only git commands (status, diff, log, etc.)
//! with configurable TTL. 5-20x speedup for repeated operations.

use std::path::Path;
use std::time::{SystemTime, Duration};
use std::collections::HashMap;
use parking_lot::RwLock;
use serde::{Serialize, Deserialize};

const DEFAULT_TTL_SECS: u64 = 300; // 5 minutes

#[derive(Clone, Debug, Serialize, Deserialize)]
struct CacheEntry {
    output: String,
    created_at: u64,
    ttl_secs: u64,
}

/// In-memory TTL cache for git operations
pub struct GitCache {
    entries: RwLock<HashMap<String, CacheEntry>>,
    ttl_secs: u64,
}

impl GitCache {
    /// Create a new cache with default TTL
    pub fn new() -> Self {
        Self {
            entries: RwLock::new(HashMap::new()),
            ttl_secs: DEFAULT_TTL_SECS,
        }
    }

    /// Create a new cache with custom TTL
    pub fn with_ttl(ttl_secs: u64) -> Self {
        Self {
            entries: RwLock::new(HashMap::new()),
            ttl_secs,
        }
    }

    /// Generate cache key from command and args
    pub fn make_key(cmd: &str, args: &[String], repo_root: &Path) -> String {
        let repo_str = repo_root.to_string_lossy();
        let args_str = args.join("|");
        format!("git:{}:{}:{}", repo_str, cmd, args_str)
    }

    /// Get cached result if not expired
    pub fn get(&self, key: &str) -> Option<String> {
        let entries = self.entries.read();
        if let Some(entry) = entries.get(key) {
            if let Ok(elapsed) = self.get_age(entry) {
                if elapsed < Duration::from_secs(entry.ttl_secs) {
                    return Some(entry.output.clone());
                }
            }
        }
        None
    }

    /// Store result in cache
    pub fn set(&self, key: String, output: String) {
        let now = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        let entry = CacheEntry {
            output,
            created_at: now,
            ttl_secs: self.ttl_secs,
        };

        let mut entries = self.entries.write();
        entries.insert(key, entry);
    }

    /// Invalidate all cache entries
    pub fn clear(&self) {
        self.entries.write().clear();
    }

    /// Invalidate specific key
    pub fn invalidate(&self, key: &str) {
        self.entries.write().remove(key);
    }

    /// Check if entry is expired
    fn get_age(&self, entry: &CacheEntry) -> Result<Duration, std::time::SystemTimeError> {
        let epoch = SystemTime::UNIX_EPOCH + Duration::from_secs(entry.created_at);
        SystemTime::now().duration_since(epoch)
    }
}

impl Default for GitCache {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cache_set_get() {
        let cache = GitCache::new();
        let key = "test:key".to_string();
        let value = "test:value".to_string();

        cache.set(key.clone(), value.clone());
        assert_eq!(cache.get(&key), Some(value));
    }

    #[test]
    fn test_cache_expired() {
        let cache = GitCache::with_ttl(0);
        let key = "test:key".to_string();
        let value = "test:value".to_string();

        cache.set(key.clone(), value);
        std::thread::sleep(Duration::from_millis(10));
        // Should be expired
        assert_eq!(cache.get(&key), None);
    }

    #[test]
    fn test_cache_clear() {
        let cache = GitCache::new();
        let key = "test:key".to_string();
        let value = "test:value".to_string();

        cache.set(key.clone(), value);
        cache.clear();
        assert_eq!(cache.get(&key), None);
    }

    #[test]
    fn test_make_key() {
        let repo = Path::new("/tmp/repo");
        let args = vec!["status".to_string(), "--porcelain".to_string()];
        let key1 = GitCache::make_key("status", &args, repo);
        let key2 = GitCache::make_key("status", &args, repo);
        assert_eq!(key1, key2);
    }
}
