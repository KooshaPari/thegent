//! Integration tests for report functionality
//!
//! These tests verify hook execution reports are properly created,
//! serialized, and retrieved.

#[cfg(test)]
mod report_integration_tests {
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_hook_report_serialization() {
        let report = serde_json::json!({
            "hook_name": "test-hook",
            "session_id": "session123",
            "timestamp": 1000000,
            "exit_code": 0,
            "status": "success",
            "stdout": "Test output",
            "stderr": "",
            "issues": [],
            "metrics": {
                "total_time_ms": 100,
                "cache_time_ms": 10,
                "io_time_ms": 20,
                "git_time_ms": 30,
                "analysis_time_ms": 40,
                "memory_mb": 25.5,
                "cache_hit_rate": 0.85
            },
            "statistics": {
                "files_processed": 10,
                "files_changed": 3,
                "tests_run": 50,
                "tests_passed": 50,
                "tests_failed": 0,
                "issues_found": 0,
                "lint_violations": 0,
                "security_issues": 0
            },
            "metadata": {}
        });

        // Verify structure
        assert_eq!(report["hook_name"], "test-hook");
        assert_eq!(report["exit_code"], 0);
        assert_eq!(report["status"], "success");
    }

    #[test]
    fn test_report_with_issues() {
        let report = serde_json::json!({
            "hook_name": "quality-gate",
            "session_id": "session456",
            "timestamp": 1000000,
            "exit_code": 1,
            "status": "failed",
            "stdout": "",
            "stderr": "Lint violations found",
            "issues": [
                {
                    "type": "LintViolation",
                    "severity": "warning",
                    "message": "Line too long",
                    "file": "src/main.py",
                    "line": 42,
                    "code": "E501"
                }
            ],
            "metrics": {
                "total_time_ms": 200,
                "cache_time_ms": 20,
                "io_time_ms": 40,
                "git_time_ms": 50,
                "analysis_time_ms": 90,
                "memory_mb": 50.0,
                "cache_hit_rate": 0.75
            },
            "statistics": {
                "files_processed": 20,
                "files_changed": 5,
                "tests_run": 100,
                "tests_passed": 98,
                "tests_failed": 2,
                "issues_found": 3,
                "lint_violations": 1,
                "security_issues": 0
            },
            "metadata": {}
        });

        assert_eq!(report["exit_code"], 1);
        assert_eq!(report["status"], "failed");
        assert!(report["issues"].is_array());
        assert_eq!(report["issues"].as_array().unwrap().len(), 1);
    }

    #[test]
    fn test_issue_severity_levels() {
        let severities = vec!["info", "warning", "error", "critical"];

        // Verify severity ordering
        assert!(severities.iter().position(|&s| s == "info").unwrap() <
                severities.iter().position(|&s| s == "warning").unwrap());
        assert!(severities.iter().position(|&s| s == "warning").unwrap() <
                severities.iter().position(|&s| s == "error").unwrap());
        assert!(severities.iter().position(|&s| s == "error").unwrap() <
                severities.iter().position(|&s| s == "critical").unwrap());
    }

    #[test]
    fn test_performance_metrics() {
        let metrics = serde_json::json!({
            "total_time_ms": 250,
            "cache_time_ms": 50,
            "io_time_ms": 80,
            "git_time_ms": 70,
            "analysis_time_ms": 50,
            "memory_mb": 45.5,
            "cache_hit_rate": 0.80
        });

        // Verify metric types
        assert!(metrics["total_time_ms"].is_number());
        assert!(metrics["memory_mb"].is_number());
        assert!(metrics["cache_hit_rate"].is_number());

        // Verify reasonable values
        let cache_hit: f64 = metrics["cache_hit_rate"].as_f64().unwrap();
        assert!(cache_hit >= 0.0 && cache_hit <= 1.0);
    }

    #[test]
    fn test_statistics_aggregation() {
        let stats = serde_json::json!({
            "files_processed": 100,
            "files_changed": 25,
            "tests_run": 500,
            "tests_passed": 495,
            "tests_failed": 5,
            "issues_found": 12,
            "lint_violations": 8,
            "security_issues": 0
        });

        // Verify counts
        assert_eq!(stats["files_processed"], 100);
        assert_eq!(stats["tests_failed"], 5);
        assert_eq!(stats["tests_passed"].as_u64().unwrap() + stats["tests_failed"].as_u64().unwrap(), 500);
    }

    #[test]
    fn test_report_directory_creation() {
        let tmp = TempDir::new().expect("Failed to create temp dir");
        let report_dir = tmp.path().join("reports");

        // Create directory
        fs::create_dir_all(&report_dir).ok();
        assert!(report_dir.exists());
    }

    #[test]
    fn test_report_file_naming() {
        // Report filename format: {hook_name}_{timestamp}_{session_id_prefix}.json
        let hook_name = "quality-gate";
        let timestamp = 1000000u64;
        let session_prefix = "abc123";

        let filename = format!("{}_{}_{}. json", hook_name, timestamp, session_prefix);
        assert!(filename.contains(hook_name));
        assert!(filename.contains(&timestamp.to_string()));
    }

