//! thegent-shims: Efficient shell command shims for thegent
//!
//! Provides fast Rust replacements for shell commands:
//! - git: Git wrapper with thegent integration
//! - grep: Fast grep with thegent context
//! - find: Find with thegent awareness
//! - agent: Agent invocation shim

use clap::{Parser, Subcommand};
use std::env;
use std::path::PathBuf;
use std::process::{Command as StdCommand, ExitCode};

/// thegent-shims - Efficient shell command shims for thegent
#[derive(Parser)]
#[command(name = "thegent-shims")]
#[command(version = "0.1.0")]
#[command(about = "Efficient shell command shims for thegent", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: ShimCommand,
}

#[derive(Subcommand)]
enum ShimCommand {
    /// Git wrapper with thegent integration
    Git {
        /// Arguments to pass to git
        #[arg(trailing_var_arg = true)]
        args: Vec<String>,
    },
    /// Fast grep with thegent context
    Grep {
        /// Arguments to pass to grep/rg
        #[arg(trailing_var_arg = true)]
        args: Vec<String>,
    },
    /// Find with thegent awareness
    Find {
        /// Arguments to pass to find/fd
        #[arg(trailing_var_arg = true)]
        args: Vec<String>,
    },
    /// Agent invocation shim
    Agent {
        /// Agent name (codex, copilot, dex, claude, cursor)
        name: String,
        /// Arguments to pass to the agent
        #[arg(trailing_var_arg = true)]
        args: Vec<String>,
    },
}

/// Resolve the real binary path from PATH
fn resolve_binary(name: &str) -> Option<PathBuf> {
    which::which(name).ok()
}

/// Find the first available tool from a list of candidates
fn first_available(candidates: &[&str]) -> Option<PathBuf> {
    for candidate in candidates {
        if let Ok(path) = which::which(candidate) {
            return Some(path);
        }
    }
    None
}

/// Run git with thegent integration
fn run_git(args: &[String]) -> ExitCode {
    let git_path = resolve_binary("git");
    
    match git_path {
        Some(path) => {
            // Inject thegent context if available
            let mut cmd = StdCommand::new(&path);
            cmd.args(args);
            
            // Preserve relevant environment variables for thegent
            if let Ok(project_dir) = env::var("PROJECT_DIR") {
                cmd.env("PROJECT_DIR", &project_dir);
            }
            if let Ok(session_id) = env::var("SESSION_ID") {
                cmd.env("SESSION_ID", &session_id);
            }
            
            // Execute and propagate exit code
            let status = cmd.status().unwrap_or_else(|e| {
                eprintln!("thegent-shims: failed to execute git: {}", e);
                std::process::exit(1);
            });
            
            let code = status.code().unwrap_or(1);
            ExitCode::from(code as u8)
        }
        None => {
            eprintln!("thegent-shims: git not found in PATH");
            ExitCode::from(127)
        }
    }
}

/// Run grep with thegent context - prefers ripgrep
fn run_grep(args: &[String]) -> ExitCode {
    // Prefer ripgrep, fall back to grep
    let rg_path = first_available(&["rg", "grep", "ggrep", "agrep"]);
    
    match rg_path {
        Some(path) => {
            let cmd_name = path.file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("grep");
            
            // For rg, pass args directly; for grep, may need adjustment
            let final_args: Vec<String> = if cmd_name == "rg" {
                args.to_vec()
            } else {
                // Add -n for line numbers if not present (grep compatibility)
                let mut new_args = vec!["-n".to_string()];
                new_args.extend(args.iter().cloned());
                new_args
            };
            
            let mut cmd = StdCommand::new(&path);
            cmd.args(&final_args);
            
            let status = cmd.status().unwrap_or_else(|e| {
                eprintln!("thegent-shims: failed to execute {}: {}", cmd_name, e);
                std::process::exit(1);
            });
            
            let code = status.code().unwrap_or(1);
            ExitCode::from(code as u8)
        }
        None => {
            eprintln!("thegent-shims: no grep tool found (tried: rg, grep)");
            ExitCode::from(127)
        }
    }
}

