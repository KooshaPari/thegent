//! Spec-verifier hook binary
//!
//! Scans test directories for FR (Functional Requirement) references.

#![allow(unused)]

use std::fs;
use std::io::{self, Read};
use std::path::PathBuf;
use std::process::ExitCode;

use regex::Regex;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct SpecVerifierInput {
    /// Project directory path
    project_dir: PathBuf,
    /// Path to FUNCTIONAL_REQUIREMENTS.md
    #[serde(default)]
    fr_path: Option<PathBuf>,
    /// Path to test directory
    #[serde(default)]
    test_path: Option<PathBuf>,
    /// Minimum coverage threshold (0.0 - 1.0)
    #[serde(default = "default_threshold")]
    threshold: f64,
}

fn default_threshold() -> f64 {
    0.8
}

fn extract_fr_references(content: &str) -> Vec<String> {
    let mut frs = Vec::new();

    if let Ok(re) = Regex::new(r"FR-[A-Z]+-\d+") {
        for cap in re.find_iter(content) {
            frs.push(cap.as_str().to_string());
        }
    }

    if let Ok(re) = Regex::new(r"@trace\s+(FR-[A-Z]+-\d+)") {
        for cap in re.captures_iter(content) {
            if let Some(m) = cap.get(1) {
                frs.push(m.as_str().to_string());
            }
        }
    }

    if let Ok(re) = Regex::new(r#"pytest\.mark\.requirement\(["'](FR-[A-Z]+-\d+)["']\)"#) {
        for cap in re.captures_iter(content) {
            if let Some(m) = cap.get(1) {
                frs.push(m.as_str().to_string());
            }
        }
    }

    frs
}

fn find_test_files(path: &PathBuf) -> Vec<PathBuf> {
    let mut files = Vec::new();

    if let Ok(entries) = fs::read_dir(path) {
        for entry in entries.flatten() {
            let p = entry.path();
            if p.is_dir() {
                files.extend(find_test_files(&p));
            } else if let Some(ext) = p.extension() {
                if ext == "py" || ext == "rs" || ext == "ts" || ext == "js" {
                    files.push(p);
                }
            }
        }
    }

    files
}

fn main() -> ExitCode {
    let mut stdin = String::new();
    if let Err(err) = io::stdin().read_to_string(&mut stdin) {
        eprintln!("spec-verifier: failed to read stdin: {err}");
        return ExitCode::from(2);
    }

    let input: SpecVerifierInput = match serde_json::from_str(&stdin) {
        Ok(v) => v,
        Err(err) => {
            eprintln!("spec-verifier: invalid input JSON: {err}");
            return ExitCode::from(2);
        }
    };

    let fr_path = input
        .fr_path
        .unwrap_or_else(|| input.project_dir.join("FUNCTIONAL_REQUIREMENTS.md"));
    let test_path = input
        .test_path
        .unwrap_or_else(|| input.project_dir.join("tests"));

    // Read FR requirements
    let fr_content = match fs::read_to_string(&fr_path) {
        Ok(c) => c,
        Err(_) => {
            println!(
                r#"{{"all_frs":[], "covered_frs":[], "orphan_frs":[], "orphan_tests":[], "coverage":1.0,"exit_code":0}}"#
            );
            return ExitCode::from(0);
        }
    };

    let all_frs = extract_fr_references(&fr_content);
    let test_files = find_test_files(&test_path);

    let mut covered_count = 0;
    let mut test_count = 0;

    for test_file in &test_files {
        test_count += 1;
        if let Ok(content) = fs::read_to_string(test_file) {
            let frs = extract_fr_references(&content);
            if !frs.is_empty() {
                covered_count += 1;
            }
        }
    }

    let coverage = if all_frs.is_empty() {
        1.0
    } else {
        covered_count as f64 / all_frs.len() as f64
    };

    let exit_code = if coverage >= input.threshold { 0 } else { 1 };

    println!(
        r#"{{"all_frs":{:?}, "covered_frs":{:?}, "orphan_frs":{:?}, "orphan_tests":{:?}, "coverage":{},"exit_code":{}}}"#,
        all_frs,
        covered_count,
        all_frs.len() - covered_count,
        test_files.len(),
        coverage,
        exit_code
    );

    ExitCode::from(exit_code)
}
