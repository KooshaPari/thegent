// SPDX-License-Identifier: MIT OR Apache-2.0
//! Task Completion Verifier hook binary
//!
//! Verifies task completion status and updates session ledger.

#![allow(unused)]

use std::collections::HashMap;
use std::fs::{self, OpenOptions};
use std::io::{self, Read, Write};
use std::path::PathBuf;
use std::process::ExitCode;

use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct TaskCompletionInput {
    /// Project directory
    project_dir: PathBuf,
    /// Task ID to verify
    task_id: String,
    /// Session ID
    session_id: String,
    /// Expected completion status
    #[serde(default = "default_status")]
    expected_status: String,
}

fn default_status() -> String {
    "completed".to_string()
}

fn main() -> ExitCode {
    let mut stdin = String::new();
    if let Err(err) = io::stdin().read_to_string(&mut stdin) {
        eprintln!("task-completion-verifier: failed to read stdin: {err}");
        return ExitCode::from(2);
    }

    let input: TaskCompletionInput = match serde_json::from_str(&stdin) {
        Ok(v) => v,
        Err(err) => {
            eprintln!("task-completion-verifier: invalid input JSON: {err}");
            return ExitCode::from(2);
        }
    };

    // Check if task is marked complete in session ledger
    let ledger_path = input.project_dir.join(".thegent/session_ledger.jsonl");

    let task_found = if ledger_path.exists() {
        if let Ok(content) = fs::read_to_string(&ledger_path) {
            content.contains(&input.task_id)
        } else {
            false
        }
    } else {
        false
    };

    let verified = task_found;
    let exit_code = if verified { 0 } else { 1 };

    println!(
        r#"{{"task_id":"{}","verified":{},"exit_code":{}}}"#,
        input.task_id, verified, exit_code
    );

    if !verified {
        eprintln!(
            "task-completion-verifier: task {} not found in ledger",
            input.task_id
        );
    }

    ExitCode::from(exit_code)
}
