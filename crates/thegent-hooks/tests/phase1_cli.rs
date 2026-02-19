use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

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
fn init_emits_expected_env_paths() {
    let dir = unique_dir("init");
    let input = format!(
        "{{\"cwd\":\"{}\",\"project_dir\":\"{}\",\"tool_name\":\"Write\"}}",
        dir.display(),
        dir.display()
    );

    let output = Command::new(cargo_bin())
        .arg("init")
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .spawn()
        .and_then(|mut child| {
            use std::io::Write;
            child
                .stdin
                .as_mut()
                .expect("stdin")
                .write_all(input.as_bytes())?;
            child.wait_with_output()
        })
        .expect("run init");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("PROJECT_DIR='"));
    assert!(stdout.contains("VERIFY_DIR='"));
    assert!(stdout.contains("TOOL_NAME='Write'"));
}

#[test]
fn cache_write_and_read_roundtrip() {
    let cache = unique_dir("cache");

    let status = Command::new(cargo_bin())
        .env("HOOK_CACHE_DIR", &cache)
        .args([
            "cache-write",
            "abc123",
            "--rc",
            "0",
            "--output",
            "hello-world",
        ])
        .status()
        .expect("cache-write");
    assert!(status.success());

    let status = Command::new(cargo_bin())
        .env("HOOK_CACHE_DIR", &cache)
        .args(["cache-check", "abc123", "--ttl", "120"])
        .status()
        .expect("cache-check");
    assert!(status.success());

    let output = Command::new(cargo_bin())
        .env("HOOK_CACHE_DIR", &cache)
        .args(["cache-read", "abc123"])
        .output()
        .expect("cache-read");
    assert!(output.status.success());
    assert!(String::from_utf8_lossy(&output.stdout).contains("hello-world"));
}

#[test]
fn changed_files_lists_tracked_and_untracked_and_caches() {
    let repo = unique_dir("repo");
    init_git_repo(&repo);

    fs::write(repo.join("tracked.txt"), "one\n").expect("write tracked");
    assert!(Command::new("git")
        .args(["add", "tracked.txt"])
        .current_dir(&repo)
        .status()
        .expect("git add")
        .success());
    assert!(Command::new("git")
        .args(["commit", "-m", "init"])
        .current_dir(&repo)
        .status()
        .expect("git commit")
        .success());

    fs::write(repo.join("tracked.txt"), "two\n").expect("rewrite tracked");
    fs::write(repo.join("new.txt"), "new\n").expect("write untracked");

    let cache = unique_dir("shared-cache");
    let output = Command::new(cargo_bin())
        .env("PROJECT_DIR", &repo)
        .env("HOOK_CACHE_DIR", &cache)
        .arg("changed-files")
        .current_dir(&repo)
        .output()
        .expect("changed-files");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("tracked.txt"));
    assert!(stdout.contains("new.txt"));
    assert!(cache.join("shared/changed_files").exists());
}

#[test]
fn config_get_and_skip_from_qa_local() {
    let dir = unique_dir("config");
    let hooks = dir.join(".claude/hooks");
    fs::create_dir_all(&hooks).expect("hooks dir");
    fs::write(
        hooks.join("hook-config.yaml"),
        "prewarm_on_session_start: true\nlimits:\n  debounce_ms: 250\n",
    )
    .expect("hook-config write");
    fs::write(
        dir.join(".claude/qa-local.json"),
        "{\"hooks\":{\"skip\":[\"quality-gate\"]}}",
    )
    .expect("qa-local write");

    let output = Command::new(cargo_bin())
        .env("PROJECT_DIR", &dir)
        .args(["config-get", "limits.debounce_ms"])
        .output()
        .expect("config-get");
    assert!(output.status.success());
    assert!(String::from_utf8_lossy(&output.stdout).contains("250"));

    let status = Command::new(cargo_bin())
        .env("PROJECT_DIR", &dir)
        .args(["skip", "quality-gate"])
        .status()
        .expect("skip");
    assert!(status.success());
}
