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
#[command(args_conflicts_with_subcommands = true)]
struct Cli {
    #[command(subcommand)]
    command: ShimCommand,
}

#[derive(Subcommand)]
enum ShimCommand {
    /// Git wrapper with thegent integration
    Git {
        /// Arguments to pass to git
        #[arg(allow_hyphen_values = true, trailing_var_arg = true)]
        args: Vec<String>,
    },
    /// Fast grep with thegent context
    Grep {
        /// Arguments to pass to grep/rg
        #[arg(allow_hyphen_values = true, trailing_var_arg = true)]
        args: Vec<String>,
    },
    /// Find with thegent awareness
    Find {
        /// Arguments to pass to find/fd
        #[arg(allow_hyphen_values = true, trailing_var_arg = true)]
        args: Vec<String>,
    },
    /// agent: Agent invocation shim
    Agent {
        /// Agent name (codex, copilot, dex, claude, cursor)
        name: String,
        /// Arguments to pass to the agent
        #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
        args: Vec<String>,
    },
    /// Jq accelerator
    Jq {
        /// Arguments to pass to jq/jaq
        #[arg(allow_hyphen_values = true, trailing_var_arg = true)]
        args: Vec<String>,
    },
    /// Pgrep accelerator
    Pgrep {
        /// Arguments to pass to pgrep
        #[arg(allow_hyphen_values = true, trailing_var_arg = true)]
        args: Vec<String>,
    },
    /// Wc accelerator
    Wc {
        /// Arguments to pass to wc
        #[arg(allow_hyphen_values = true, trailing_var_arg = true)]
        args: Vec<String>,
    },
    /// Date accelerator
    Date {
        /// Arguments to pass to date
        #[arg(allow_hyphen_values = true, trailing_var_arg = true)]
        args: Vec<String>,
    },
    /// Tr accelerator
    Tr {
        /// Arguments to pass to tr
        #[arg(allow_hyphen_values = true, trailing_var_arg = true)]
        args: Vec<String>,
    },
}

const SAFE_PATH: &str = "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/usr/local/bin";

/// Create a Command with a safe PATH to avoid recursion through our own shims
fn safe_command(name: &str) -> StdCommand {
    let mut cmd = StdCommand::new(name);
    cmd.env("PATH", SAFE_PATH);
    cmd
}

/// Resolve the real binary path, avoiding shims in ~/.local/bin
fn resolve_binary(name: &str) -> Option<PathBuf> {
    // We use which_in to specify the path explicitly
    which::which_in(name, Some(SAFE_PATH), env::current_dir().ok().unwrap_or_else(|| PathBuf::from("."))).ok()
}

