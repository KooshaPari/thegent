// SPDX-License-Identifier: MIT OR Apache-2.0
//! Hook Execution Reports
//!
//! This module handles generation and management of hook execution reports
//! including performance metrics, issues, and statistics.

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ReportError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("Invalid report format: {0}")]
    InvalidFormat(String),
}

pub type Result<T> = std::result::Result<T, ReportError>;

/// Severity level of an issue
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum IssueSeverity {
    Info,
    Warning,
    Error,
    Critical,
}

/// Type of issue
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum IssueType {
    LintViolation,
    SecurityIssue,
    TestFailure,
    PerformanceDegradation,
    CacheMiss,
    DependencyIssue,
    Other(String),
}

/// Single issue in a report
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Issue {
    /// Issue type
    #[serde(rename = "type")]
    pub issue_type: IssueType,
    /// Severity level
    pub severity: IssueSeverity,
    /// Issue message
    pub message: String,
    /// File path (optional)
    pub file: Option<String>,
    /// Line number (optional)
    pub line: Option<u32>,
    /// Code/rule (optional)
    pub code: Option<String>,
}

/// Performance metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceMetrics {
    /// Total execution time in milliseconds
    pub total_time_ms: u64,
    /// Time spent in cache operations
    pub cache_time_ms: u64,
    /// Time spent in I/O operations
    pub io_time_ms: u64,
    /// Time spent in git operations
    pub git_time_ms: u64,
    /// Time spent in analysis
    pub analysis_time_ms: u64,
    /// Memory usage in MB
    pub memory_mb: f64,
    /// Cache hit rate (0.0 - 1.0)
    pub cache_hit_rate: f64,
}

/// Hook execution statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Statistics {
    /// Number of files processed
    pub files_processed: u32,
    /// Number of files changed
    pub files_changed: u32,
    /// Number of tests run
    pub tests_run: u32,
    /// Number of tests passed
    pub tests_passed: u32,
    /// Number of tests failed
    pub tests_failed: u32,
    /// Number of issues found
    pub issues_found: u32,
    /// Number of lint violations
    pub lint_violations: u32,
    /// Number of security issues
    pub security_issues: u32,
}

/// Single hook execution report
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HookReport {
    /// Hook name
    pub hook_name: String,
    /// Execution timestamp
    pub timestamp: u64,
    /// Session ID
    pub session_id: String,
    /// Exit code (0 = success)
    pub exit_code: i32,
    /// Execution status (success, failure, timeout)
    pub status: String,
    /// Standard output
    pub stdout: String,
    /// Standard error
    pub stderr: String,
    /// Issues found
    pub issues: Vec<Issue>,
    /// Performance metrics
    pub metrics: PerformanceMetrics,
    /// Statistics
    pub statistics: Statistics,
    /// Custom metadata
    pub metadata: serde_json::Value,
}

impl HookReport {
    /// Create a new hook report
    pub fn new(hook_name: String, session_id: String) -> Self {
        Self {
            hook_name,
            timestamp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0),
            session_id,
            exit_code: 0,
            status: "unknown".to_string(),
            stdout: String::new(),
            stderr: String::new(),
            issues: Vec::new(),
            metrics: PerformanceMetrics {
                total_time_ms: 0,
                cache_time_ms: 0,
                io_time_ms: 0,
                git_time_ms: 0,
                analysis_time_ms: 0,
                memory_mb: 0.0,
                cache_hit_rate: 0.0,
            },
            statistics: Statistics {
                files_processed: 0,
                files_changed: 0,
                tests_run: 0,
                tests_passed: 0,
                tests_failed: 0,
                issues_found: 0,
                lint_violations: 0,
                security_issues: 0,
            },
            metadata: serde_json::json!({}),
        }
    }

    /// Add an issue to the report
    pub fn add_issue(&mut self, issue: Issue) {
        match issue.severity {
            IssueSeverity::Error | IssueSeverity::Critical => {
                self.statistics.issues_found += 1;
            }
            _ => {}
        }
        self.issues.push(issue);
    }

    /// Set execution status and exit code
    pub fn set_status(&mut self, status: &str, exit_code: i32) {
        self.status = status.to_string();
        self.exit_code = exit_code;
    }

    /// Check if report indicates success
    pub fn is_success(&self) -> bool {
        self.exit_code == 0 && self.status == "success"
    }

    /// Get highest severity issue
    pub fn highest_severity(&self) -> Option<IssueSeverity> {
        self.issues.iter().map(|i| i.severity).max()
    }
}

/// Report manager for storing and querying reports
pub struct ReportManager {
    report_dir: PathBuf,
}

impl ReportManager {
    /// Create a new report manager
    pub fn new(report_dir: impl AsRef<Path>) -> Result<Self> {
        let report_dir = report_dir.as_ref().to_path_buf();
        fs::create_dir_all(&report_dir)?;
        Ok(ReportManager { report_dir })
    }

    /// Get report directory
    pub fn report_dir(&self) -> &Path {
        &self.report_dir
    }

    /// Write report to file
    pub fn write_report(&self, report: &HookReport) -> Result<PathBuf> {
        let filename = format!(
            "{}_{}_{}.json",
            report.hook_name,
            report.timestamp,
            report.session_id.chars().take(8).collect::<String>()
        );
        let path = self.report_dir.join(&filename);

        let json = serde_json::to_string_pretty(report)?;
        fs::write(&path, json)?;

        Ok(path)
    }