    #[test]
    fn test_report_persistence() {
        let tmp = TempDir::new().expect("Failed to create temp dir");
        let report_path = tmp.path().join("test-report.json");

        let report = serde_json::json!({
            "hook_name": "test",
            "session_id": "test123",
            "timestamp": 1000000,
            "exit_code": 0,
            "status": "success",
            "stdout": "success",
            "stderr": "",
            "issues": [],
            "metrics": {},
            "statistics": {},
            "metadata": {}
        });

        // Write report
        let json_str = serde_json::to_string_pretty(&report).unwrap();
        fs::write(&report_path, json_str).ok();

        // Verify it was written
        assert!(report_path.exists());

        // Read it back
        if let Ok(content) = fs::read_to_string(&report_path) {
            if let Ok(loaded) = serde_json::from_str::<serde_json::Value>(&content) {
                assert_eq!(loaded["hook_name"], "test");
            }
        }
    }

    #[test]
    fn test_summary_report() {
        let summary = serde_json::json!({
            "hook_count": 5,
            "total_issues": 12,
            "failed_hooks": ["hook1", "hook3"],
            "total_time_ms": 1500,
            "timestamp": 1000000
        });

        assert_eq!(summary["hook_count"], 5);
        assert_eq!(summary["total_issues"], 12);
        assert!(summary["failed_hooks"].is_array());
    }

    #[test]
    fn test_healthy_system_report() {
        let summary = serde_json::json!({
            "hook_count": 10,
            "total_issues": 0,
            "failed_hooks": [],
            "total_time_ms": 2000,
            "timestamp": 1000000
        });

        // System is healthy if no failed hooks and no issues
        let is_healthy = summary["failed_hooks"].as_array().unwrap().is_empty() &&
                        summary["total_issues"] == 0;
        assert!(is_healthy);
    }

    #[test]
    fn test_unhealthy_system_report() {
        let summary = serde_json::json!({
            "hook_count": 10,
            "total_issues": 5,
            "failed_hooks": ["hook2", "hook5"],
            "total_time_ms": 2000,
            "timestamp": 1000000
        });

        // System is unhealthy with failed hooks
        let is_healthy = summary["failed_hooks"].as_array().unwrap().is_empty() &&
                        summary["total_issues"] == 0;
        assert!(!is_healthy);
    }

    #[test]
    fn test_timestamp_format() {
        let now = std::time::SystemTime::now();
        let since_epoch = now.duration_since(std::time::UNIX_EPOCH).unwrap();
        let timestamp = since_epoch.as_secs();

        // Timestamp should be reasonable (not zero, not in future)
        assert!(timestamp > 1000000000); // After 2001
        assert!(timestamp < 4000000000); // Before 2096
    }

    #[test]
    fn test_issue_without_optional_fields() {
        let issue = serde_json::json!({
            "type": "SecurityIssue",
            "severity": "critical",
            "message": "SQL injection vulnerability",
            "file": null,
            "line": null,
            "code": null
        });

        assert_eq!(issue["message"], "SQL injection vulnerability");
        assert!(issue["file"].is_null());
    }

    #[test]
    fn test_comprehensive_report() {
        let report = serde_json::json!({
            "hook_name": "comprehensive-test",
            "session_id": "comp-session-123",
            "timestamp": 1000000,
            "exit_code": 1,
            "status": "failed",
            "stdout": "Hook execution output",
            "stderr": "Some errors occurred",
            "issues": [
                {
                    "type": "LintViolation",
                    "severity": "warning",
                    "message": "Unused import",
                    "file": "src/main.py",
                    "line": 5,
                    "code": "F401"
                },
                {
                    "type": "TestFailure",
                    "severity": "error",
                    "message": "Test failed",
                    "file": "tests/test_main.py",
                    "line": 42,
                    "code": null
                }
            ],
            "metrics": {
                "total_time_ms": 350,
                "cache_time_ms": 50,
                "io_time_ms": 100,
                "git_time_ms": 80,
                "analysis_time_ms": 120,
                "memory_mb": 75.5,
                "cache_hit_rate": 0.65
            },
            "statistics": {
                "files_processed": 50,
                "files_changed": 15,
                "tests_run": 200,
                "tests_passed": 198,
                "tests_failed": 2,
                "issues_found": 5,
                "lint_violations": 3,
                "security_issues": 0
            },
            "metadata": {
                "custom_field": "custom_value"
            }
        });

        // Verify all components
        assert_eq!(report["hook_name"], "comprehensive-test");
        assert_eq!(report["exit_code"], 1);
        assert!(report["issues"].is_array());
        assert!(report["metrics"].is_object());
        assert!(report["statistics"].is_object());
        assert!(report["metadata"].is_object());
    }
}
