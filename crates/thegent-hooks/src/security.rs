/// Security scanning: secret detection and SAST integration
use crate::types::{HookError, SecurityFinding, Severity};
use regex::Regex;
use serde_json::Value;

pub struct SecurityScanner {
    patterns: Vec<SecretPattern>,
}

struct SecretPattern {
    name: String,
    pattern: Regex,
    severity: Severity,
}

impl SecurityScanner {
    /// Create a new security scanner with default patterns
    pub fn new() -> Self {
        let patterns = vec![
            SecretPattern {
                name: "OpenAI API Key".to_string(),
                pattern: Regex::new(r"sk-[a-zA-Z0-9-]{20,}").unwrap(),
                severity: Severity::Critical,
            },
            SecretPattern {
                name: "GitHub Token".to_string(),
                pattern: Regex::new(r"ghp_[a-zA-Z0-9]{36,}").unwrap(),
                severity: Severity::Critical,
            },
            SecretPattern {
                name: "GitHub OAuth Token".to_string(),
                pattern: Regex::new(r"gho_[a-zA-Z0-9]{36,}").unwrap(),
                severity: Severity::Critical,
            },
            SecretPattern {
                name: "AWS Access Key".to_string(),
                pattern: Regex::new(r"AKIA[0-9A-Z]{16}").unwrap(),
                severity: Severity::Critical,
            },
            SecretPattern {
                name: "Slack API Token".to_string(),
                pattern: Regex::new(r"xox[bapru]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32}")
                    .unwrap(),
                severity: Severity::Critical,
            },
            SecretPattern {
                name: "Private Key".to_string(),
                pattern: Regex::new(
                    r"-----BEGIN (?:RSA|DSA|EC|PGP|ENCRYPTED|OPENSSH) PRIVATE KEY-----",
                )
                .unwrap(),
                severity: Severity::Critical,
            },
            SecretPattern {
                name: "JWT Token".to_string(),
                pattern: Regex::new(r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.").unwrap(),
                severity: Severity::Error,
            },
            SecretPattern {
                name: "Database Password".to_string(),
                pattern: Regex::new(
                    r#"(?:password|passwd|pwd)\s*[=:]\s*['"]?[a-zA-Z0-9!@#$%^&*()_+=\-]{8,}['"]?"#,
                )
                .unwrap(),
                severity: Severity::Error,
            },
        ];

        SecurityScanner { patterns }
    }

    /// Scan text for secret patterns
    pub fn scan_text(&self, content: &str) -> Vec<SecurityFinding> {
        let mut findings = Vec::new();

        for (line_num, line) in content.lines().enumerate() {
            for pattern in &self.patterns {
                if pattern.pattern.is_match(line) {
                    findings.push(SecurityFinding {
                        id: format!("SEC-{:04}", findings.len() + 1),
                        severity: pattern.severity.clone(),
                        category: "Secret Detected".to_string(),
                        message: format!("Potential {} found", pattern.name),
                        location: Some(format!("Line {}", line_num + 1)),
                        remediation: Some(format!(
                            "Remove {} from code and rotate if necessary",
                            pattern.name
                        )),
                    });
                }
            }
        }

        findings
    }

    /// Parse semgrep JSON output into SecurityFindings
    pub fn parse_semgrep_json(json_str: &str) -> Result<Vec<SecurityFinding>, HookError> {
        let value: Value = serde_json::from_str(json_str)
            .map_err(|e| HookError::JsonError(format!("Failed to parse semgrep JSON: {}", e)))?;

        let mut findings = Vec::new();

        if let Some(arr) = value.get("results").and_then(|v| v.as_array()) {
            for result in arr {
                let finding = SecurityFinding {
                    id: format!("SEMGREP-{}", findings.len() + 1),
                    severity: Self::parse_severity(
                        result
                            .get("extra")
                            .and_then(|e| e.get("severity"))
                            .and_then(|s| s.as_str())
                            .unwrap_or("WARNING"),
                    ),
                    category: result
                        .get("check_id")
                        .and_then(|v| v.as_str())
                        .unwrap_or("unknown")
                        .to_string(),
                    message: result
                        .get("extra")
                        .and_then(|e| e.get("message"))
                        .and_then(|m| m.as_str())
                        .unwrap_or("Security issue detected")
                        .to_string(),
                    location: result
                        .get("path")
                        .and_then(|p| p.as_str())
                        .map(String::from),
                    remediation: None,
                };
                findings.push(finding);
            }
        }

        Ok(findings)
    }

    /// Parse severity string to Severity enum
    fn parse_severity(sev: &str) -> Severity {
        match sev.to_uppercase().as_str() {
            "CRITICAL" => Severity::Critical,
            "ERROR" => Severity::Error,
            "WARNING" | "WARN" => Severity::Warning,
            _ => Severity::Info,
        }
    }

    /// Add custom pattern
    pub fn add_pattern(
        &mut self,
        name: &str,
        pattern_str: &str,
        severity: Severity,
    ) -> Result<(), HookError> {
        let regex = Regex::new(pattern_str)
            .map_err(|e| HookError::ParseError(format!("Invalid regex: {}", e)))?;

        self.patterns.push(SecretPattern {
            name: name.to_string(),
            pattern: regex,
            severity,
        });

        Ok(())
    }
}

impl Default for SecurityScanner {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_openai_key() {
        let scanner = SecurityScanner::new();
        let text = "export OPENAI_KEY=sk-proj-1234567890123456789012345";
        let findings = scanner.scan_text(text);
        assert!(!findings.is_empty());
        assert_eq!(findings[0].severity, Severity::Critical);
    }

    #[test]
    fn test_detect_github_token() {
        let scanner = SecurityScanner::new();
        let text = "token = ghp_1234567890123456789012345678901234567890";
        let findings = scanner.scan_text(text);
        assert!(!findings.is_empty());
    }

    #[test]
    fn test_detect_private_key() {
        let scanner = SecurityScanner::new();
        let text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...";
        let findings = scanner.scan_text(text);
        assert!(!findings.is_empty());
    }

    #[test]
    fn test_no_false_positives_on_clean_code() {
        let scanner = SecurityScanner::new();
        let text = "fn main() {\n    println!(\"Hello, world!\");\n}";
        let findings = scanner.scan_text(text);
        assert_eq!(findings.len(), 0);
    }

    #[test]
    fn test_parse_semgrep_json() {
        let json = r#"
        {
            "results": [
                {
                    "check_id": "python.flask.security.xss.template-injection",
                    "extra": {
                        "severity": "ERROR",
                        "message": "Potential template injection"
                    },
                    "path": "app.py"
                }
            ]
        }
        "#;

        let findings = SecurityScanner::parse_semgrep_json(json).unwrap();
        assert_eq!(findings.len(), 1);
        assert_eq!(findings[0].severity, Severity::Error);
    }
}
