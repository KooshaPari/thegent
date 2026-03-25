use clap::Parser;
use std::process::{Command, ExitCode};

use thegent_shims::utils::{exec_command, resolve_binary};

#[derive(Parser)]
#[command(name = "thegent-git-checkout")]
#[command(about = "Git checkout wrapper with clean-worktree guard")]
struct Args {
    #[arg(trailing_var_arg = true)]
    args: Vec<String>,
}

fn is_inside_git_worktree(git_bin: &std::path::Path) -> bool {
    match Command::new(git_bin)
        .arg("rev-parse")
        .arg("--is-inside-work-tree")
        .output()
    {
        Ok(output) => output.status.success() && output.stdout == b"true\n",
        Err(_) => false,
    }
}

fn is_worktree_clean(git_bin: &std::path::Path) -> Option<bool> {
    match Command::new(git_bin)
        .arg("status")
        .arg("--porcelain")
        .output()
    {
        Ok(output) => {
            if !output.status.success() {
                return Some(false);
            }
            let status = String::from_utf8_lossy(&output.stdout);
            Some(status.lines().all(|line| line.trim().is_empty()))
        }
        Err(_) => None,
    }
}

fn run_checkout(args: &[String]) -> ExitCode {
    let git_path = match resolve_binary("git") {
        Some(path) => path,
        None => {
            eprintln!("thegent-git-checkout: git not found in PATH");
            return ExitCode::from(127);
        }
    };

    if is_inside_git_worktree(&git_path) {
        match is_worktree_clean(&git_path) {
            Some(false) => {
                eprintln!("thegent-git-checkout: blocked checkout on dirty working tree.");
                eprintln!("Please commit/stage/reset/discard changes before retrying.");
                return ExitCode::from(1);
            }
            Some(true) => {}
            None => {
                eprintln!("thegent-git-checkout: failed to read git status; refusing checkout.");
                return ExitCode::from(1);
            }
        }
    }

    let mut git_args = Vec::with_capacity(args.len() + 1);
    git_args.push("checkout".to_string());
    git_args.extend_from_slice(args);
    exec_command(git_path.to_str().unwrap_or("git"), &git_args)
}

fn main() -> ExitCode {
    let args = Args::parse();
    run_checkout(&args.args)
}
