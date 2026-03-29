/// Core types for thegent-hooks governance library
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct PolicyRule {
    pub id: String,
    pub name: String,
    pub description: String,
    pub rule_type: RuleType,
    pub condition: String,
    pub severity: Severity,
    pub enabled: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum RuleType {
    #[serde(rename = "cost")]
    Cost,
    #[serde(rename = "quality")]
    Quality,
    #[serde(rename = "security")]
    Security,
    #[serde(rename = "spec")]
    Spec,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
pub enum Severity {
    #[serde(rename = "info")]
    Info,
    #[serde(rename = "warning")]
    Warning,
    #[serde(rename = "error")]
    Error,
    #[serde(rename = "critical")]
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QualityMetrics {
    pub coverage_percent: f64,
    pub lint_issues: u32,
    pub lint_errors: u32,
    pub lint_warnings: u32,
    pub cyclomatic_complexity: u32,
    pub cognitive_complexity: u32,
    pub function_max_lines: u32,
}

impl Default for QualityMetrics {
    fn default() -> Self {
        QualityMetrics {
            coverage_percent: 0.0,
            lint_issues: 0,
            lint_errors: 0,
            lint_warnings: 0,
            cyclomatic_complexity: 0,
            cognitive_complexity: 0,
            function_max_lines: 0,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityFinding {
    pub id: String,
    pub severity: Severity,
    pub category: String,
    pub message: String,
    pub location: Option<String>,
    pub remediation: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyOutcome {
    pub rule_id: String,
    pub passed: bool,
    pub message: String,
    pub details: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CostEstimate {
    pub model: String,
    pub input_tokens: u32,
    pub output_tokens: u32,
    pub input_cost_usd: f64,
    pub output_cost_usd: f64,
    pub total_cost_usd: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LintIssue {
    pub rule: String,
    pub severity: String,
    pub message: String,
    pub file: Option<String>,
    pub line: Option<u32>,
    pub column: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HookConfig {
    pub policies: Vec<PolicyRule>,
    pub cost_limits: HashMap<String, f64>,
    pub quality_thresholds: QualityThresholds,
    pub security_rules: Vec<SecurityRule>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QualityThresholds {
    pub min_coverage: f64,
    pub max_lint_errors: u32,
    pub max_cyclomatic_complexity: u32,
    pub max_cognitive_complexity: u32,
    pub max_function_lines: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityRule {
    pub id: String,
    pub pattern: String,
    pub description: String,
    pub severity: Severity,
}

#[derive(Debug)]
pub enum HookError {
    IoError(String),
    JsonError(String),
    YamlError(String),
    ParseError(String),
    ValidationError(String),
    UnknownModel(String),
}

impl std::fmt::Display for HookError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            HookError::IoError(msg) => write!(f, "IO Error: {}", msg),
            HookError::JsonError(msg) => write!(f, "JSON Error: {}", msg),
            HookError::YamlError(msg) => write!(f, "YAML Error: {}", msg),
            HookError::ParseError(msg) => write!(f, "Parse Error: {}", msg),
            HookError::ValidationError(msg) => write!(f, "Validation Error: {}", msg),
            HookError::UnknownModel(msg) => write!(f, "Unknown Model: {}", msg),
        }
    }
}

impl std::error::Error for HookError {}
