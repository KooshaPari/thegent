//! QA Policy Test hook binary
//! 
//! Runs governance policy evaluation on changes.

#![allow(unused)]

use std::fs;
use std::io::{self, Read};
use std::path::PathBuf;
use std::process::ExitCode;

use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct QaPolicyTestInput {
    /// Project directory
    project_dir: PathBuf,
    /// Changed files (JSON array)
    #[serde(default)]
    changed_files: Vec<String>,
    /// Policy config path
    #[serde(default)]
    policy_config: Option<PathBuf>,
    /// Whether to fail on warnings
    #[serde(default)]
    fail_on_warnings: bool,
}

fn main() -> ExitCode {
    let mut stdin = String::new();
    if let Err(err) = io::stdin().read_to_string(&mut stdin) {
        eprintln!("qa-policy-test: failed to read stdin: {err}");
        return ExitCode::from(2);
    }

    let input: QaPolicyTestInput = match serde_json::from_str(&stdin) {
        Ok(v) => v,
        Err(err) => {
            eprintln!("qa-policy-test: invalid input JSON: {err}");
            return ExitCode::from(2);
        }
    };

    let mut violations: Vec<String> = Vec::new();
    let mut warnings: Vec<String> = Vec::new();

    // Check for common policy violations
    for file in &input.changed_files {
        // Check for large files
        if let Ok(meta) = fs::metadata(file) {
            if meta.len() > 1_000_000 {
                warnings.push(format!("{}: file size {} bytes", file, meta.len()));
            }
        }
        
        // Check for debug code
        if let Ok(content) = fs::read_to_string(file) {
            if content.contains("println!(") || content.contains("console.log") {
                warnings.push(format!("{}: contains debug output", file));
            }
            if content.contains("TODO") || content.contains("FIXME") {
                warnings.push(format!("{}: contains TODO/FIXME", file));
            }
        }
    }

    let exit_code = if violations.is_empty() {
        if warnings.is_empty() || !input.fail_on_warnings {
            0
        } else {
            1
        }
    } else {
        1
    };

    println!(r#"{{"violations":{:?}, "warnings":{:?}, "exit_code":{}}}"#, 
        violations, warnings, exit_code);

    if exit_code != 0 {
        for w in &warnings {
            eprintln!("qa-policy-test: warning: {}", w);
        }
    }

    ExitCode::from(exit_code)
}
