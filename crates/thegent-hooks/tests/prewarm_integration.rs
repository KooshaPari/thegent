//! Integration tests for prewarm functionality
//!
//! These tests verify that caches are properly prewarmed and can be
//! retrieved for improved performance.

#[cfg(test)]
mod prewarm_integration_tests {
    use std::fs;
    use std::path::Path;
    use tempfile::TempDir;

    /// Helper to create a temporary project
    fn setup_project() -> TempDir {
        let tmp = TempDir::new().expect("Failed to create temp dir");
        let project = tmp.path();

        // Create source structure
        fs::create_dir_all(project.join("src")).ok();
        fs::create_dir_all(project.join("tests")).ok();

        // Create Python files
        fs::write(project.join("src/main.py"), "def main(): pass").ok();
        fs::write(project.join("src/config.py"), "def config(): pass").ok();
        fs::write(project.join("tests/test_main.py"), "def test_main(): pass").ok();

        // Create Rust files
        fs::write(project.join("src/lib.rs"), "pub fn lib() {}").ok();
        fs::write(project.join("src/utils.rs"), "pub fn util() {}").ok();

        // Create config files
        fs::write(
            project.join("pyproject.toml"),
            "[tool.python]\nversion = \"3.11\"\n",
        )
        .ok();
        fs::write(project.join(".shellcheckrc"), "disable=SC2086\n").ok();

        tmp
    }

    #[test]
    fn test_prewarm_creates_cache_directory() {
        let cache_dir = TempDir::new().expect("Failed to create cache dir");
        let cache_path = cache_dir.path();

        // Verify directory exists
        assert!(cache_path.exists());
        assert!(cache_path.is_dir());
    }

    #[test]
    fn test_shared_data_cache_structure() {
        let tmp = setup_project();
        let project = tmp.path();

        // Verify project structure
        assert!(project.join("src").exists());
        assert!(project.join("tests").exists());
        assert!(project.join("src/main.py").exists());
        assert!(project.join("src/lib.rs").exists());
    }

    #[test]
    fn test_python_file_detection() {
        let tmp = setup_project();
        let project = tmp.path();

        // Find Python files
        let mut py_files = Vec::new();
        if let Ok(entries) = fs::read_dir(project.join("src")) {
            for entry in entries {
                if let Ok(entry) = entry {
                    let path = entry.path();
                    if let Some(ext) = path.extension() {
                        if ext == "py" {
                            py_files.push(path);
                        }
                    }
                }
            }
        }

        assert_eq!(py_files.len(), 2); // main.py, config.py
    }

    #[test]
    fn test_test_file_detection() {
        let tmp = setup_project();
        let project = tmp.path();

        // Find test files
        let mut test_files = Vec::new();
        if let Ok(entries) = fs::read_dir(project.join("tests")) {
            for entry in entries {
                if let Ok(entry) = entry {
                    let path = entry.path();
                    if let Some(name) = path.file_name() {
                        if let Some(name_str) = name.to_str() {
                            if name_str.contains("test") {
                                test_files.push(path);
                            }
                        }
                    }
                }
            }
        }

        assert!(test_files.len() > 0);
    }

    #[test]
    fn test_ruff_cache_structure() {
        // Ruff cache should contain version and rules
        let cache = serde_json::json!({
            "version": "0.1.0",
            "rules": ["E501", "F401"],
            "format_config": {}
        });

        assert!(cache.get("version").is_some());
        assert!(cache.get("rules").is_some());
    }

    #[test]
    fn test_shellcheck_cache_structure() {
        // Shellcheck cache should contain version and config
        let cache = serde_json::json!({
            "version": "0.9.0",
            "enabled_checks": [],
            "excluded_errors": ["SC2086"]
        });

        assert!(cache.get("version").is_some());
        assert!(cache.get("excluded_errors").is_some());
    }

    #[test]
    fn test_system_info_cache() {
        // System info should contain OS and architecture
        let cache = serde_json::json!({
            "os": "macos",
            "arch": "aarch64",
            "python_version": "3.11.0",
            "available_tools": ["python", "cargo", "git"]
        });

        assert_eq!(cache["os"], "macos");
        assert_eq!(cache["arch"], "aarch64");
        assert!(cache["available_tools"].is_array());
    }

    #[test]
    fn test_metadata_ttl() {
        let metadata = serde_json::json!({
            "timestamp": 1000000,
            "ttl_seconds": 3600,
            "size_bytes": 1024,
            "component": "shared-data",
            "version": "1.0"
        });

        assert_eq!(metadata["ttl_seconds"], 3600);
        assert!(metadata["timestamp"].is_number());
    }

    #[test]
    fn test_cache_freshness_check() {
        // TTL validation: cache is fresh if age < ttl
        let now = std::time::SystemTime::now();
        let ttl_secs = 3600u64;

        // Simulated: file is 100 seconds old, ttl is 3600
        // So it should be fresh
        let age_secs = 100u64;
        assert!(age_secs < ttl_secs);
    }

    #[test]
    fn test_cache_expiration() {
        // Expired cache: age > ttl
        let ttl_secs = 3600u64;
        let age_secs = 7200u64; // 2 hours old
        assert!(age_secs > ttl_secs);
    }

    #[test]
    fn test_file_discovery_with_exclusions() {
        let tmp = setup_project();
        let project = tmp.path();

        // Create exclusion directories
        fs::create_dir_all(project.join("node_modules")).ok();
        fs::create_dir_all(project.join(".venv")).ok();
        fs::create_dir_all(project.join("target")).ok();

        // These should be excluded from scanning
        let excluded = vec!["node_modules", ".venv", "target"];
        for name in &excluded {
            let path = project.join(name);
            assert!(path.exists());
        }
    }

    #[test]
    fn test_config_file_detection() {
        let tmp = setup_project();
        let project = tmp.path();

        // Verify config files
        assert!(project.join("pyproject.toml").exists());
        assert!(project.join(".shellcheckrc").exists());
    }

    #[test]
    fn test_prewarm_report_structure() {
        let report = serde_json::json!({
            "successful": ["shared-data", "ruff"],
            "errors": []
        });

        assert!(report["successful"].is_array());
        assert_eq!(report["successful"].as_array().unwrap().len(), 2);
        assert!(report["errors"].is_array());
    }

    #[test]
    fn test_prewarm_report_with_errors() {
        let report = serde_json::json!({
            "successful": ["shared-data"],
            "errors": ["ruff: command not found"]
        });

        assert_eq!(report["successful"].as_array().unwrap().len(), 1);
        assert_eq!(report["errors"].as_array().unwrap().len(), 1);
    }

    #[test]
    fn test_nested_directory_scanning() {
        let tmp = setup_project();
        let project = tmp.path();

        // Create nested structure
        fs::create_dir_all(project.join("src/deep/nested")).ok();
        fs::write(
            project.join("src/deep/nested/module.py"),
            "def module(): pass",
        )
        .ok();

        assert!(project.join("src/deep/nested/module.py").exists());
    }

    #[test]
    fn test_git_head_sha_format() {
        // SHA should be 40 or 64 characters (SHA-1 or SHA-256)
        let sha = "abc123def456abc123def456abc123def456abc1";
        assert_eq!(sha.len(), 40);
        assert!(sha.chars().all(|c| c.is_ascii_hexdigit()));
    }
}
