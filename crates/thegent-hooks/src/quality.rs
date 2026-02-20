/// Quality metrics evaluator for lint output and coverage
use crate::types::{HookError, LintIssue, QualityMetrics};
use serde_json::Value;

pub struct QualityEvaluator;

impl QualityEvaluator {
    /// Parse ruff JSON output into LintIssues
    pub fn parse_ruff_json(json_str: &str) -> Result<Vec<LintIssue>, HookError> {
        let value: Value = serde_json::from_str(json_str)
            .map_err(|e| HookError::JsonError(format!("Failed to parse ruff JSON: {}", e)))?;

        let mut issues = Vec::new();

        if let Some(arr) = value.as_array() {
            for issue in arr {
                let lint_issue = LintIssue {
                    rule: issue
                        .get("code")
                        .and_then(|v| v.as_str())
                        .unwrap_or("unknown")
                        .to_string(),
                    severity: issue
                        .get("severity")
                        .and_then(|v| v.as_str())
                        .unwrap_or("warning")
                        .to_string(),
                    message: issue
                        .get("message")
                        .and_then(|v| v.as_str())
                        .unwrap_or("unknown")
                        .to_string(),
                    file: issue.get("filename").and_then(|v| v.as_str()).map(String::from),
                    line: issue.get("location").and_then(|v| {
                        v.get("row").and_then(|r| r.as_u64()).map(|r| r as u32)
                    }),
                    column: issue.get("location").and_then(|v| {
                        v.get("column").and_then(|c| c.as_u64()).map(|c| c as u32)
                    }),
                };
                issues.push(lint_issue);
            }
        }

        Ok(issues)
    }

    /// Parse oxlint JSON output into LintIssues
    pub fn parse_oxlint_json(json_str: &str) -> Result<Vec<LintIssue>, HookError> {
        let value: Value = serde_json::from_str(json_str)
            .map_err(|e| HookError::JsonError(format!("Failed to parse oxlint JSON: {}", e)))?;

        let mut issues = Vec::new();

        // oxlint format: {linter -> [issues]}
        if let Some(obj) = value.as_object() {
            for (_linter, issues_arr) in obj.iter() {
                if let Some(arr) = issues_arr.as_array() {
                    for issue in arr {
                        let lint_issue = LintIssue {
                            rule: issue
                                .get("ruleId")
                                .and_then(|v| v.as_str())
                                .unwrap_or("unknown")
                                .to_string(),
                            severity: issue
                                .get("severity")
                                .and_then(|v| v.as_str())
                                .unwrap_or("warning")
                                .to_string(),
                            message: issue
                                .get("message")
                                .and_then(|v| v.as_str())
                                .unwrap_or("unknown")
                                .to_string(),
                            file: issue.get("filePath").and_then(|v| v.as_str()).map(String::from),
                            line: issue
                                .get("line")
                                .and_then(|v| v.as_u64())
                                .map(|l| l as u32),
                            column: issue
                                .get("column")
                                .and_then(|v| v.as_u64())
                                .map(|c| c as u32),
                        };
                        issues.push(lint_issue);
                    }
                }
            }
        }

        Ok(issues)
    }

    /// Extract coverage percentage from coverage.py JSON format
    pub fn extract_coverage_percent(json_str: &str) -> Result<f64, HookError> {
        let value: Value = serde_json::from_str(json_str)
            .map_err(|e| HookError::JsonError(format!("Failed to parse coverage JSON: {}", e)))?;

        // coverage.py format: {"totals": {"percent_covered": 85.5, ...}}
        if let Some(pct) = value
            .get("totals")
            .and_then(|t| t.get("percent_covered"))
            .and_then(|p| p.as_f64())
        {
            return Ok(pct);
        }

        // Alternative: {"meta": ..., "coverage": {... "summary": {"percent_covered": 85.5}}}
        if let Some(pct) = value
            .get("coverage")
            .and_then(|c| c.get("summary"))
            .and_then(|s| s.get("percent_covered"))
            .and_then(|p| p.as_f64())
        {
            return Ok(pct);
        }

        Err(HookError::ParseError(
            "Could not find coverage percentage in JSON".to_string(),
        ))
    }

    /// Count lint issues by severity
    pub fn count_by_severity(issues: &[LintIssue]) -> (u32, u32, u32) {
        let mut errors = 0;
        let mut warnings = 0;
        let mut info = 0;

        for issue in issues {
            match issue.severity.as_str() {
                "error" | "ERROR" => errors += 1,
                "warning" | "WARNING" => warnings += 1,
                _ => info += 1,
            }
        }

        (errors, warnings, info)
    }