/// Find the first available tool from a list of candidates
fn first_available(candidates: &[&str]) -> Option<PathBuf> {
    for candidate in candidates {
        if let Some(path) = which::which_in(candidate, Some(SAFE_PATH), env::current_dir().ok().unwrap_or_else(|| PathBuf::from("."))).ok() {
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
            let mut cmd = safe_command(path.to_str().unwrap_or("git"));
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
                // translate -E (extended regex) to nothing as rg is always extended
                // and -E in rg means --encoding which causes errors.
                args.iter()
                    .filter(|&arg| arg != "-E")
                    .cloned()
                    .collect()
            } else {
                // Add -n for line numbers if not present (grep compatibility)
                let mut new_args = vec!["-n".to_string()];
                new_args.extend(args.iter().cloned());
                new_args
            };
            
            let mut cmd = safe_command(path.to_str().unwrap_or(cmd_name));
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
                let fd_args = args.to_vec();
                
                // fd defaults to hidden=false, follow=false
                // Common conversions: -name -> (positional), -type f -> -t f
                let mut final_args: Vec<String> = Vec::new();
                let mut i = 0;
                while i < fd_args.len() {
                    let arg = &fd_args[i];
                    if arg == "-name" && i + 1 < fd_args.len() {
                        final_args.push(fd_args[i+1].clone());
                        i += 2;
                    } else if arg == "-type" && i + 1 < fd_args.len() {
                        final_args.push("-t".to_string());
                        final_args.push(fd_args[i+1].clone());
                        i += 2;
                    } else if arg == "-maxdepth" && i + 1 < fd_args.len() {
                        final_args.push("--max-depth".to_string());
                        final_args.push(fd_args[i+1].clone());
                        i += 2;
                    } else {
                        final_args.push(arg.clone());
                        i += 1;
                    }
                }
                
                let mut cmd = safe_command(path.to_str().unwrap_or(cmd_name));
                cmd.args(&final_args);
                
                let status = cmd.status().unwrap_or_else(|e| {
                    eprintln!("thegent-shims: failed to execute fd: {}", e);
                    std::process::exit(1);
                });
                
                let code = status.code().unwrap_or(1);
                ExitCode::from(code as u8)
            } else {
                // Regular find - pass through
                let mut cmd = safe_command(path.to_str().unwrap_or(cmd_name));
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
            let mut cmd = safe_command(path.to_str().unwrap_or(name));
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

/// Run jq with acceleration - prefers jaq
fn run_jq(args: &[String]) -> ExitCode {
    let jq_path = first_available(&["jaq", "jq", "gojq"]);
    match jq_path {
        Some(path) => {
            let mut cmd = safe_command(path.to_str().unwrap_or("jq"));
            cmd.args(args);
            let status = cmd.status().unwrap_or_else(|e| {
                eprintln!("thegent-shims: failed to execute jq: {}", e);
                std::process::exit(1);
            });
            let code = status.code().unwrap_or(1);
            ExitCode::from(code as u8)
        }
        None => {
            eprintln!("thegent-shims: no jq tool found");
            ExitCode::from(127)
        }
    }
}

/// Run pgrep with acceleration
fn run_pgrep(args: &[String]) -> ExitCode {
    let pgrep_path = first_available(&["procs", "pgrep"]);
    match pgrep_path {
        Some(path) => {
            let cmd_name = path.file_name().and_then(|n| n.to_str()).unwrap_or("pgrep");
            let mut cmd = safe_command(path.to_str().unwrap_or(cmd_name));
            cmd.args(args);
            let status = cmd.status().unwrap_or_else(|e| {
                eprintln!("thegent-shims: failed to execute pgrep: {}", e);
                std::process::exit(1);
            });
            let code = status.code().unwrap_or(1);
            ExitCode::from(code as u8)
        }
        None => {
            eprintln!("thegent-shims: pgrep not found");
            ExitCode::from(127)
        }
    }
}

/// Run wc with acceleration - fast path for -l
fn run_wc(args: &[String]) -> ExitCode {
    if args.len() == 1 && args[0] == "-l" {
        // Fast path for line count: read from stdin and count \n
        use std::io::{BufRead, BufReader};
        let stdin = std::io::stdin();
        let reader = BufReader::new(stdin.lock());
        let count = reader.lines().count();
        println!("{}", count);
        return ExitCode::from(0);
    }

    let wc_path = resolve_binary("wc");
    match wc_path {
        Some(path) => {
            let mut cmd = safe_command(path.to_str().unwrap_or("wc"));
            cmd.args(args);
            let status = cmd.status().unwrap_or_else(|e| {
                eprintln!("thegent-shims: failed to execute wc: {}", e);
                std::process::exit(1);
            });
            let code = status.code().unwrap_or(1);
            ExitCode::from(code as u8)
        }
        None => {
            eprintln!("thegent-shims: wc not found");
            ExitCode::from(127)
        }
    }
}

/// Run date with acceleration - fast path for %s
fn run_date(args: &[String]) -> ExitCode {
    if args.len() == 1 && args[0] == "+%s" {
        use std::time::{SystemTime, UNIX_EPOCH};
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        println!("{}", now);
        return ExitCode::from(0);
    }

    let date_path = resolve_binary("date");
    match date_path {
        Some(path) => {
            let mut cmd = safe_command(path.to_str().unwrap_or("date"));
            cmd.args(args);
            let status = cmd.status().unwrap_or_else(|e| {
                eprintln!("thegent-shims: failed to execute date: {}", e);
                std::process::exit(1);
            });
            let code = status.code().unwrap_or(1);
            ExitCode::from(code as u8)
        }
        None => {
            eprintln!("thegent-shims: date not found");
            ExitCode::from(127)
        }
    }
}

/// Run tr with acceleration - fast path for space/newline removal
fn run_tr(args: &[String]) -> ExitCode {
    if args.len() == 2 && args[0] == "-d" && (args[1] == " " || args[1] == "' '" || args[1] == "\n" || args[1] == "'\n'") {
        use std::io::{Read, Write};
        let to_remove = args[1].trim_matches('\'').as_bytes()[0];
        let mut input = Vec::new();
        let _ = std::io::stdin().read_to_end(&mut input);
        let output: Vec<u8> = input.into_iter().filter(|&b| b != to_remove).collect();
        let _ = std::io::stdout().write_all(&output);
        return ExitCode::from(0);
    }

    let tr_path = resolve_binary("tr");
    match tr_path {
        Some(path) => {
            let mut cmd = safe_command(path.to_str().unwrap_or("tr"));
            cmd.args(args);
            let status = cmd.status().unwrap_or_else(|e| {
                eprintln!("thegent-shims: failed to execute tr: {}", e);
                std::process::exit(1);
            });
            let code = status.code().unwrap_or(1);
            ExitCode::from(code as u8)
        }
        None => {
            eprintln!("thegent-shims: tr not found");
            ExitCode::from(127)
        }
    }
}

fn main() -> ExitCode {
    // Initialize logger for debugging
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("warn"))
        .init();
    
    // Phase 2: Support symlink dispatching (e.g. called as 'thegent-git')
    let args: Vec<String> = env::args().collect();
    let program_path = PathBuf::from(&args[0]);
    let program_name = program_path.file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("");

    if program_name == "thegent-git" {
        return run_git(&args[1..].to_vec());
    } else if program_name == "thegent-grep" {
        return run_grep(&args[1..].to_vec());
    } else if program_name == "thegent-find" {
        return run_find(&args[1..].to_vec());
    } else if program_name == "thegent-jq" {
        return run_jq(&args[1..].to_vec());
    } else if program_name == "thegent-pgrep" {
        return run_pgrep(&args[1..].to_vec());
    } else if program_name == "thegent-wc" {
        return run_wc(&args[1..].to_vec());
    } else if program_name == "thegent-date" {
        return run_date(&args[1..].to_vec());
    } else if program_name == "thegent-tr" {
        return run_tr(&args[1..].to_vec());
    } else if program_name.starts_with("thegent-") && program_name != "thegent-shims" && program_name != "thegent-agent" {
        let agent = program_name.strip_prefix("thegent-").unwrap();
        if matches!(agent, "codex" | "copilot" | "dex" | "claude" | "cursor" | "clode" | "roid") {
            return run_agent(agent, &args[1..].to_vec());
        }
    } else if program_name == "thegent-agent" {
        if args.len() > 1 {
            let agent_name = &args[1];
            return run_agent(agent_name, &args[2..].to_vec());
        }
    }

    // Try to detect if we're calling via thegent-shims <subcommand>
    // If so, we manually handle the dispatch to bypass clap's hyphen issues
    if program_name == "thegent-shims" && args.len() > 1 {
        let cmd = &args[1];
        let cmd_args = args[2..].to_vec();
        match cmd.as_str() {
            "git" => return run_git(&cmd_args),
            "grep" => return run_grep(&cmd_args),
            "find" => return run_find(&cmd_args),
            "jq" => return run_jq(&cmd_args),
            "pgrep" => return run_pgrep(&cmd_args),
            "wc" => return run_wc(&cmd_args),
            "date" => return run_date(&cmd_args),
            "tr" => return run_tr(&cmd_args),
            "--version" | "-V" => {
                println!("thegent-shims {}", env!("CARGO_PKG_VERSION"));
                return ExitCode::SUCCESS;
            }
            _ => {
                // If it's not a known subcommand and starts with --, it might be a global flag
                if cmd.starts_with("--") || cmd.starts_with("-") {
                    // Let clap handle it
                } else {
                    // Unknown subcommand
                }
            }
        }
    }

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
        ShimCommand::Jq { args } => {
            run_jq(&args)
        }
        ShimCommand::Pgrep { args } => {
            run_pgrep(&args)
        }
        ShimCommand::Wc { args } => {
            run_wc(&args)
        }
        ShimCommand::Date { args } => {
            run_date(&args)
        }
        ShimCommand::Tr { args } => {
            run_tr(&args)
        }
    }
}
