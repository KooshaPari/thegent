use std::fs;
use std::io::{self, Read};
use std::path::PathBuf;
use std::process::ExitCode;

use serde::Deserialize;
use thegent_hooks::{SecurityFinding, SecurityScanner, Severity};

#[derive(Debug, Deserialize)]
struct SecurityPipelineInput {
    #[serde(default)]
    text: String,
    #[serde(default)]
    files: Vec<PathBuf>,
    #[serde(default)]
    semgrep_json: Option<String>,
    #[serde(default = "default_fail_on")]
    fail_on: SeverityThreshold,
}

#[derive(Debug, Clone, Copy, Deserialize)]
#[serde(rename_all = "lowercase")]
enum SeverityThreshold {
    Info,
    Warning,
    Error,
    Critical,
}

fn default_fail_on() -> SeverityThreshold {
    SeverityThreshold::Warning
}

fn meets_threshold(sev: &Severity, threshold: SeverityThreshold) -> bool {
    let sev_rank = match sev {
        Severity::Info => 0_u8,
        Severity::Warning => 1_u8,
        Severity::Error => 2_u8,
        Severity::Critical => 3_u8,
    };
    let threshold_rank = match threshold {
        SeverityThreshold::Info => 0_u8,
        SeverityThreshold::Warning => 1_u8,
        SeverityThreshold::Error => 2_u8,
        SeverityThreshold::Critical => 3_u8,
    };
    sev_rank >= threshold_rank
}

fn main() -> ExitCode {
    let mut stdin = String::new();
    if let Err(err) = io::stdin().read_to_string(&mut stdin) {
        eprintln!("security-pipeline: failed to read stdin: {err}");
        return ExitCode::from(124);
    }

    let input: SecurityPipelineInput = match serde_json::from_str(&stdin) {
        Ok(v) => v,
        Err(err) => {
            eprintln!("security-pipeline: invalid input JSON: {err}");
            return ExitCode::from(124);
        }
    };

    let scanner = SecurityScanner::new();
    let mut findings: Vec<SecurityFinding> = Vec::new();

    if !input.text.is_empty() {
        findings.extend(scanner.scan_text(&input.text));
    }

    for file in &input.files {
        let content = match fs::read_to_string(file) {
            Ok(c) => c,
            Err(err) => {
                eprintln!(
                    "security-pipeline: failed reading {}: {err}",
                    file.display()
                );
                return ExitCode::from(124);
            }
        };
        findings.extend(scanner.scan_text(&content));
    }

    if let Some(semgrep_json) = input.semgrep_json.as_ref() {
        match SecurityScanner::parse_semgrep_json(semgrep_json) {
            Ok(parsed) => findings.extend(parsed),
            Err(err) => {
                eprintln!("security-pipeline: semgrep parse failed: {err}");
                return ExitCode::from(124);
            }
        }
    }

    let blocking: Vec<&SecurityFinding> = findings
        .iter()
        .filter(|f| meets_threshold(&f.severity, input.fail_on))
        .collect();

    if blocking.is_empty() {
        println!("security-pipeline: pass");
        ExitCode::SUCCESS
    } else {
        for finding in blocking {
            eprintln!(
                "[{:?}] {} {} {}",
                finding.severity, finding.id, finding.category, finding.message
            );
        }
        ExitCode::from(1)
    }
}