    /// Aggregate quality metrics from lint and coverage data
    pub fn aggregate_metrics(
        lint_issues: &[LintIssue],
        coverage_percent: f64,
    ) -> QualityMetrics {
        let (errors, warnings, _info) = Self::count_by_severity(lint_issues);

        QualityMetrics {
            coverage_percent,
            lint_issues: lint_issues.len() as u32,
            lint_errors: errors,
            lint_warnings: warnings,
            cyclomatic_complexity: 0,
            cognitive_complexity: 0,
            function_max_lines: 0,
        }
    }

    /// Measure complexity metrics for a file
    pub fn measure_complexity(path: &std::path::Path) -> Result<QualityMetrics, HookError> {
        let content = std::fs::read_to_string(path)
            .map_err(|e| HookError::IoError(format!("Failed to read {}: {}", path.display(), e)))?;
        
        let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
        
        let mut cyc = 0;
        let mut cog = 0;
        let mut max_nest = 0;
        let mut line_count = 0;
        let mut current_nest = 0;
        
        for line in content.lines() {
            line_count += 1;
            let trimmed = line.trim();
            if trimmed.is_empty() || trimmed.starts_with('#') || trimmed.starts_with("//") { continue; }
            
            // Simplified nesting and complexity proxies
            match ext {
                "py" => {
                    // Python: indentation based
                    let indent = line.len() - line.trim_start().len();
                    let level = indent / 4;
                    if level > max_nest { max_nest = level; }
                    
                    if trimmed.contains("if ") || trimmed.contains("elif ") || trimmed.contains("for ") || 
                       trimmed.contains("while ") || trimmed.contains("except ") || trimmed.contains("with ") {
                        cyc += 1;
                        cog += 1 + level;
                    }
                    if trimmed.contains(" and ") || trimmed.contains(" or ") {
                        cyc += 1;
                        cog += 1;
                    }
                },
                "js" | "ts" | "jsx" | "tsx" | "rs" | "go" | "java" | "kt" => {
                    // Brace based
                    for c in trimmed.chars() {
                        if c == '{' {
                            current_nest += 1;
                            if current_nest > max_nest { max_nest = current_nest; }
                        } else if c == '}' {
                            if current_nest > 0 { current_nest -= 1; }
                        }
                    }
                    
                    if trimmed.contains("if ") || trimmed.contains("else if") || trimmed.contains("for ") || 
                       trimmed.contains("while ") || trimmed.contains("switch ") || trimmed.contains("case ") ||
                       trimmed.contains("catch ") {
                        cyc += 1;
                        cog += 1 + current_nest;
                    }
                    if trimmed.contains(" && ") || trimmed.contains(" || ") || trimmed.contains(" ?? ") {
                        cyc += 1;
                        cog += 1;
                    }
                },
                _ => {}
            }
        }
        
        Ok(QualityMetrics {
            coverage_percent: 0.0,
            lint_issues: 0,
            lint_errors: 0,
            lint_warnings: 0,
            cyclomatic_complexity: cyc as u32,
            cognitive_complexity: cog as u32,
            function_max_lines: max_nest as u32, // Reusing field for nesting depth for now
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_ruff_json() {
        let json = r#"
        [
            {
                "code": "E501",
                "severity": "warning",
                "message": "Line too long",
                "filename": "test.py",
                "location": {"row": 10, "column": 80}
            }
        ]
        "#;

        let issues = QualityEvaluator::parse_ruff_json(json).unwrap();
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule, "E501");
        assert_eq!(issues[0].severity, "warning");
    }

    #[test]
    fn test_parse_oxlint_json() {
        let json = r#"
        {
            "eslint": [
                {
                    "ruleId": "no-unused-vars",
                    "severity": "error",
                    "message": "Variable unused",
                    "filePath": "test.js",
                    "line": 5,
                    "column": 10
                }
            ]
        }
        "#;

        let issues = QualityEvaluator::parse_oxlint_json(json).unwrap();
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule, "no-unused-vars");
    }

    #[test]
    fn test_extract_coverage() {
        let json = r#"
        {
            "totals": {
                "percent_covered": 85.5
            }
        }
        "#;

        let coverage = QualityEvaluator::extract_coverage_percent(json).unwrap();
        assert_eq!(coverage, 85.5);
    }

    #[test]
    fn test_count_by_severity() {
        let issues = vec![
            LintIssue {
                rule: "E1".to_string(),
                severity: "error".to_string(),
                message: "err".to_string(),
                file: None,
                line: None,
                column: None,
            },
            LintIssue {
                rule: "W1".to_string(),
                severity: "warning".to_string(),
                message: "warn".to_string(),
                file: None,
                line: None,
                column: None,
            },
        ];

        let (errors, warnings, info) = QualityEvaluator::count_by_severity(&issues);
        assert_eq!(errors, 1);
        assert_eq!(warnings, 1);
        assert_eq!(info, 0);
    }
}