/// Run find with thegent awareness - prefers fd, falls back to find
fn run_find(args: &[String]) -> ExitCode {
    // Prefer fd, fall back to find
    let fd_path = first_available(&["fd", "fdfind", "find"]);
    
    match fd_path {
        Some(path) => {
            let cmd_name = path.file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("find");
            
            if cmd_name == "fd" || cmd_name == "fdfind" {
                // fd has different argument structure
                // Convert common find flags to fd equivalents
                let fd_args = args.clone();
                
                // fd defaults to hidden=false, follow=false
                // Common conversions: -name -> -n, -type f -> -t f
                let final_args: Vec<String> = fd_args.iter()
                    .map(|arg| {
                        if arg == "-name" {
                            "-n".to_string()
                        } else if arg == "-type" {
                            "-t".to_string()
                        } else {
                            arg.clone()
                        }
                    })
                    .collect();
                
                let mut cmd = StdCommand::new(&path);
                cmd.args(&final_args);
                
                let status = cmd.status().unwrap_or_else(|e| {
                    eprintln!("thegent-shims: failed to execute fd: {}", e);
                    std::process::exit(1);
                });
                
                let code = status.code().unwrap_or(1);
                ExitCode::from(code as u8)
            } else {
                // Regular find - pass through
                let mut cmd = StdCommand::new(&path);
                cmd.args(args);
                
                let status = cmd.status().unwrap_or_else(|e| {
                    eprintln!("thegent-shims: failed to execute find: {}", e);
                    std::process::exit(1);
                });
                
                let code = status.code().unwrap_or(1);
                ExitCode::from(code as u8)
            }
        }
        None => {
            eprintln!("thegent-shims: no find tool found (tried: fd, find)");
            ExitCode::from(127)
        }
    }
}

/// Resolve agent binary - handles fallback logic (dex -> codex, etc.)
fn resolve_agent(name: &str) -> Option<PathBuf> {
    // Direct names first
    if resolve_binary(name).is_some() {
        return resolve_binary(name);
    }
    
    // Fallback mappings
    let fallback = match name.to_lowercase().as_str() {
        "dex" => Some("codex"),
        "claude" => Some("claude"),
        "cursor" => Some("cursor"),
        "copilot" => Some("copilot"),
        _ => None,
    };
    
    if let Some(fb) = fallback {
        if let Ok(path) = which::which(fb) {
            return Some(path);
        }
    }
    
    None
}

/// Run agent with thegent integration
fn run_agent(name: &str, args: &[String]) -> ExitCode {
    // Resolve the agent binary
    let agent_path = resolve_agent(name);
    
    match agent_path {
        Some(path) => {
            let mut cmd = StdCommand::new(&path);
            cmd.args(args);
            
            // Preserve thegent environment
            if let Ok(project_dir) = env::var("PROJECT_DIR") {
                cmd.env("PROJECT_DIR", &project_dir);
            }
            if let Ok(session_id) = env::var("SESSION_ID") {
                cmd.env("SESSION_ID", &session_id);
            }
            
            // Execute and propagate exit code
            let status = cmd.status().unwrap_or_else(|e| {
                eprintln!("thegent-shims: failed to execute {}: {}", name, e);
                std::process::exit(1);
            });
            
            let code = status.code().unwrap_or(1);
            ExitCode::from(code as u8)
        }
        None => {
            eprintln!("thegent-shims: agent '{}' not found in PATH", name);
            eprintln!("thegent-shims: tried: {} (with fallbacks)", name);
            ExitCode::from(127)
        }
    }
}

fn main() -> ExitCode {
    // Initialize logger for debugging
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("warn"))
        .init();
    
    let cli = Cli::parse();
    
    match cli.command {
        ShimCommand::Git { args } => {
            run_git(&args)
        }
        ShimCommand::Grep { args } => {
            run_grep(&args)
        }
        ShimCommand::Find { args } => {
            run_find(&args)
        }
        ShimCommand::Agent { name, args } => {
            run_agent(&name, &args)
        }
    }
}
