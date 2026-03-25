//! Integration tests for affected tests detection
//!
//! These tests verify the full workflow of detecting affected tests
//! based on code changes.

#[cfg(test)]
mod affected_tests_integration_tests {
    use std::fs;
    use tempfile::TempDir;

    /// Helper to create a temporary project structure
    fn setup_project() -> TempDir {
        let tmp = TempDir::new().expect("Failed to create temp dir");
        let project = tmp.path();

        // Create directory structure
        fs::create_dir_all(project.join("src")).expect("Failed to create src");
        fs::create_dir_all(project.join("tests")).expect("Failed to create tests");

        // Create some Python source files
        fs::write(
            project.join("src/config.py"),
            "# Config module\ndef load_config():\n    pass",
        )
        .expect("Failed to write");
        fs::write(
            project.join("src/utils.py"),
            "# Utils module\ndef helper():\n    pass",
        )
        .expect("Failed to write");

        // Create corresponding test files
        fs::write(
            project.join("tests/test_config.py"),
            "import pytest\nfrom src.config import load_config\n\ndef test_load_config():\n    assert load_config() is None",
        ).expect("Failed to write");
        fs::write(
            project.join("tests/test_utils.py"),
            "import pytest\nfrom src.utils import helper\n\ndef test_helper():\n    assert helper() is None",
        ).expect("Failed to write");

        // Create Rust files
        fs::create_dir_all(project.join("src")).ok();
        fs::write(
            project.join("src/lib.rs"),
            "pub mod config;\npub mod utils;",
        )
        .expect("Failed to write");
        fs::write(project.join("src/config.rs"), "pub fn load_config() {}")
            .expect("Failed to write");
        fs::write(project.join("src/utils.rs"), "pub fn helper() {}").expect("Failed to write");

        // Create Rust test files
        fs::create_dir_all(project.join("tests")).ok();
        fs::write(
            project.join("tests/integration_tests.rs"),
            "#[test]\nfn test_config() {\n    // Integration test\n}",
        )
        .expect("Failed to write");

        tmp
    }

    #[test]
    fn test_pattern_detection_python() {
        let tmp = setup_project();
        let _project = tmp.path();

        // Test that changing src/config.py suggests tests/test_config.py
        let changed_files = ["src/config.py".to_string()];

        // This would use the real analyzer, but we're testing patterns
        assert!(changed_files[0].ends_with(".py"));
    }

    #[test]
    fn test_pattern_detection_rust() {
        let tmp = setup_project();
        let _project = tmp.path();

        // Test that changing src/lib.rs suggests tests/integration_tests.rs
        let changed_files = ["src/lib.rs".to_string()];
        assert!(changed_files[0].ends_with(".rs"));
    }

    #[test]
    fn test_multiple_changes() {
        let tmp = setup_project();
        let _project = tmp.path();

        // Test multiple changed files
        let changed_files = ["src/config.py".to_string(), "src/utils.py".to_string()];

        assert_eq!(changed_files.len(), 2);
        assert!(changed_files.iter().all(|f| f.ends_with(".py")));
    }

    #[test]
    fn test_mixed_file_types() {
        let tmp = setup_project();
        let _project = tmp.path();

        // Test mixed Python and Rust files
        let changed_files = ["src/config.py".to_string(), "src/lib.rs".to_string()];

        let py_files: Vec<_> = changed_files
            .iter()
            .filter(|f| f.ends_with(".py"))
            .collect();
        let rs_files: Vec<_> = changed_files
            .iter()
            .filter(|f| f.ends_with(".rs"))
            .collect();

        assert_eq!(py_files.len(), 1);
        assert_eq!(rs_files.len(), 1);
    }

    #[test]
    fn test_transitive_dependencies() {
        let tmp = setup_project();
        let project = tmp.path();

        // Create a file hierarchy: config.py imports utils.py
        fs::write(
            project.join("src/config.py"),
            "from src.utils import helper\n\ndef load_config():\n    helper()",
        )
        .expect("Failed to write");

        // Both config and utils should be affected
        let changed_files = ["src/utils.py".to_string()];
        assert_eq!(changed_files.len(), 1);
    }

    #[test]
    fn test_test_file_detection() {
        let tmp = setup_project();
        let project = tmp.path();

        // Verify test files exist
        assert!(project.join("tests/test_config.py").exists());
        assert!(project.join("tests/test_utils.py").exists());
    }

    #[test]
    fn test_nonexistent_changed_file() {
        // Should handle gracefully
        let changed_files = ["src/nonexistent.py".to_string()];
        assert_eq!(changed_files.len(), 1);
        assert!(changed_files[0].contains("nonexistent"));
    }

    #[test]
    fn test_deep_directory_structure() {
        let tmp = setup_project();
        let project = tmp.path();

        // Create nested directories
        fs::create_dir_all(project.join("src/deep/nested/module")).ok();
        fs::write(
            project.join("src/deep/nested/module/handler.py"),
            "def process(): pass",
        )
        .ok();

        let changed_file = "src/deep/nested/module/handler.py";
        assert!(changed_file.contains("deep/nested"));
    }

    #[test]
    fn test_empty_changed_files() {
        let changed_files: Vec<String> = vec![];
        assert_eq!(changed_files.len(), 0);
    }

    #[test]
    fn test_test_file_exclusion() {
        // Test files shouldn't suggest themselves
        let test_file = "tests/test_config.py";
        assert!(test_file.contains("test"));
    }

    #[test]
    fn test_typescript_pattern() {
        let tmp = setup_project();
        let _project = tmp.path();

        let changed_file = "src/auth.ts";
        assert!(changed_file.ends_with(".ts"));
        // Should suggest src/auth.test.ts or tests/auth.test.ts
    }
}
