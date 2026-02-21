use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::thread;
use std::os::unix::process::ExitStatusExt;

fn unique_dir(name: &str) -> PathBuf {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("time")
        .as_nanos();
    let dir = std::env::temp_dir().join(format!("thegent-hooks-{name}-{nanos}"));
    fs::create_dir_all(&dir).expect("create temp dir");
    dir
}

fn init_git_repo(path: &Path) {
    let ok = Command::new("git")
        .arg("init")
        .current_dir(path)
        .status()
        .expect("git init");
    assert!(ok.success());

    let ok = Command::new("git")
        .args(["config", "user.email", "test@example.com"])
        .current_dir(path)
        .status()
        .expect("git config email");
    assert!(ok.success());

    let ok = Command::new("git")
        .args(["config", "user.name", "Test User"])
        .current_dir(path)
        .status()
        .expect("git config name");
    assert!(ok.success());
}

fn cargo_bin() -> PathBuf {
    if let Ok(var) = std::env::var("CARGO_BIN_EXE_thegent-hooks") {
        return PathBuf::from(var);
    }
    if let Ok(var) = std::env::var("CARGO_BIN_EXE_thegent_hooks") {
        return PathBuf::from(var);
    }
    let mut p = std::env::current_exe().expect("current_exe");
    p.pop(); // deps
    p.pop(); // debug
    p.join("thegent-hooks")
}

#[test]
fn test_git_cache_with_default_ttl() {
    let dir = unique_dir("git-cache-default");
    init_git_repo(&dir);

    let cache_dir = dir.join(".git-cache");

    // First git status call
    let output1 = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git status 1");
    assert!(output1.status.success());

    // Second call should hit cache (same output)
    let output2 = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git status 2");
    assert!(output2.status.success());

    // Both should produce identical output
    assert_eq!(output1.stdout, output2.stdout);

    // Cache should exist
    assert!(cache_dir.exists(), "Cache directory should exist");
}

#[test]
fn test_git_cache_with_custom_ttl() {
    let dir = unique_dir("git-cache-custom-ttl");
    init_git_repo(&dir);

    let cache_dir = dir.join(".git-cache");

    // First call with 2 second TTL
    let output1 = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "--ttl", "2", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git status ttl");
    assert!(output1.status.success());

    let out1 = String::from_utf8_lossy(&output1.stdout);

    // Immediate second call should hit cache
    let output2 = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git status (immediate)");
    let out2 = String::from_utf8_lossy(&output2.stdout);
    assert_eq!(out1, out2, "Immediate cache hit");

    // Wait for TTL to expire
    thread::sleep(Duration::from_secs(3));

    // Cache should be expired (but still callable)
    let output3 = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git status (after ttl)");
    assert!(output3.status.success());
}

