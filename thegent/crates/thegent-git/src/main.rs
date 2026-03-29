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
use std::path::Path;
use std::path::PathBuf;
use std::process;
use std::process::Command as ProcCommand;

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

fn head_sha(path: &str) -> Result<Option<String>, String> {
    let out = ProcCommand::new("git")
        .arg("-C")
        .arg(path)
        .arg("rev-parse")
        .arg("--verify")
        .arg("HEAD")
        .output()
        .map_err(|e| e.to_string())?;
    if out.status.success() {
        Ok(Some(
            String::from_utf8_lossy(&out.stdout).trim().to_string(),
        ))
    } else {
        Ok(None)
    }
}

fn branch_name(path: &str) -> Result<Option<String>, String> {
    let out = ProcCommand::new("git")
        .arg("-C")
        .arg(path)
        .arg("rev-parse")
        .arg("--abbrev-ref")
        .arg("HEAD")
        .output()
        .map_err(|e| e.to_string())?;
    if !out.status.success() {
        return Err(String::from_utf8_lossy(&out.stderr).trim().to_string());
    }
    let name = String::from_utf8_lossy(&out.stdout).trim().to_string();
    if name == "HEAD" || name.is_empty() {
        Ok(None)
    } else {
        Ok(Some(name))
    }
}

fn status_short(path: &str) -> Result<String, String> {
    let out = ProcCommand::new("git")
        .arg("-C")
        .arg(path)
        .arg("status")
        .arg("--porcelain")
        .output()
        .map_err(|e| e.to_string())?;
    if !out.status.success() {
        return Err(String::from_utf8_lossy(&out.stderr).trim().to_string());
    }
    Ok(String::from_utf8_lossy(&out.stdout).to_string())
}

fn diff_stats(path: &str) -> Result<(u64, u64, u64), String> {
    let out = ProcCommand::new("git")
        .arg("-C")
        .arg(path)
        .arg("diff")
        .arg("--shortstat")
        .arg("HEAD")
        .output()
        .map_err(|e| e.to_string())?;
    if !out.status.success() {
        return Err(String::from_utf8_lossy(&out.stderr).trim().to_string());
    }
    let txt = String::from_utf8_lossy(&out.stdout);
    let mut files = 0u64;
    let mut ins = 0u64;
    let mut del = 0u64;
    for token in txt.split(',') {
        let t = token.trim();
        if t.contains("file changed") || t.contains("files changed") {
            files = t
                .split_whitespace()
                .next()
                .and_then(|n| n.parse::<u64>().ok())
                .unwrap_or(0);
        } else if t.contains("insertion") {
            ins = t
                .split_whitespace()
                .next()
                .and_then(|n| n.parse::<u64>().ok())
                .unwrap_or(0);
        } else if t.contains("deletion") {
            del = t
                .split_whitespace()
                .next()
                .and_then(|n| n.parse::<u64>().ok())
                .unwrap_or(0);
        }
    }
    Ok((files, ins, del))
}

fn cmd_head(repo_path: &Path) {
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

fn cmd_status(repo_path: &Path) {
    let p = repo_path.to_string_lossy();
    let short = match status_short(&p) {
        Ok(s) => s,
        Err(e) => exit_code(&e),
    };

    let mut modified: Vec<String> = Vec::new();
    let mut untracked: Vec<String> = Vec::new();
    let mut staged: Vec<String> = Vec::new();

    for line in short.lines() {
        if line.len() < 3 {
            continue;
        }
        let code = &line[..2];
        let rest = line[3..].to_string();
        if code == "??" {
            untracked.push(rest);
            continue;
        }
        let x = code.chars().next().unwrap_or(' ');
        let y = code.chars().nth(1).unwrap_or(' ');
        if x != ' ' {
            staged.push(rest.clone());
        }
        if y != ' ' {
            modified.push(rest);
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

fn cmd_diff_stat(repo_path: &Path) {
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
