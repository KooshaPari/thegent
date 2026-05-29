use serde::Serialize;

/// A single governance violation found during file scanning.
#[derive(Serialize)]
pub struct GovernanceViolation {
    /// Rule ID that was violated (e.g. "noqa-no-justification").
    pub rule: String,
    /// Severity level: "error", "warning", or "info".
    pub severity: String,
    /// 1-based line number of the violation.
    pub line: usize,
    /// Human-readable description of the violation.
    pub message: String,
}

/// Top-level JSON output for `hook-dispatcher governance scan`.
#[derive(Serialize)]
pub struct GovernanceScanOutput {
    /// Total number of violations found.
    pub violation_count: usize,
    /// The list of individual violations.
    pub violations: Vec<GovernanceViolation>,
}

impl GovernanceScanOutput {
    pub fn new() -> Self {
        Self {
            violation_count: 0,
            violations: Vec::new(),
        }
    }

    pub fn with_violations(violations: Vec<GovernanceViolation>) -> Self {
        let count = violations.len();
        Self {
            violation_count: count,
            violations,
        }
    }

    pub fn add_violation(&mut self, rule: &str, severity: &str, line: usize, message: &str) {
        self.violations.push(GovernanceViolation {
            rule: rule.to_string(),
            severity: severity.to_string(),
            line,
            message: message.to_string(),
        });
        self.violation_count = self.violations.len();
    }
}

impl Default for GovernanceScanOutput {
    fn default() -> Self {
        Self::new()
    }
}
