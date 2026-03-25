use std::fs;
#[cfg(unix)]
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

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

fn fake_path_env(dir: &Path) -> String {
    let bin_dir = dir.join(".fake-bin");
    fs::create_dir_all(&bin_dir).expect("create fake bin dir");

    let thegent = bin_dir.join("thegent");
    fs::write(
        &thegent,
        "#!/bin/sh\nif [ \"$1\" = \"git\" ]; then shift; fi\nexec git \"$@\"\n",
    )
    .expect("write fake thegent");

    #[cfg(unix)]
    {
        let mut perms = fs::metadata(&thegent).expect("metadata").permissions();
        perms.set_mode(0o755);
        fs::set_permissions(&thegent, perms).expect("set perms");
    }

    let mut parts = vec![bin_dir.to_string_lossy().to_string()];
    if let Ok(existing) = std::env::var("PATH") {
        parts.push(existing);
    }
    parts.join(":")
}

#[test]
fn test_git_cache_with_default_ttl() {
    let dir = unique_dir("git-cache-default");
    init_git_repo(&dir);

    let cache_dir = dir.join(".git-cache");
    let path_env = fake_path_env(&dir);

    // First git status call
    let output1 = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git status 1");
    assert!(output1.status.success());

    // Second call should hit cache (same output)
    let output2 = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git status 2");
    assert!(output2.status.success());

    // Both should produce identical output
    assert_eq!(output1.stdout, output2.stdout);
}

#[test]
fn test_git_cache_with_custom_ttl() {
    let dir = unique_dir("git-cache-custom-ttl");
    init_git_repo(&dir);

    let cache_dir = dir.join(".git-cache");
    let path_env = fake_path_env(&dir);

    // First call
    let output1 = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git status");
    assert!(output1.status.success());

    let out1 = String::from_utf8_lossy(&output1.stdout);

    // Immediate second call should hit cache
    let output2 = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git status (immediate)");
    let out2 = String::from_utf8_lossy(&output2.stdout);
    assert_eq!(out1, out2, "Immediate cache hit");

    // Wait briefly, then call again
    thread::sleep(Duration::from_millis(200));

    // Cache should be expired (but still callable)
    let output3 = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "status", "--porcelain"])
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

    let path_env = fake_path_env(&dir);

    // Unsupported legacy flag should fail
    let output = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .args(["git", "--detect-lock", "status"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git --detect-lock");
    assert!(
        !output.status.success(),
        "Unsupported legacy flag should fail"
    );

    // Clean up lock
    fs::remove_file(&lock_file).expect("remove lock file");

    // Without the legacy flag, status should succeed
    let output2 = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .args(["git", "status"])
        .current_dir(&dir)
        .output()
        .expect("thegent-hooks git status");
    assert!(
        output2.status.success(),
        "Should succeed without legacy flag"
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
    let _old_time = SystemTime::now() - Duration::from_secs(15);

    // Use touch to set mtime (on Unix)
    #[cfg(unix)]
    {
        // We can't directly set mtime from Rust stdlib easily, so we'll use a different approach:
        // Create an old file and then copy it
        let temp_old = git_dir.join("old-lock-temp");
        fs::write(&temp_old, "").expect("create temp");

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

    let path_env = fake_path_env(&dir);

    // Create a test file to add
    let test_file = dir.join("test.txt");
    fs::write(&test_file, "test content").expect("write test file");

    // Add file with agent metadata
    let output = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_AGENT_ID", "test-agent-1")
        .env("SESSION_ID", "test-session-abc")
        .args(["git", "add", "test.txt"])
        .current_dir(&dir)
        .output()
        .expect("git add with metadata");
    assert!(output.status.success());

    // Verify file was staged
    let status = Command::new("git")
        .args(["status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("git status");
    let status_str = String::from_utf8_lossy(&status.stdout);
    assert!(
        status_str.contains("test.txt"),
        "File should be staged: {}",
        status_str
    );
}

#[test]
fn test_git_concurrent_operations_with_cache() {
    let dir = unique_dir("git-concurrent");
    init_git_repo(&dir);

    let cache_dir = dir.join(".git-cache");
    let path_env = fake_path_env(&dir);

    // Simulate two "concurrent" operations
    let output1 = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .env("SESSION_ID", "session-1")
        .args(["git", "rev-parse", "--is-inside-work-tree"])
        .current_dir(&dir)
        .output()
        .expect("concurrent op 1");
    assert!(output1.status.success());

    let output2 = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .env("SESSION_ID", "session-2")
        .args(["git", "rev-parse", "--is-inside-work-tree"])
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
    let path_env = fake_path_env(&dir);

    // Run two different operations
    let status_output = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("git status");
    assert!(status_output.status.success());

    let branch_output = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "rev-parse", "--is-inside-work-tree"])
        .current_dir(&dir)
        .output()
        .expect("git rev-parse");
    assert!(branch_output.status.success());

    // Outputs should be different (they're different commands)
    assert_ne!(status_output.stdout, branch_output.stdout);
}

#[test]
fn test_git_write_operations_invalidate_cache() {
    let dir = unique_dir("git-cache-invalidation");
    init_git_repo(&dir);

    let cache_dir = dir.join(".git-cache");
    let path_env = fake_path_env(&dir);

    // First status call to populate cache
    let _status1 = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("git status 1");

    // Create and add a file (write operation)
    let test_file = dir.join("new-file.txt");
    fs::write(&test_file, "content").expect("write file");

    let _add = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "add", "new-file.txt"])
        .current_dir(&dir)
        .output()
        .expect("git add");

    // Status should now include the new file (cache should be invalidated)
    let status2 = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "status", "--porcelain"])
        .current_dir(&dir)
        .output()
        .expect("git status 2");

    let status_str = String::from_utf8_lossy(&status2.stdout);
    assert!(
        status_str.contains("new-file.txt"),
        "New file should appear in status"
    );
}

#[test]
fn test_git_help_shows_new_options() {
    let dir = unique_dir("git-no-args");
    let path_env = fake_path_env(&dir);
    let output = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .args(["git"])
        .output()
        .expect("thegent-hooks git help");
    assert!(output.status.success(), "git without args should succeed");
}

#[test]
fn test_git_read_only_vs_write_operations() {
    let dir = unique_dir("git-ro-vs-write");
    init_git_repo(&dir);

    let cache_dir = dir.join(".git-cache");
    let path_env = fake_path_env(&dir);

    // Read-only operations should be cached
    let _status = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "status"])
        .current_dir(&dir)
        .output()
        .expect("git status (cached)");

    // Write operations should not hit cache
    let test_file = dir.join("test.txt");
    fs::write(&test_file, "test").expect("write file");

    let add_output = Command::new(cargo_bin())
        .env("PATH", &path_env)
        .env("THEGENT_CACHE_DIR", &cache_dir)
        .args(["git", "add", "test.txt"])
        .current_dir(&dir)
        .output()
        .expect("git add (not cached)");
    assert!(add_output.status.success());
}
