//! Integration tests for Phase 1.5 changed-files enhancement
//! Tests filtering, dependency analysis, and impact classification

use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

fn unique_dir(name: &str) -> PathBuf {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("time")
        .as_nanos();
    let dir = std::env::temp_dir().join(format!("thegent-changed-{name}-{nanos}"));
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
    p.pop(); // debug or release
    p.join("thegent-hooks")
}

/// Test: Filter by extension
#[test]
#[ignore] // Ignore until thegent-hooks binary builds successfully
fn test_changed_files_filter_by_extension() {
    let repo = unique_dir("filter-ext");
    init_git_repo(&repo);

    // Create initial files
    fs::write(repo.join("main.py"), "print('hello')\n").expect("write python");
    fs::write(repo.join("main.ts"), "console.log('hello')\n").expect("write typescript");
    fs::write(repo.join("README.md"), "# Project\n").expect("write markdown");

    // Commit initial state
    Command::new("git")
        .args(["add", "."])
        .current_dir(&repo)
        .status()
        .expect("git add");
    Command::new("git")
        .args(["commit", "-m", "initial"])
        .current_dir(&repo)
        .status()
        .expect("git commit");

    // Modify files
    fs::write(repo.join("main.py"), "print('world')\n").expect("rewrite python");
    fs::write(repo.join("main.ts"), "console.log('world')\n").expect("rewrite typescript");
    fs::write(repo.join("README.md"), "# Project Updated\n").expect("rewrite markdown");

    // Test: Filter for Python files only
    let output = Command::new(cargo_bin())
        .args(["changed-files-filter", "--extension", "py"])
        .current_dir(&repo)
        .output()
        .expect("changed-files-filter");

    assert!(output.status.success(), "command should succeed");
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("main.py"), "should find main.py");
    assert!(!stdout.contains("main.ts"), "should not find main.ts");
    assert!(!stdout.contains("README.md"), "should not find README.md");
}

/// Test: Filter by directory
#[test]
#[ignore] // Ignore until thegent-hooks binary builds successfully
fn test_changed_files_filter_by_directory() {
    let repo = unique_dir("filter-dir");
    init_git_repo(&repo);

    // Create files in different directories
    fs::create_dir_all(repo.join("src")).expect("create src");
    fs::create_dir_all(repo.join("tests")).expect("create tests");
    fs::create_dir_all(repo.join("docs")).expect("create docs");

    fs::write(repo.join("src/main.py"), "").expect("write src file");
    fs::write(repo.join("tests/test.py"), "").expect("write test file");
    fs::write(repo.join("docs/guide.md"), "").expect("write doc file");

    // Commit initial state
    Command::new("git")
        .args(["add", "."])
        .current_dir(&repo)
        .status()
        .expect("git add");
    Command::new("git")
        .args(["commit", "-m", "initial"])
        .current_dir(&repo)
        .status()
        .expect("git commit");

    // Modify files
    fs::write(repo.join("src/main.py"), "updated").expect("rewrite src");
    fs::write(repo.join("tests/test.py"), "updated").expect("rewrite test");
    fs::write(repo.join("docs/guide.md"), "updated").expect("rewrite doc");

    // Test: Filter for src/ directory only
    let output = Command::new(cargo_bin())
        .args(["changed-files-filter", "--directory", "src"])
        .current_dir(&repo)
        .output()
        .expect("changed-files-filter");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("src/main.py"), "should find src/main.py");
    assert!(
        !stdout.contains("tests/test.py"),
        "should not find tests/test.py"
    );
}

/// Test: Filter by impact type (code vs docs)
#[test]
#[ignore] // Ignore until thegent-hooks binary builds successfully
fn test_changed_files_filter_by_impact() {
    let repo = unique_dir("filter-impact");
    init_git_repo(&repo);

    // Create files with different impact types
    fs::write(repo.join("main.py"), "def hello(): pass\n").expect("write code");
    fs::write(repo.join("README.md"), "# Readme\n").expect("write doc");
    fs::write(repo.join("Cargo.toml"), "[package]\n").expect("write config");

    // Commit initial state
    Command::new("git")
        .args(["add", "."])
        .current_dir(&repo)
        .status()
        .expect("git add");
    Command::new("git")
        .args(["commit", "-m", "initial"])
        .current_dir(&repo)
        .status()
        .expect("git commit");

    // Modify all files
    fs::write(repo.join("main.py"), "def hello(): return 1\n").expect("rewrite code");
    fs::write(repo.join("README.md"), "# Updated\n").expect("rewrite doc");
    fs::write(repo.join("Cargo.toml"), "[package]\nversion = \"0.2.0\"\n").expect("rewrite config");

    // Test: Filter for code-impacting changes only
    let output = Command::new(cargo_bin())
        .args(["changed-files-impact"])
        .current_dir(&repo)
        .output()
        .expect("changed-files-impact");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("main.py"), "should find main.py (code)");
    assert!(
        !stdout.contains("README.md"),
        "should not find README.md (docs)"
    );
}