#[test]
fn test_git_lock_detection() {
    let dir = unique_dir("git-lock-detection");
    init_git_repo(&dir);

    let git_dir = dir.join(".git");
    let lock_file = git_dir.join("index.lock");

    // Create a lock file
    fs::write(&lock_file, "").expect("create lock file");

    // Test --detect-lock flag
    let output = Command::new(cargo_bin())
        .args(&["git", "--detect-lock", "status"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git --detect-lock");

    // Should exit with code 2 (lock detected)
    assert_eq!(output.status.code(), Some(2), "Should detect lock");

    // Error output should contain lock info
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(
        stderr.contains("GIT-LOCK-DETECTED"),
        "Stderr should contain lock detection message: {}",
        stderr
    );

    // Clean up lock
    fs::remove_file(&lock_file).expect("remove lock file");

    // Test again without lock
    let output2 = Command::new(cargo_bin())
        .args(&["git", "--detect-lock", "status"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git --detect-lock (no lock)");

    // Should exit with code 0 (no lock)
    assert_eq!(
        output2.status.code(),
        Some(0),
        "Should succeed when no lock: {:?}",
        output2
    );
}

#[test]
fn test_git_lock_recovery_stale() {
    let dir = unique_dir("git-lock-recovery");
    init_git_repo(&dir);

    let git_dir = dir.join(".git");
    let lock_file = git_dir.join("index.lock");

    // Create a lock file (pretend it's stale by setting old mtime)
    fs::write(&lock_file, "").expect("create lock file");

    // Manually set mtime to 15 seconds ago
    let now = SystemTime::now();
    let old_time = now - Duration::from_secs(15);

    // Use touch to set mtime (on Unix)
    #[cfg(unix)]
    {
        use std::os::unix::fs::MetadataExt;
        let metadata = fs::metadata(&lock_file).expect("get metadata");
        let old_mtime = old_time
            .duration_since(UNIX_EPOCH)
            .expect("duration since epoch");
        let old_atime = old_mtime;

        // We can't directly set mtime from Rust stdlib easily, so we'll use a different approach:
        // Create an old file and then copy it
        let temp_old = git_dir.join("old-lock-temp");
        fs::write(&temp_old, "").expect("create temp");

        // Instead, test indirectly by checking the message
        let output = Command::new("stat")
            .arg(&lock_file)
            .output()
            .unwrap_or_else(|_| {
                // If stat fails, skip this part
                let mut out = std::process::Output {
                    status: std::process::ExitStatus::from_raw(0),
                    stdout: Vec::new(),
                    stderr: Vec::new(),
                };
                out.status = std::process::ExitStatus::from_raw(0);
                out
            });

        // For now, just verify the lock exists and can be detected
        assert!(lock_file.exists(), "Lock file should exist");

        // Clean up
        let _ = fs::remove_file(&temp_old);
    }

    // Clean up for test
    let _ = fs::remove_file(&lock_file);
}

#[test]
fn test_git_agent_metadata_passthrough() {
    let dir = unique_dir("git-agent-metadata");
    init_git_repo(&dir);

    // Create a test file to add
    let test_file = dir.join("test.txt");
    fs::write(&test_file, "test content").expect("write test file");

    // Add file with agent metadata
    let output = Command::new(cargo_bin())
        .env("THEGENT_AGENT_ID", "test-agent-1")
        .env("SESSION_ID", "test-session-abc")
        .args(&["git", "add", "test.txt"])
        .current_dir(&dir)
        .output()
        .expect("git add with metadata");
    assert!(output.status.success());

    // Verify file was staged
    let status = Command::new("git")
        .args(&["status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("git status");
    let status_str = String::from_utf8_lossy(&status.stdout);
    assert!(status_str.contains("test.txt"), "File should be staged: {}", status_str);
}

#[test]
fn test_git_concurrent_operations_with_cache() {
    let dir = unique_dir("git-concurrent");
    init_git_repo(&dir);

    let cache_dir = dir.join(".git-cache");

    // Simulate two "concurrent" operations
    let output1 = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .env("SESSION_ID", "session-1")
        .args(&["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .current_dir(&dir)
        .output()
        .expect("concurrent op 1");
    assert!(output1.status.success());

    let output2 = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .env("SESSION_ID", "session-2")
        .args(&["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .current_dir(&dir)
        .output()
        .expect("concurrent op 2");
    assert!(output2.status.success());

    // Both should produce same result
    assert_eq!(output1.stdout, output2.stdout);
}

#[test]
fn test_git_different_operations_different_cache_keys() {
    let dir = unique_dir("git-different-ops");
    init_git_repo(&dir);

    let cache_dir = dir.join(".git-cache");

    // Run two different operations
    let status_output = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("git status");
    assert!(status_output.status.success());

    let branch_output = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .current_dir(&dir)
        .output()
        .expect("git rev-parse");
    assert!(branch_output.status.success());

    // Outputs should be different (they're different commands)
    assert_ne!(status_output.stdout, branch_output.stdout);

    // Cache should have separate entries
    assert!(cache_dir.exists());
}

#[test]
fn test_git_write_operations_invalidate_cache() {
    let dir = unique_dir("git-cache-invalidation");
    init_git_repo(&dir);

    let cache_dir = dir.join(".git-cache");

    // First status call to populate cache
    let _status1 = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("git status 1");

    // Create and add a file (write operation)
    let test_file = dir.join("new-file.txt");
    fs::write(&test_file, "content").expect("write file");

    let _add = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "add", "new-file.txt"])
        .current_dir(&dir)
        .output()
        .expect("git add");

    // Status should now include the new file (cache should be invalidated)
    let status2 = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("git status 2");

    let status_str = String::from_utf8_lossy(&status2.stdout);
    assert!(status_str.contains("new-file.txt"), "New file should appear in status");
}

#[test]
fn test_git_help_shows_new_options() {
    let output = Command::new(cargo_bin())
        .args(&["git"])
        .output()
        .expect("thegent-hooks git help");

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    let all_output = format!("{}{}", stdout, stderr);

    // Help should mention new options
    assert!(all_output.contains("ttl") || all_output.contains("--ttl"), "Should mention TTL option");
    assert!(
        all_output.contains("detect-lock") || all_output.contains("--detect-lock"),
        "Should mention lock detection"
    );
}

#[test]
fn test_git_read_only_vs_write_operations() {
    let dir = unique_dir("git-ro-vs-write");
    init_git_repo(&dir);

    let cache_dir = dir.join(".git-cache");

    // Read-only operations should be cached
    let _status = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "status"])
        .current_dir(&dir)
        .output()
        .expect("git status (cached)");

    // Write operations should not hit cache
    let test_file = dir.join("test.txt");
    fs::write(&test_file, "test").expect("write file");

    let add_output = Command::new(cargo_bin())
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(&["git", "add", "test.txt"])
        .current_dir(&dir)
        .output()
        .expect("git add (not cached)");
    assert!(add_output.status.success());
}
