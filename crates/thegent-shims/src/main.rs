//! thegent-shims: Efficient shell command shims for thegent
//!
//! Provides fast Rust replacements for shell commands:
//! - git: Git wrapper with thegent integration
//! - grep: Fast grep with thegent context
//! - find: Find with thegent awareness
//! - agent: Agent invocation shim

use clap::{Parser, Subcommand};
use std::env;
use std::os::unix::process::ExitStatusExt;
use std::path::{Path, PathBuf};
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
        /// Agent name (codex, dex, claude, cursor, clode, roid, droid, fanta, anen, antigma, cline, roocode)
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
    /// Flock accelerator
    Flock {
        /// Arguments to pass to flock
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
    which::which_in(
        name,
        Some(SAFE_PATH),
        env::current_dir().unwrap_or_else(|_| PathBuf::from(".")),
    )
    .ok()
}

/// Find the first available tool from a list of candidates
fn first_available(candidates: &[&str]) -> Option<PathBuf> {
    for candidate in candidates {
        if let Ok(path) = which::which_in(
            candidate,
            Some(SAFE_PATH),
            env::current_dir().unwrap_or_else(|_| PathBuf::from(".")),
        ) {
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
            let cmd_name = path.file_name().and_then(|n| n.to_str()).unwrap_or("grep");

            // For rg, pass args directly; for grep, may need adjustment
            let final_args: Vec<String> = if cmd_name == "rg" {
                // translate -E (extended regex) to nothing as rg is always extended
                // and -E in rg means --encoding which causes errors.
                args.iter().filter(|&arg| arg != "-E").cloned().collect()
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
            let cmd_name = path.file_name().and_then(|n| n.to_str()).unwrap_or("find");

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
                        final_args.push(fd_args[i + 1].clone());
                        i += 2;
                    } else if arg == "-type" && i + 1 < fd_args.len() {
                        final_args.push("-t".to_string());
                        final_args.push(fd_args[i + 1].clone());
                        i += 2;
                    } else if arg == "-maxdepth" && i + 1 < fd_args.len() {
                        final_args.push("--max-depth".to_string());
                        final_args.push(fd_args[i + 1].clone());
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

/// Guarded git checkout command:
/// - Block when not in a git worktree: delegate directly
/// - Block when working tree is dirty
/// - Delegate to git checkout when clean
#[allow(dead_code)]
fn run_git_checkout(args: &[String]) -> ExitCode {
    let git_path = match resolve_binary("git") {
        Some(path) => path,
        None => {
            eprintln!("thegent-git-checkout: git not found in PATH");
            return ExitCode::from(127);
        }
    };

    // If this is not a git checkout, pass through to raw git checkout semantics.
    let is_git_worktree = match StdCommand::new(&git_path)
        .arg("rev-parse")
        .arg("--is-inside-work-tree")
        .output()
    {
        Ok(output) => {
            output.status.success() && String::from_utf8_lossy(&output.stdout).trim() == "true"
        }
        Err(e) => {
            eprintln!("thegent-git-checkout: failed to check git worktree: {}", e);
            return ExitCode::from(1);
        }
    };

    if is_git_worktree {
        let status = match StdCommand::new(&git_path)
            .arg("status")
            .arg("--porcelain")
            .output()
        {
            Ok(output) => output,
            Err(e) => {
                eprintln!("thegent-git-checkout: failed to read git status; refusing checkout.");
                eprintln!("thegent-git-checkout: error: {}", e);
                return ExitCode::from(1);
            }
        };

        if !status.status.success() {
            return ExitCode::from(status.status.code().unwrap_or(1) as u8);
        }

        if !status.stdout.is_empty() {
            let status_text = String::from_utf8_lossy(&status.stdout);
            let mut has_uncommitted = false;
            for line in status_text.lines() {
                if !line.trim().is_empty() {
                    has_uncommitted = true;
                    break;
                }
            }

            if has_uncommitted {
                eprintln!("thegent-git-checkout: blocked checkout on dirty working tree.");
                eprintln!("Please commit/stage/reset/discard changes before retrying.");
                eprintln!("Uncommitted changes:");
                eprintln!("{}", status_text.trim_end());
                return ExitCode::from(1);
            }
        }
    }

    let mut git_args = Vec::with_capacity(args.len() + 1);
    git_args.push("checkout".to_string());
    git_args.extend_from_slice(args);

    thegent_shims::GitShim::new().exec(&git_args)
}

/// Resolve agent binary - handles fallback logic (dex -> codex, etc.)
fn is_self_or_shim_wrapper(path: &Path) -> bool {
    if let (Ok(candidate), Ok(current)) = (path.canonicalize(), env::current_exe()) {
        if let Ok(current_canon) = current.canonicalize() {
            if candidate == current_canon {
                return true;
            }
        }
    }

    if let Ok(content) = std::fs::read_to_string(path) {
        return content.contains("thegent-shims");
    }

    false
}

fn resolve_nonshim_binary(name: &str) -> Option<PathBuf> {
    if let Ok(path) = which::which_in(
        name,
        Some(SAFE_PATH),
        env::current_dir().unwrap_or_else(|_| PathBuf::from(".")),
    ) {
        if !is_self_or_shim_wrapper(&path) {
            return Some(path);
        }
    }
    None
}

fn canonical_harness_name(name: &str) -> &str {
    match name {
        "anen" | "antigma" => "fanta",
        _ => name,
    }
}

fn resolve_agent(name: &str) -> Option<PathBuf> {
    // Prefer canonical target binaries for alias wrappers before resolving the alias name itself.
    let lowered = name.to_lowercase();
    let candidates: &[&str] = match lowered.as_str() {
        "dex" => &["codex"],
        "clode" => &["claude"],
        "roid" => &["droid"],
        "droid" => &["droid"],
        "fanta" | "anen" | "antigma" => &["ante"],
        "cline" => &["cline", "cursor-agent", "cursor"],
        "roocode" => &["roocode", "roo", "cursor-agent", "cursor"],
        "cursor" => &["cursor-agent", "cursor"],
        "claude" => &["claude"],
        "codex" => &["codex"],
        _ => &[name],
    };

    for candidate in candidates {
        if let Some(path) = resolve_nonshim_binary(candidate) {
            return Some(path);
        }
    }

    // Home-local fallback for ante.
    if matches!(lowered.as_str(), "fanta" | "anen" | "antigma") {
        if let Ok(home) = env::var("HOME") {
            let candidate = PathBuf::from(home).join(".ante").join("bin").join("ante");
            if candidate.is_file() {
                return Some(candidate);
            }
        }
    }

    None
}

fn inject_harness_defaults(name: &str, args: &[String]) -> Vec<String> {
    let mut out = args.to_vec();
    match name {
        "dex" => {
            if !out
                .iter()
                .any(|a| a == "--dangerously-bypass-approvals-and-sandbox")
            {
                out.insert(0, "--dangerously-bypass-approvals-and-sandbox".to_string());
            }
            if !out.iter().any(|a| a == "--search") {
                if out.iter().any(|a| a == "exec") {
                    let exec_idx = out.iter().position(|a| a == "exec").unwrap_or(1);
                    out.insert(exec_idx, "--search".to_string());
                } else {
                    out.push("--search".to_string());
                }
            }
        }
        "clode" => {
            if !out.iter().any(|a| {
                a == "--dangerously-skip-permissions" || a == "--allow-dangerously-skip-permissions"
            }) {
                out.insert(0, "--dangerously-skip-permissions".to_string());
            }
        }
        "roid" | "droid" => {
            if out.first().map(String::as_str) == Some("exec") {
                let has_skip = out.iter().any(|a| a == "--skip-permissions-unsafe");
                let has_auto = out.iter().any(|a| a == "--auto");
                if !has_skip && !has_auto {
                    out.insert(1, "--skip-permissions-unsafe".to_string());
                }
            }
        }
        _ => {}
    }
    out
}

fn is_native_command_passthrough(name: &str, token: &str) -> bool {
    match name {
        "dex" => matches!(
            token,
            "exec"
                | "review"
                | "login"
                | "logout"
                | "mcp"
                | "mcp-server"
                | "app-server"
                | "app"
                | "completion"
                | "sandbox"
                | "debug"
                | "apply"
                | "resume"
                | "fork"
                | "cloud"
                | "features"
                | "help"
        ),
        "roid" | "droid" => {
            matches!(
                token,
                "exec" | "resume" | "continue" | "help" | "login" | "logout" | "version"
            )
        }
        _ => true,
    }
}

fn normalize_harness_command_labels(name: &str, args: &[String]) -> Vec<String> {
    if args.is_empty() {
        return args.to_vec();
    }

    let name = canonical_harness_name(name);
    let first = args[0].as_str();
    let rest = &args[1..];

    match (name, first) {
        ("dex", "continue") => {
            if rest.is_empty() {
                vec!["resume".to_string(), "--last".to_string()]
            } else {
                let mut out = vec!["resume".to_string()];
                out.extend(rest.iter().cloned());
                out
            }
        }
        ("clode", "exec") => rest.to_vec(),
        ("clode", "continue") => {
            let mut out = vec!["--continue".to_string()];
            out.extend(rest.iter().cloned());
            out
        }
        ("clode", "resume") => {
            if rest.is_empty() {
                vec!["--continue".to_string()]
            } else {
                let mut out = vec!["--resume".to_string()];
                out.extend(rest.iter().cloned());
                out
            }
        }
        ("fanta", "exec") => {
            if rest.is_empty() {
                return rest.to_vec();
            }
            if rest.iter().any(|a| a == "-h" || a == "--help") {
                return vec!["--help".to_string()];
            }
            if rest.iter().any(|a| a == "-p" || a == "--prompt") {
                return rest.to_vec();
            }
            vec!["-p".to_string(), rest.join(" ")]
        }
        ("roid", "continue") | ("droid", "continue") => {
            let mut out = vec!["resume".to_string()];
            out.extend(rest.iter().cloned());
            out
        }
        ("dex", token) | ("roid", token) | ("droid", token)
            if !token.starts_with('-') && !is_native_command_passthrough(name, token) =>
        {
            let mut out = vec!["exec".to_string()];
            out.extend(args.iter().cloned());
            out
        }
        _ => args.to_vec(),
    }
}

fn normalize_harness_exec_legacy_args(name: &str, args: &[String]) -> Vec<String> {
    if !matches!(name, "dex" | "roid" | "droid") || args.len() < 4 {
        return args.to_vec();
    }
    if args[0] != "exec" || args[1].starts_with('-') {
        return args.to_vec();
    }
    if args[2] != "-p" && args[2] != "--prompt" {
        return args.to_vec();
    }

    let normalized_model = if name == "dex" && args[1] == "max" {
        "minimax-m2.5".to_string()
    } else {
        args[1].clone()
    };

    let mut out = vec!["exec".to_string(), "-m".to_string(), normalized_model];
    out.extend(args[3..].iter().cloned());
    out
}

fn split_native_flag(args: &[String]) -> (bool, Vec<String>) {
    let native_mode = args.iter().any(|a| a == "--native");
    let filtered = args
        .iter()
        .filter(|a| a.as_str() != "--native")
        .cloned()
        .collect();
    (native_mode, filtered)
}

fn split_force_flag(args: &[String]) -> (bool, Vec<String>) {
    let force_mode = args
        .iter()
        .any(|a| a == "--force" || a == "-f" || a.starts_with("--force="));
    let filtered = args
        .iter()
        .filter(|a| a.as_str() != "--force" && a.as_str() != "-f" && !a.starts_with("--force="))
        .cloned()
        .collect();
    (force_mode, filtered)
}

fn inject_native_force_alias(name: &str, args: &[String], force_mode: bool) -> Vec<String> {
    if name != "dex" || !force_mode {
        return args.to_vec();
    }

    if args.iter().any(|a| a == "--force-yolo") {
        return args.to_vec();
    }

    let mut out = args.to_vec();
    out.insert(0, "--force-yolo".to_string());
    out
}

fn dex_proxy_env_defaults() -> (Option<String>, Option<String>) {
    let base_url = env::var("OPENAI_BASE_URL").ok();
    let api_key = env::var("OPENAI_API_KEY").ok();

    let should_reset_base = base_url
        .as_deref()
        .map(str::trim)
        .map(|value| value.is_empty() || value.contains(":3847") || value.ends_with("/mcp"))
        .unwrap_or(true);

    let default_base = if should_reset_base {
        Some("http://127.0.0.1:8317/v1".to_string())
    } else {
        None
    };

    let default_key = if api_key.as_deref().map(str::is_empty).unwrap_or(true) {
        Some("sk-test".to_string())
    } else {
        None
    };

    (default_base, default_key)
}

fn should_inject_proxy_env_defaults(name: &str) -> bool {
    matches!(
        name,
        "dex" | "clode" | "claude" | "codex" | "roid" | "droid" | "fanta" | "anen" | "antigma"
    )
}

fn inject_force_alias(name: &str, args: &[String], force_mode: bool) -> Vec<String> {
    if !force_mode {
        return args.to_vec();
    }

    let mut out = args.to_vec();
    match name {
        "dex" => {
            if !out
                .iter()
                .any(|a| a == "--dangerously-bypass-approvals-and-sandbox")
            {
                out.insert(0, "--dangerously-bypass-approvals-and-sandbox".to_string());
            }
        }
        "clode" => {
            if !out.iter().any(|a| {
                a == "--dangerously-skip-permissions" || a == "--allow-dangerously-skip-permissions"
            }) {
                out.insert(0, "--dangerously-skip-permissions".to_string());
            }
        }
        "roid" | "droid" => {
            let has_skip = out.iter().any(|a| a == "--skip-permissions-unsafe");
            let has_auto = out.iter().any(|a| a == "--auto");
            if !has_skip && !has_auto {
                if out.first().map(String::as_str) == Some("exec") {
                    out.insert(1, "--skip-permissions-unsafe".to_string());
                } else {
                    out.insert(0, "--skip-permissions-unsafe".to_string());
                }
            }
        }
        _ => {}
    }
    out
}

fn dedupe_exact_flags(args: &[String], flags: &[&str]) -> Vec<String> {
    let mut out: Vec<String> = Vec::with_capacity(args.len());
    let mut seen: std::collections::HashSet<&str> = std::collections::HashSet::new();
    for arg in args {
        let as_str = arg.as_str();
        if flags.contains(&as_str) {
            if seen.contains(as_str) {
                continue;
            }
            seen.insert(as_str);
        }
        out.push(arg.clone());
    }
    out
}

/// Run agent with thegent integration
fn run_agent(name: &str, args: &[String]) -> ExitCode {
    let lowered_name = name.to_lowercase();
    let canonical_name = canonical_harness_name(lowered_name.as_str());
    let (native_mode, filtered_native) = split_native_flag(args);
    let (force_mode, filtered) = split_force_flag(&filtered_native);
    let filtered = normalize_harness_command_labels(canonical_name, &filtered);
    let filtered = normalize_harness_exec_legacy_args(canonical_name, &filtered);
    let filtered = inject_force_alias(canonical_name, &filtered, force_mode);
    if canonical_name == "fanta"
        && filtered
            .first()
            .map(String::as_str)
            .is_some_and(|cmd| cmd == "continue" || cmd == "resume")
    {
        eprintln!("thegent-shims: fanta/ante does not expose resume/continue in native CLI.");
        return ExitCode::from(2);
    }

    // Resolve the agent binary
    let agent_path = resolve_agent(canonical_name);

    match agent_path {
        Some(path) => {
            let mut cmd = safe_command(path.to_str().unwrap_or(name));
            let passthrough_args: Vec<String> = if native_mode {
                inject_native_force_alias(canonical_name, &filtered, force_mode)
            } else if matches!(canonical_name, "dex" | "clode" | "roid" | "droid" | "fanta") {
                inject_harness_defaults(canonical_name, &filtered)
            } else {
                filtered
            };
            let passthrough_args = dedupe_exact_flags(
                &passthrough_args,
                &[
                    "--dangerously-bypass-approvals-and-sandbox",
                    "--dangerously-skip-permissions",
                    "--allow-dangerously-skip-permissions",
                    "--skip-permissions-unsafe",
                ],
            );
            cmd.args(&passthrough_args);

            // Preserve thegent environment
            if let Ok(project_dir) = env::var("PROJECT_DIR") {
                cmd.env("PROJECT_DIR", &project_dir);
            }
            if let Ok(session_id) = env::var("SESSION_ID") {
                cmd.env("SESSION_ID", &session_id);
            }
            // Scrub problematic malloc logging env vars from spawned agent processes.
            // These vars can cause noisy stderr warnings on macOS in non-debuggable shells.
            cmd.env_remove("MallocStackLogging");
            cmd.env_remove("MallocStackLoggingNoCompact");
            cmd.env_remove("MallocStackLoggingDirectory");
            if should_inject_proxy_env_defaults(canonical_name) {
                let (default_base, default_key) = dex_proxy_env_defaults();
                if let Some(base) = default_base {
                    cmd.env("OPENAI_BASE_URL", base);
                }
                if let Some(key) = default_key {
                    cmd.env("OPENAI_API_KEY", key);
                }
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
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
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
    if args.len() == 2
        && args[0] == "-d"
        && (args[1] == " " || args[1] == "' '" || args[1] == "\n" || args[1] == "'\n'")
    {
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

/// Run flock with acceleration
fn run_flock(args: &[String]) -> ExitCode {
    // Basic implementation of flock -n <fd> <command>
    if args.len() >= 2 {
        // We don't actually support FD-based locking easily in a portable way here
        // but we can support file-based locking.
        // For now, if it's 'flock -n <fd>', we just skip or try to resolve.
        // If it's a real command, we just execute it.
        // This is a stub to prevent 'command not found' errors.

        let mut cmd_idx = 0;
        while cmd_idx < args.len()
            && (args[cmd_idx].starts_with("-") || args[cmd_idx].chars().all(|c| c.is_ascii_digit()))
        {
            cmd_idx += 1;
        }

        if cmd_idx < args.len() {
            let mut cmd = StdCommand::new(&args[cmd_idx]);
            cmd.args(&args[cmd_idx + 1..]);
            let status = cmd
                .status()
                .unwrap_or_else(|_| std::process::ExitStatus::from_raw(0));
            return ExitCode::from(status.code().unwrap_or(0) as u8);
        }
    }
    ExitCode::SUCCESS
}

fn main() -> ExitCode {
    // Initialize logger for debugging
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("warn")).init();

    // Phase 2: Support symlink dispatching (e.g. called as 'thegent-git')
    let args: Vec<String> = env::args().collect();
    let program_path = PathBuf::from(&args[0]);
    let program_name = program_path
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("");

    if program_name == "dex"
        || program_name == "clode"
        || program_name == "roid"
        || program_name == "droid"
        || program_name == "fanta"
        || program_name == "anen"
        || program_name == "antigma"
        || program_name == "cline"
        || program_name == "roocode"
    {
        return run_agent(program_name, &args[1..]);
    } else if program_name == "thegent-git" {
        return run_git(&args[1..]);
    } else if program_name == "thegent-grep" {
        return run_grep(&args[1..]);
    } else if program_name == "thegent-find" {
        return run_find(&args[1..]);
    } else if program_name == "thegent-jq" {
        return run_jq(&args[1..]);
    } else if program_name == "thegent-pgrep" {
        return run_pgrep(&args[1..]);
    } else if program_name == "thegent-wc" {
        return run_wc(&args[1..]);
    } else if program_name == "thegent-date" {
        return run_date(&args[1..]);
    } else if program_name == "thegent-tr" {
        return run_tr(&args[1..]);
    } else if program_name.starts_with("thegent-")
        && program_name != "thegent-shims"
        && program_name != "thegent-agent"
    {
        let agent = program_name.strip_prefix("thegent-").unwrap();
        if matches!(
            agent,
            "codex"
                | "dex"
                | "claude"
                | "cursor"
                | "clode"
                | "roid"
                | "droid"
                | "fanta"
                | "anen"
                | "antigma"
                | "cline"
                | "roocode"
        ) {
            return run_agent(agent, &args[1..]);
        }
    } else if program_name == "thegent-agent" && args.len() > 1 {
        let agent_name = &args[1];
        return run_agent(agent_name, &args[2..]);
    }

    // Try to detect if we're calling via thegent-shims <subcommand>
    // If so, we manually handle the dispatch to bypass clap's hyphen issues
    if program_name == "thegent-shims" && args.len() > 1 {
        let cmd = &args[1];
        let cmd_args = &args[2..];
        match cmd.as_str() {
            "agent" => {
                if args.len() > 2 {
                    let agent_name = &args[2];
                    return run_agent(agent_name, &args[3..]);
                }
                eprintln!("thegent-shims: missing agent name");
                return ExitCode::from(2);
            }
            "git" => return run_git(cmd_args),
            "grep" => return run_grep(cmd_args),
            "find" => return run_find(cmd_args),
            "jq" => return run_jq(cmd_args),
            "pgrep" => return run_pgrep(cmd_args),
            "wc" => return run_wc(cmd_args),
            "date" => return run_date(cmd_args),
            "tr" => return run_tr(cmd_args),
            "flock" => return run_flock(cmd_args),
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
        ShimCommand::Git { args } => run_git(&args),
        ShimCommand::Grep { args } => run_grep(&args),
        ShimCommand::Find { args } => run_find(&args),
        ShimCommand::Agent { name, args } => run_agent(&name, &args),
        ShimCommand::Jq { args } => run_jq(&args),
        ShimCommand::Pgrep { args } => run_pgrep(&args),
        ShimCommand::Wc { args } => run_wc(&args),
        ShimCommand::Date { args } => run_date(&args),
        ShimCommand::Tr { args } => run_tr(&args),
        ShimCommand::Flock { args } => run_flock(&args),
    }
}

#[cfg(test)]
mod tests {
    use std::env;
    use std::sync::{Mutex, OnceLock};

    use super::{
        dedupe_exact_flags, dex_proxy_env_defaults, inject_force_alias, inject_harness_defaults,
        inject_native_force_alias, normalize_harness_command_labels,
        normalize_harness_exec_legacy_args, should_inject_proxy_env_defaults, split_force_flag,
        split_native_flag,
    };

    fn v(args: &[&str]) -> Vec<String> {
        args.iter().map(|s| s.to_string()).collect()
    }

    fn env_lock() -> &'static Mutex<()> {
        static LOCK: OnceLock<Mutex<()>> = OnceLock::new();
        LOCK.get_or_init(|| Mutex::new(()))
    }

    #[test]
    fn split_native_flag_filters_only_native() {
        let (native, filtered) = split_native_flag(&v(&["--native", "resume", "--last"]));
        assert!(native);
        assert_eq!(filtered, v(&["resume", "--last"]));
    }

    #[test]
    fn split_native_flag_leaves_other_args_when_not_native() {
        let (native, filtered) = split_native_flag(&v(&["resume", "--last"]));
        assert!(!native);
        assert_eq!(filtered, v(&["resume", "--last"]));
    }

    #[test]
    fn split_force_flag_filters_short_and_long_flags() {
        let (force, filtered) = split_force_flag(&v(&["-f", "resume", "--force", "--last"]));
        assert!(force);
        assert_eq!(filtered, v(&["resume", "--last"]));
    }

    #[test]
    fn split_force_flag_filters_equivalent_force_forms() {
        let (force, filtered) = split_force_flag(&v(&["--force=true", "resume"]));
        assert!(force);
        assert_eq!(filtered, v(&["resume"]));
    }

    #[test]
    fn split_force_flag_leaves_other_args_when_not_force() {
        let (force, filtered) = split_force_flag(&v(&["resume", "--last"]));
        assert!(!force);
        assert_eq!(filtered, v(&["resume", "--last"]));
    }

    #[test]
    fn inject_force_alias_for_dex_adds_bypass_flag() {
        let out = inject_force_alias("dex", &v(&["resume"]), true);
        assert_eq!(out[0], "--dangerously-bypass-approvals-and-sandbox");
        assert!(out.contains(&"resume".to_string()));
    }

    #[test]
    fn inject_native_force_alias_for_dex_adds_force_yolo() {
        let out = inject_native_force_alias("dex", &v(&["resume"]), true);
        assert_eq!(out[0], "--force-yolo");
        assert!(out.contains(&"resume".to_string()));
    }

    #[test]
    fn inject_native_force_alias_for_dex_leaves_force_yolo() {
        let out = inject_native_force_alias("dex", &v(&["--force-yolo", "resume"]), true);
        assert_eq!(out, v(&["--force-yolo", "resume"]));
    }

    #[test]
    fn inject_force_alias_for_clode_adds_skip_permissions_flag() {
        let out = inject_force_alias("clode", &v(&["resume"]), true);
        assert_eq!(out[0], "--dangerously-skip-permissions");
        assert!(out.contains(&"resume".to_string()));
    }

    #[test]
    fn inject_force_alias_for_roid_exec_adds_skip_permissions_unsafe() {
        let out = inject_force_alias("roid", &v(&["exec", "status"]), true);
        assert_eq!(out[0], "exec");
        assert_eq!(out[1], "--skip-permissions-unsafe");
    }

    #[test]
    fn inject_force_alias_for_fanta_non_exec_is_noop() {
        let out = inject_force_alias("fanta", &v(&["--model", "flash"]), true);
        assert_eq!(out, v(&["--model", "flash"]));
    }

    #[test]
    fn normalize_harness_labels_for_dex_continue_without_args_uses_resume_last() {
        let out = normalize_harness_command_labels("dex", &v(&["continue"]));
        assert_eq!(out, v(&["resume", "--last"]));
    }

    #[test]
    fn normalize_harness_labels_for_dex_continue_with_id_uses_resume_id() {
        let out = normalize_harness_command_labels("dex", &v(&["continue", "abc123"]));
        assert_eq!(out, v(&["resume", "abc123"]));
    }

    #[test]
    fn normalize_harness_labels_for_clode_continue_to_flag() {
        let out = normalize_harness_command_labels("clode", &v(&["continue"]));
        assert_eq!(out, v(&["--continue"]));
    }

    #[test]
    fn normalize_harness_labels_for_clode_resume_to_resume_flag() {
        let out = normalize_harness_command_labels("clode", &v(&["resume", "abc123"]));
        assert_eq!(out, v(&["--resume", "abc123"]));
    }

    #[test]
    fn normalize_harness_labels_for_roid_continue_to_resume() {
        let out = normalize_harness_command_labels("roid", &v(&["continue", "abc123"]));
        assert_eq!(out, v(&["resume", "abc123"]));
    }

    #[test]
    fn normalize_harness_labels_for_clode_exec_strips_exec_marker() {
        let out = normalize_harness_command_labels("clode", &v(&["exec", "--print", "hi"]));
        assert_eq!(out, v(&["--print", "hi"]));
    }

    #[test]
    fn normalize_harness_labels_for_dex_defaults_unknown_label_to_exec() {
        let out = normalize_harness_command_labels("dex", &v(&["max", "-p", "hi"]));
        assert_eq!(out, v(&["exec", "max", "-p", "hi"]));
    }

    #[test]
    fn normalize_harness_labels_for_fanta_defaults_unknown_label_to_exec() {
        let out = normalize_harness_command_labels("fanta", &v(&["max", "-p", "hi"]));
        assert_eq!(out, v(&["max", "-p", "hi"]));
    }

    #[test]
    fn normalize_harness_labels_for_dex_keeps_native_commands_passthrough() {
        let out = normalize_harness_command_labels("dex", &v(&["login"]));
        assert_eq!(out, v(&["login"]));
    }

    #[test]
    fn normalize_harness_exec_legacy_args_for_dex_max_prompt_rewrites_to_model_and_prompt() {
        let out = normalize_harness_exec_legacy_args("dex", &v(&["exec", "max", "-p", "hi"]));
        assert_eq!(out, v(&["exec", "-m", "minimax-m2.5", "hi"]));
    }

    #[test]
    fn normalize_harness_labels_for_fanta_exec_without_prompt_uses_prompt_flag() {
        let out = normalize_harness_command_labels("fanta", &v(&["exec", "hi there"]));
        assert_eq!(out, v(&["-p", "hi there"]));
    }

    #[test]
    fn normalize_harness_labels_for_fanta_exec_with_prompt_flag_strips_exec_marker() {
        let out = normalize_harness_command_labels("fanta", &v(&["exec", "-m", "foo", "-p", "hi"]));
        assert_eq!(out, v(&["-m", "foo", "-p", "hi"]));
    }

    #[test]
    fn normalize_harness_labels_for_fanta_exec_with_help_returns_help() {
        let out = normalize_harness_command_labels("fanta", &v(&["exec", "--help"]));
        assert_eq!(out, v(&["--help"]));
    }

    #[test]
    fn normalize_harness_labels_for_antigma_exec_without_prompt_uses_prompt_flag() {
        let out = normalize_harness_command_labels("antigma", &v(&["exec", "hi there"]));
        assert_eq!(out, v(&["-p", "hi there"]));
    }

    #[test]
    fn inject_defaults_for_dex_includes_search_and_bypass() {
        let out = inject_harness_defaults("dex", &v(&["resume"]));
        assert!(out.contains(&"--search".to_string()));
        assert!(out.contains(&"--dangerously-bypass-approvals-and-sandbox".to_string()));
        assert!(out.contains(&"resume".to_string()));
        assert_eq!(out.last().map(String::as_str), Some("--search"));
    }

    #[test]
    fn inject_defaults_for_dex_is_idempotent_for_existing_flags() {
        let out = inject_harness_defaults(
            "dex",
            &v(&[
                "--search",
                "--dangerously-bypass-approvals-and-sandbox",
                "resume",
            ]),
        );
        let search_count = out.iter().filter(|a| a.as_str() == "--search").count();
        let bypass_count = out
            .iter()
            .filter(|a| a.as_str() == "--dangerously-bypass-approvals-and-sandbox")
            .count();
        assert_eq!(search_count, 1);
        assert_eq!(bypass_count, 1);
    }

    #[test]
    fn dedupe_exact_flags_collapses_duplicate_dangerous_bypass_flag() {
        let out = dedupe_exact_flags(
            &v(&[
                "--dangerously-bypass-approvals-and-sandbox",
                "exec",
                "--dangerously-bypass-approvals-and-sandbox",
                "resume",
            ]),
            &["--dangerously-bypass-approvals-and-sandbox"],
        );
        let bypass_count = out
            .iter()
            .filter(|a| a.as_str() == "--dangerously-bypass-approvals-and-sandbox")
            .count();
        assert_eq!(bypass_count, 1);
        assert!(out.contains(&"exec".to_string()));
        assert!(out.contains(&"resume".to_string()));
    }

    #[test]
    fn inject_defaults_for_dex_places_search_before_exec_subcommand() {
        let out = inject_harness_defaults("dex", &v(&["exec", "-m", "minimax-m2.5", "hi"]));
        let exec_index = out
            .iter()
            .position(|a| a == "exec")
            .expect("exec should be present");
        let search_index = out
            .iter()
            .position(|a| a == "--search")
            .expect("search should be present");
        assert!(search_index < exec_index);
    }

    #[test]
    fn inject_defaults_for_clode_adds_skip_permissions_once() {
        let out = inject_harness_defaults("clode", &v(&["resume"]));
        assert!(out.contains(&"--dangerously-skip-permissions".to_string()));
        let out2 =
            inject_harness_defaults("clode", &v(&["--dangerously-skip-permissions", "resume"]));
        let count = out2
            .iter()
            .filter(|a| a.as_str() == "--dangerously-skip-permissions")
            .count();
        assert_eq!(count, 1);
    }

    #[test]
    fn inject_defaults_for_roid_exec_adds_skip_permissions_unsafe() {
        let out = inject_harness_defaults("roid", &v(&["exec", "status"]));
        assert_eq!(out[0], "exec");
        assert_eq!(out[1], "--skip-permissions-unsafe");
    }

    #[test]
    fn inject_defaults_for_droid_exec_adds_skip_permissions_unsafe() {
        let out = inject_harness_defaults("droid", &v(&["exec", "status"]));
        assert_eq!(out[0], "exec");
        assert_eq!(out[1], "--skip-permissions-unsafe");
    }

    #[test]
    fn inject_defaults_for_fanta_exec_does_not_add_when_auto_present() {
        let out = inject_harness_defaults("fanta", &v(&["exec", "--auto", "status"]));
        assert!(!out.iter().any(|a| a == "--skip-permissions-unsafe"));
    }

    #[test]
    fn dex_proxy_env_defaults_are_populated_when_unset() {
        let _guard = env_lock().lock().expect("env lock poisoned");
        unsafe {
            env::remove_var("OPENAI_BASE_URL");
            env::remove_var("OPENAI_API_KEY");
        }
        let (base, key) = dex_proxy_env_defaults();
        assert_eq!(base.as_deref(), Some("http://127.0.0.1:8317/v1"));
        assert_eq!(key.as_deref(), Some("sk-test"));
    }

    #[test]
    fn dex_proxy_env_defaults_respect_existing_env() {
        let _guard = env_lock().lock().expect("env lock poisoned");
        unsafe {
            env::set_var("OPENAI_BASE_URL", "https://api.openai.com/v1");
            env::set_var("OPENAI_API_KEY", "sk-live");
        }
        let (base, key) = dex_proxy_env_defaults();
        assert!(base.is_none());
        assert!(key.is_none());
        unsafe {
            env::remove_var("OPENAI_BASE_URL");
            env::remove_var("OPENAI_API_KEY");
        }
    }

    #[test]
    fn dex_proxy_env_defaults_overrides_mcp_port_base_url() {
        let _guard = env_lock().lock().expect("env lock poisoned");
        unsafe {
            env::set_var("OPENAI_BASE_URL", "http://127.0.0.1:3847/mcp");
            env::set_var("OPENAI_API_KEY", "sk-live");
        }
        let (base, key) = dex_proxy_env_defaults();
        assert_eq!(base.as_deref(), Some("http://127.0.0.1:8317/v1"));
        assert!(key.is_none());
        unsafe {
            env::remove_var("OPENAI_BASE_URL");
            env::remove_var("OPENAI_API_KEY");
        }
    }

    #[test]
    fn should_inject_proxy_env_defaults_for_supported_harnesses() {
        assert!(should_inject_proxy_env_defaults("dex"));
        assert!(should_inject_proxy_env_defaults("clode"));
        assert!(should_inject_proxy_env_defaults("claude"));
        assert!(should_inject_proxy_env_defaults("codex"));
        assert!(should_inject_proxy_env_defaults("roid"));
        assert!(should_inject_proxy_env_defaults("droid"));
        assert!(should_inject_proxy_env_defaults("fanta"));
        assert!(should_inject_proxy_env_defaults("antigma"));
        assert!(should_inject_proxy_env_defaults("anen"));
        assert!(!should_inject_proxy_env_defaults("copilot"));
        assert!(!should_inject_proxy_env_defaults("opencode"));
        assert!(!should_inject_proxy_env_defaults("cursor"));
    }
}
