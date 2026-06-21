// SPDX-License-Identifier: MIT OR Apache-2.0
//! Git index.lock contention handling
//!
//! Handles multi-tenant git lock conflicts with:
//! - Lock age detection (steal stale locks > 10s)
//! - Adaptive backoff (0.1s start, +0.1s per retry)
//! - Max 20 retries before fail

use std::path::Path;
use std::thread;
use std::time::{Duration, SystemTime};

const MAX_RETRIES: u32 = 20;
const LOCK_STALE_THRESHOLD: u64 = 10; // seconds

/// Check if a lock file exists
pub fn lock_exists(repo_root: &Path) -> bool {
    repo_root.join(".git/index.lock").exists()
}

/// Get lock file age in seconds
pub fn lock_age(repo_root: &Path) -> Result<u64, std::io::Error> {
    let lock_path = repo_root.join(".git/index.lock");
    let metadata = std::fs::metadata(&lock_path)?;
    let modified = metadata.modified()?;
    let elapsed = SystemTime::now()
        .duration_since(modified)
        .unwrap_or_default();
    Ok(elapsed.as_secs())
}

/// Wait for git lock with adaptive backoff
/// Returns true if lock was acquired, false if max retries exceeded
pub fn acquire_lock(repo_root: &Path) -> bool {
    let mut retry_count = 0;

    while lock_exists(repo_root) {
        if let Ok(age) = lock_age(repo_root) {
            if age > LOCK_STALE_THRESHOLD {
                eprintln!(
                    "GIT-MUTEX: Stealing stale lock ({} seconds old) from crashed process...",
                    age
                );
                if let Err(e) = std::fs::remove_file(repo_root.join(".git/index.lock")) {
                    eprintln!("GIT-MUTEX: Failed to remove stale lock: {}", e);
                }
                break;
            }
        }

        if retry_count >= MAX_RETRIES {
            eprintln!("GIT-MUTEX: Max retries reached waiting for git lock. Failing.");
            return false;
        }

        let sleep_time = Duration::from_millis(100 + (retry_count as u64 * 100));
        eprintln!(
            "GIT-MUTEX: Waiting {:?} for git index.lock (held by another agent/tenant)...",
            sleep_time
        );
        thread::sleep(sleep_time);
        retry_count += 1;
    }

    true
}

/// Invalidate git cache (called before write operations)
pub fn invalidate_cache() {
    // This would be called before write operations
    // Cache invalidation is handled by the cache module
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_lock_exists() {
        let temp = TempDir::new().unwrap();
        let git_dir = temp.path().join(".git");
        std::fs::create_dir(&git_dir).unwrap();

        assert!(!lock_exists(temp.path()));

        let lock_file = git_dir.join("index.lock");
        std::fs::write(&lock_file, "").unwrap();

        assert!(lock_exists(temp.path()));
    }

    #[test]
    fn test_acquire_lock_no_contention() {
        let temp = TempDir::new().unwrap();
        let git_dir = temp.path().join(".git");
        std::fs::create_dir(&git_dir).unwrap();

        // Should succeed immediately if no lock
        assert!(acquire_lock(temp.path()));
    }
}