    /// Read report from file
    pub fn read_report(&self, filename: &str) -> Result<HookReport> {
        let path = self.report_dir.join(filename);
        let content = fs::read_to_string(path)?;
        Ok(serde_json::from_str(&content)?)
    }

    /// List all reports for a hook
    pub fn list_reports(&self, hook_name: &str) -> Result<Vec<PathBuf>> {
        let mut reports = Vec::new();

        for entry in fs::read_dir(&self.report_dir)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_file() {
                if let Some(filename) = path.file_name().and_then(|n| n.to_str()) {
                    if filename.starts_with(&format!("{}_", hook_name)) {
                        reports.push(path);
                    }
                }
            }
        }

        reports.sort();
        Ok(reports)
    }

    /// Get latest report for a hook
    pub fn latest_report(&self, hook_name: &str) -> Result<Option<HookReport>> {
        let reports = self.list_reports(hook_name)?;

        if reports.is_empty() {
            return Ok(None);
        }

        let latest = reports
            .last()
            .ok_or_else(|| ReportError::InvalidFormat("No reports found".to_string()))?;

        Ok(Some(self.read_report(
            latest.file_name().and_then(|n| n.to_str()).unwrap_or(""),
        )?))
    }

    /// Generate summary report for multiple hooks
    pub fn generate_summary(&self) -> Result<SummaryReport> {
        let mut summary = SummaryReport::new();
        let mut total_issues = 0;
        let mut total_time = 0;

        for entry in fs::read_dir(&self.report_dir)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_file() {
                if let Some(filename) = path.file_name().and_then(|n| n.to_str()) {
                    if let Ok(report) = self.read_report(filename) {
                        summary.hook_count += 1;
                        total_issues += report.statistics.issues_found;
                        total_time += report.metrics.total_time_ms;

                        if !report.is_success() {
                            summary.failed_hooks.push(report.hook_name.clone());
                        }
                    }
                }
            }
        }

        summary.total_issues = total_issues;
        summary.total_time_ms = total_time;

        Ok(summary)
    }

    /// Delete old reports (older than max_age_seconds)
    pub fn cleanup(&self, max_age_seconds: u64) -> Result<usize> {
        let cutoff = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs())
            .unwrap_or(0)
            - max_age_seconds;

        let mut deleted = 0;

        for entry in fs::read_dir(&self.report_dir)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_file() {
                if let Ok(metadata) = fs::metadata(&path) {
                    if let Ok(modified) = metadata.modified() {
                        if let Ok(elapsed) = SystemTime::now().duration_since(modified) {
                            let mtime = SystemTime::now()
                                .duration_since(UNIX_EPOCH)
                                .map(|d| d.as_secs())
                                .unwrap_or(0)
                                - elapsed.as_secs();

                            if mtime < cutoff {
                                fs::remove_file(&path)?;
                                deleted += 1;
                            }
                        }
                    }
                }
            }
        }

        Ok(deleted)
    }
}

/// Summary report across multiple hooks
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SummaryReport {
    /// Number of hooks with reports
    pub hook_count: u32,
    /// Total issues found
    pub total_issues: u32,
    /// Hooks that failed
    pub failed_hooks: Vec<String>,
    /// Total execution time in ms
    pub total_time_ms: u64,
    /// Timestamp
    pub timestamp: u64,
}

impl SummaryReport {
    pub fn new() -> Self {
        Self {
            hook_count: 0,
            total_issues: 0,
            failed_hooks: Vec::new(),
            total_time_ms: 0,
            timestamp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0),
        }
    }

    pub fn is_healthy(&self) -> bool {
        self.failed_hooks.is_empty() && self.total_issues == 0
    }
}

impl Default for SummaryReport {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hook_report_new() {
        let report = HookReport::new("test-hook".to_string(), "session123".to_string());
        assert_eq!(report.hook_name, "test-hook");
        assert_eq!(report.session_id, "session123");
        assert_eq!(report.exit_code, 0);
        assert!(!report.is_success());
    }

    #[test]
    fn test_hook_report_set_status() {
        let mut report = HookReport::new("test-hook".to_string(), "session123".to_string());
        report.set_status("success", 0);
        assert!(report.is_success());

        report.set_status("failed", 1);
        assert!(!report.is_success());
    }

    #[test]
    fn test_hook_report_add_issue() {
        let mut report = HookReport::new("test-hook".to_string(), "session123".to_string());

        let issue = Issue {
            issue_type: IssueType::LintViolation,
            severity: IssueSeverity::Warning,
            message: "test issue".to_string(),
            file: Some("test.py".to_string()),
            line: Some(10),
            code: Some("E501".to_string()),
        };

        report.add_issue(issue);
        assert_eq!(report.issues.len(), 1);
    }

    #[test]
    fn test_issue_severity_ordering() {
        assert!(IssueSeverity::Info < IssueSeverity::Warning);
        assert!(IssueSeverity::Warning < IssueSeverity::Error);
        assert!(IssueSeverity::Error < IssueSeverity::Critical);
    }

    #[test]
    fn test_summary_report() {
        let mut summary = SummaryReport::new();
        assert!(summary.is_healthy());

        summary.failed_hooks.push("hook1".to_string());
        assert!(!summary.is_healthy());

        summary.failed_hooks.clear();
        summary.total_issues = 5;
        assert!(!summary.is_healthy());
    }
}