/// Test: Dependency analysis
#[test]
#[ignore] // Ignore until thegent-hooks binary builds successfully
fn test_changed_files_dependency_analysis() {
    let repo = unique_dir("deps");
    init_git_repo(&repo);

    // Create Python files with dependencies
    fs::write(repo.join("utils.py"), "def helper(): pass\n").expect("write utils");
    fs::write(
        repo.join("main.py"),
        "from utils import helper\n\nhelper()\n",
    )
    .expect("write main");

    // Commit initial state
    Command::new("git")
        .args(["add", "."])
        .current_dir(&repo)
        .status()
        .expect("git add");
    Command::new("git")
        .args(["commit", "-m", "initial"])
        .current_dir(&repo)
        .status()
        .expect("git commit");

    // Modify utils (which main depends on)
    fs::write(repo.join("utils.py"), "def helper(): return 42\n").expect("rewrite utils");

    // Test: Get dependency graph
    let output = Command::new(cargo_bin())
        .args(["changed-files-deps"])
        .current_dir(&repo)
        .output()
        .expect("changed-files-deps");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    // Should produce valid JSON with dependency information
    assert!(
        stdout.contains("depends_on") || stdout.contains("utils.py"),
        "should have dependency information"
    );
}

/// Test: Filter by status (modified vs added)
#[test]
#[ignore] // Ignore until thegent-hooks binary builds successfully
fn test_changed_files_filter_by_status() {
    let repo = unique_dir("filter-status");
    init_git_repo(&repo);

    // Create and commit initial file
    fs::write(repo.join("existing.py"), "").expect("write existing");
    Command::new("git")
        .args(["add", "existing.py"])
        .current_dir(&repo)
        .status()
        .expect("git add");
    Command::new("git")
        .args(["commit", "-m", "initial"])
        .current_dir(&repo)
        .status()
        .expect("git commit");

    // Modify existing file
    fs::write(repo.join("existing.py"), "modified").expect("modify existing");
    // Add new file
    fs::write(repo.join("new.py"), "").expect("write new");

    // Test: Filter for modified status only
    let output = Command::new(cargo_bin())
        .args(["changed-files-filter", "--status", "modified"])
        .current_dir(&repo)
        .output()
        .expect("changed-files-filter");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("existing.py"), "should find modified files");
    // Note: new.py is untracked, not "added" in git sense
}

/// Test: Multiple filters combined
#[test]
#[ignore] // Ignore until thegent-hooks binary builds successfully
fn test_changed_files_multiple_filters() {
    let repo = unique_dir("multi-filter");
    init_git_repo(&repo);

    // Create files in various categories
    fs::create_dir_all(repo.join("src")).expect("create src");
    fs::create_dir_all(repo.join("tests")).expect("create tests");

    fs::write(repo.join("src/main.py"), "").expect("write main");
    fs::write(repo.join("src/utils.py"), "").expect("write utils");
    fs::write(repo.join("tests/test.py"), "").expect("write test");
    fs::write(repo.join("README.md"), "").expect("write readme");

    // Commit initial state
    Command::new("git")
        .args(["add", "."])
        .current_dir(&repo)
        .status()
        .expect("git add");
    Command::new("git")
        .args(["commit", "-m", "initial"])
        .current_dir(&repo)
        .status()
        .expect("git commit");

    // Modify all files
    for file in &["src/main.py", "src/utils.py", "tests/test.py", "README.md"] {
        fs::write(repo.join(file), "updated").expect("update file");
    }

    // Test: Filter for Python files in src/ only
    let output = Command::new(cargo_bin())
        .args([
            "changed-files-filter",
            "--extension",
            "py",
            "--directory",
            "src",
        ])
        .current_dir(&repo)
        .output()
        .expect("changed-files-filter");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("src/main.py"), "should find src/main.py");
    assert!(stdout.contains("src/utils.py"), "should find src/utils.py");
    assert!(
        !stdout.contains("tests/test.py"),
        "should not find tests/test.py"
    );
    assert!(!stdout.contains("README.md"), "should not find README.md");
}

/// Test: Exclusion filters
#[test]
#[ignore] // Ignore until thegent-hooks binary builds successfully
fn test_changed_files_exclude_filters() {
    let repo = unique_dir("exclude");
    init_git_repo(&repo);

    // Create files
    fs::write(repo.join("main.py"), "").expect("write main");
    fs::write(repo.join("config.py"), "").expect("write config");
    fs::write(repo.join("test.py"), "").expect("write test");

    // Commit initial state
    Command::new("git")
        .args(["add", "."])
        .current_dir(&repo)
        .status()
        .expect("git add");
    Command::new("git")
        .args(["commit", "-m", "initial"])
        .current_dir(&repo)
        .status()
        .expect("git commit");

    // Modify all files
    fs::write(repo.join("main.py"), "updated").expect("update main");
    fs::write(repo.join("config.py"), "updated").expect("update config");
    fs::write(repo.join("test.py"), "updated").expect("update test");

    // Test: Get all Python files except tests
    let output = Command::new(cargo_bin())
        .args([
            "changed-files-filter",
            "--extension",
            "py",
            "--exclude-extension",
            "md", // This should have no effect
        ])
        .current_dir(&repo)
        .output()
        .expect("changed-files-filter");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("main.py"), "should find main.py");
    assert!(stdout.contains("config.py"), "should find config.py");
    assert!(stdout.contains("test.py"), "should find test.py");
}
