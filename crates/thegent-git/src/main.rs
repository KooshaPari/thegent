//! BKM-06: thegent-git CLI binary.
//!
//! Uses the unified lib.rs API which dispatches to the gix backend by default
//! (pure Rust, no C deps) or falls back to git2/libgit2 when the `gix`
//! feature flag is disabled.
//!
//! Output: newline-terminated JSON to stdout.
//! Exit codes: 0 = success, 1 = git error, 2 = not a git repository.

#![cfg(feature = "cli")]

use clap::{Parser, Subcommand};
use serde_json::json;
use std::path::PathBuf;
use std::process;

// The lib exports a unified API regardless of which backend is active.
use thegent_git::{branch_name, diff_stats, head_sha, status_short};

#[derive(Parser)]
#[command(
    name = "thegent-git",
    version,
    about = "BKM-06: Native git metadata for thegent (HEAD, status, diff-stat)"
)]
struct Cli {
    /// Repository path (defaults to current directory)
    #[arg(short = 'C', long, default_value = ".")]
    repo: PathBuf,

    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Print current HEAD SHA and branch name as JSON
    Head,
    /// Print working-tree status (modified, untracked, staged) as JSON
    Status,
    /// Print diff stats vs HEAD (files_changed, insertions, deletions) as JSON
    DiffStat,
}

fn exit_code(err: &str) -> ! {
    let code = if err.contains("not a git repository") {
        2
    } else {
        1
    };
    eprintln!("error: {err}");
    process::exit(code);
}

fn cmd_head(repo_path: &PathBuf) {
    let p = repo_path.to_string_lossy();
    let sha = match head_sha(&p) {
        Ok(Some(s)) => s,
        Ok(None) => String::new(), // unborn HEAD
        Err(e) => exit_code(&e),
    };
    let branch = match branch_name(&p) {
        Ok(Some(b)) => b,
        Ok(None) => "HEAD".to_string(), // detached HEAD
        Err(e) => exit_code(&e),
    };
    println!("{}", json!({ "sha": sha, "branch": branch }));
}

fn cmd_status(repo_path: &PathBuf) {
    let p = repo_path.to_string_lossy();
    let short = match status_short(&p) {
        Ok(s) => s,
        Err(e) => exit_code(&e),
    };

    let mut modified: Vec<String> = Vec::new();
    let mut untracked: Vec<String> = Vec::new();
    let mut staged: Vec<String> = Vec::new();

    for line in short.lines() {
        if let Some((code, rest)) = line.split_once(' ') {
            match code {
                "M" | "D" | "R" => modified.push(rest.to_string()),
                "A" => staged.push(rest.to_string()),
                "?" => untracked.push(rest.to_string()),
                _ => {}
            }
        }
    }

    println!(
        "{}",
        json!({
            "modified": modified,
            "untracked": untracked,
            "staged": staged,
        })
    );
}

fn cmd_diff_stat(repo_path: &PathBuf) {
    let p = repo_path.to_string_lossy();
    let (files, ins, del) = match diff_stats(&p) {
        Ok(stats) => stats,
        Err(e) => exit_code(&e),
    };
    println!(
        "{}",
        json!({
            "files_changed": files,
            "insertions": ins,
            "deletions": del,
        })
    );
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Command::Head => cmd_head(&cli.repo),
        Command::Status => cmd_status(&cli.repo),
        Command::DiffStat => cmd_diff_stat(&cli.repo),
    }
}
