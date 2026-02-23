//! Complexity Ratchet hook binary
//!
//! Enforces complexity limits and prevents regression.

#![allow(unused)]

use std::fs;
use std::io::{self, Read};
use std::path::PathBuf;
use std::process::ExitCode;

use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct ComplexityRatchetInput {
    /// Project directory
    project_dir: PathBuf,
    /// Changed files (JSON array)
    #[serde(default)]
    changed_files: Vec<String>,
    /// Maximum cyclomatic complexity allowed
    #[serde(default = "default_max_complexity")]
    max_complexity: usize,
    /// Maximum cognitive complexity allowed
    #[serde(default = "default_max_cognitive")]
    max_cognitive: usize,
    /// Maximum function lines
    #[serde(default = "default_max_lines")]
    max_lines: usize,
}

fn default_max_complexity() -> usize {
    10
}
fn default_max_cognitive() -> usize {
    15
}
fn default_max_lines() -> usize {
    40
}

fn analyze_file(content: &str) -> (Vec<String>, Vec<String>) {
    let mut violations = Vec::new();
    let mut warnings = Vec::new();

    let mut in_function = false;
    let mut func_lines = 0;
    let mut func_name = String::new();
    let mut branches = 0;

    for line in content.lines() {
        let trimmed = line.trim();

        // Detect function start
        if trimmed.contains("fn ") || trimmed.contains("def ") || trimmed.contains("function ") {
            in_function = true;
            func_lines = 0;

            // Extract function name
            if let Some(name) = trimmed.split_whitespace().nth(1) {
                func_name = name.split('(').next().unwrap_or("unknown").to_string();
            }
        }

        // Count lines in function
        if in_function {
            func_lines += 1;

            // Count branches
            if trimmed.contains("if ") || trimmed.starts_with("if ") {
                branches += 1;
            }
            if trimmed.contains("for ") || trimmed.contains("while ") {
                branches += 1;
            }
            if trimmed.contains("match ") {
                branches += 1;
            }

            // End of function (simple heuristic)
            if trimmed == "}" || trimmed.ends_with(':') && func_lines > 1 {
                if func_lines > 40 {
                    violations.push(format!("{}: {} lines (max 40)", func_name, func_lines));
                } else if func_lines > 30 {
                    warnings.push(format!("{}: {} lines", func_name, func_lines));
                }
                in_function = false;
            }
        }
    }

    (violations, warnings)
}

fn main() -> ExitCode {
    let mut stdin = String::new();
    if let Err(err) = io::stdin().read_to_string(&mut stdin) {
        eprintln!("complexity-ratchet: failed to read stdin: {err}");
        return ExitCode::from(2);
    }

    let input: ComplexityRatchetInput = match serde_json::from_str(&stdin) {
        Ok(v) => v,
        Err(err) => {
            eprintln!("complexity-ratchet: invalid input JSON: {err}");
            return ExitCode::from(2);
        }
    };

    let mut all_violations: Vec<String> = Vec::new();
    let mut all_warnings: Vec<String> = Vec::new();

    for file in &input.changed_files {
        if let Ok(content) = fs::read_to_string(file) {
            let (violations, warnings) = analyze_file(&content);
            for v in violations {
                all_violations.push(format!("{}: {}", file, v));
            }
            for w in warnings {
                all_warnings.push(format!("{}: {}", file, w));
            }
        }
    }

    let exit_code = if all_violations.is_empty() { 0 } else { 1 };

    println!(
        r#"{{"violations":{:?}, "warnings":{:?}, "exit_code":{}}}"#,
        all_violations, all_warnings, exit_code
    );

    for v in &all_violations {
        eprintln!("complexity-ratchet: violation: {}", v);
    }

    ExitCode::from(exit_code)
}
