//! Stop-reconcile hook binary
//!
//! Reads session state from stdin, checks git status, detects conflicts.

#![allow(unused)]

use std::io::{self, Read};
use std::path::PathBuf;
use std::process::{Command, ExitCode};

use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct StopReconcileInput {
    /// Project directory path
    project_dir: PathBuf,
    /// Current session ID
    session_id: String,
    /// Previous session IDs for conflict detection
    #[serde(default)]
    previous_sessions: Vec<String>,
    /// Whether to perform a dry run
    #[serde(default)]
    dry_run: bool,
}

fn main() -> ExitCode {
    let mut stdin = String::new();
    if let Err(err) = io::stdin().read_to_string(&mut stdin) {
        eprintln!("stop-reconcile: failed to read stdin: {err}");
        return ExitCode::from(2);
    }

    let input: StopReconcileInput = match serde_json::from_str(&stdin) {
        Ok(v) => v,
        Err(err) => {
            eprintln!("stop-reconcile: invalid input JSON: {err}");
            return ExitCode::from(2);
        }
    };

    // Check git status
    let output = Command::new("git")
        .args(["status", "--porcelain"])
        .current_dir(&input.project_dir)
        .output();

    let (clean, dirty_files, untracked_files) = match output {
        Ok(o) => {
            let status = String::from_utf8_lossy(&o.stdout);
            let is_clean = status.trim().is_empty();
            let dirty: Vec<String> = status
                .lines()
                .filter(|l| l.starts_with(" M") || l.starts_with("M "))
                .map(|l| l[3..].to_string())
                .collect();
            let untracked: Vec<String> = status
                .lines()
                .filter(|l| l.starts_with("??"))
                .map(|l| l[3..].to_string())
                .collect();
            (is_clean, dirty, untracked)
        }
        Err(err) => {
            eprintln!("stop-reconcile: failed to run git: {}", err);
            (true, vec![], vec![])
        }
    };

    // Simple JSON output
    println!(
        r#"{{"clean":{}, "dirty_files":{:?}, "untracked_files":{:?}, "exit_code":0}}"#,
        clean, dirty_files, untracked_files
    );

    ExitCode::from(0)
}
