//! Post-Edit Checker hook binary
//!
//! Detects AI-generated patterns (slop) and measures code complexity.

#![allow(unused)]

use std::fs;
use std::io::{self, Read};
use std::path::PathBuf;
use std::process::ExitCode;

use regex::Regex;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct PostEditCheckerInput {
    /// Project directory
    project_dir: PathBuf,
    /// Changed files (JSON array)
    #[serde(default)]
    changed_files: Vec<String>,
    /// Check for AI slop patterns
    #[serde(default = "default_true")]
    check_ai_slop: bool,
    /// Check complexity
    #[serde(default = "default_true")]
    check_complexity: bool,
}

fn default_true() -> bool {
    true
}

fn detect_ai_slop(content: &str) -> Vec<String> {
    let mut issues = Vec::new();

    let patterns = [
        (r"(?i)as an ai", "AI self-reference"),
        (r"(?i)i cannot|i am unable|i'm sorry", "AI apology/refusal"),
        (r"(?i)todo:?\s*implement", "TODO: implement placeholder"),
        (r"(?i)lorem ipsum", "Lorem ipsum placeholder"),
        (r"(?i)placeholder", "Placeholder text"),
        (r"example\.com", "Example domain in non-test"),
    ];

    for (pattern, desc) in &patterns {
        if let Ok(re) = Regex::new(pattern) {
            if re.is_match(content) {
                issues.push(desc.to_string());
            }
        }
    }

    issues
}

fn measure_complexity(content: &str) -> (usize, usize) {
    // Simple cyclomatic complexity: count branches
    let mut branches = 0;
    let mut functions = 0;

    for line in content.lines() {
        let trimmed = line.trim();
        if trimmed.contains("if ") || trimmed.starts_with("if ") {
            branches += 1;
        }
        if trimmed.contains("for ") || trimmed.contains("while ") {
            branches += 1;
        }
        if trimmed.contains("match ") || trimmed.contains("switch ") {
            branches += 1;
        }
        if trimmed.contains("fn ") || trimmed.contains("def ") || trimmed.contains("function ") {
            functions += 1;
        }
    }

    (branches, functions)
}

fn main() -> ExitCode {
    let mut stdin = String::new();
    if let Err(err) = io::stdin().read_to_string(&mut stdin) {
        eprintln!("post-edit-checker: failed to read stdin: {err}");
        return ExitCode::from(2);
    }

    let input: PostEditCheckerInput = match serde_json::from_str(&stdin) {
        Ok(v) => v,
        Err(err) => {
            eprintln!("post-edit-checker: invalid input JSON: {err}");
            return ExitCode::from(2);
        }
    };

    let mut ai_slop_issues: Vec<String> = Vec::new();
    let mut complexity_warnings: Vec<String> = Vec::new();

    for file in &input.changed_files {
        if let Ok(content) = fs::read_to_string(file) {
            // AI slop detection
            if input.check_ai_slop {
                let issues = detect_ai_slop(&content);
                for issue in issues {
                    ai_slop_issues.push(format!("{}: {}", file, issue));
                }
            }

            // Complexity check
            if input.check_complexity {
                let (branches, funcs) = measure_complexity(&content);
                if funcs > 0 && branches / funcs > 10 {
                    complexity_warnings.push(format!(
                        "{}: high complexity ({} branches in {} funcs)",
                        file, branches, funcs
                    ));
                }
            }
        }
    }

    let has_issues = !ai_slop_issues.is_empty() || !complexity_warnings.is_empty();
    let exit_code = if has_issues { 1 } else { 0 };

    println!(
        r#"{{"ai_slop_issues":{:?}, "complexity_warnings":{:?}, "exit_code":{}}}"#,
        ai_slop_issues, complexity_warnings, exit_code
    );

    if has_issues {
        for issue in &ai_slop_issues {
            eprintln!("post-edit-checker: AI slop: {}", issue);
        }
        for warn in &complexity_warnings {
            eprintln!("post-edit-checker: complexity: {}", warn);
        }
    }

    ExitCode::from(exit_code)
}
