//! thegent-discovery binary
//!
//! BKM-08: Consolidates N subprocess spawns (git, ps, tmux, which, npx) into
//! a single binary that returns structured JSON. The Python wrapper
//! `src/thegent/native/discovery_native.py` calls this binary and falls back
//! to individual subprocess calls when the binary is not present on PATH.
//!
//! Subcommands:
//!   sessions   — tmux/screen sessions as JSON array
//!   tools      — which claude/thegent/tmux/git/npx → {"tool": bool}
//!   processes  — matching processes as JSON (optional --pattern <regex>)
//!   all        — combined JSON with all of the above

use anyhow::Result;
use clap::{Parser, Subcommand};
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::process::Command;
use sysinfo::System;

// ---------------------------------------------------------------------------
// CLI definition
// ---------------------------------------------------------------------------

#[derive(Parser, Debug)]
#[command(
    name = "thegent-discovery",
    version,
    about = "Consolidated discovery binary for thegent (BKM-08)",
    long_about = "Replaces multiple subprocess spawns (git, ps, tmux, which, npx) with a \
                  single binary that emits structured JSON. Used by the Python \
                  DiscoveryClient in src/thegent/native/discovery_native.py."
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// List tmux and screen sessions as JSON
    Sessions,
    /// Check which tools are available on PATH → {"tool": bool, ...}
    Tools,
    /// List processes matching an optional regex pattern
    Processes {
        /// Regex pattern to filter process command lines (default: agent patterns)
        #[arg(short, long)]
        pattern: Option<String>,
    },
    /// Combined output: sessions + tools + processes
    All {
        /// Regex pattern for processes (default: agent patterns)
        #[arg(short, long)]
        pattern: Option<String>,
    },
}

// ---------------------------------------------------------------------------
// Output types
// ---------------------------------------------------------------------------

#[derive(Serialize, Deserialize, Debug)]
struct TmuxSession {
    session_name: String,
    windows: u32,
    created: String,
    attached: bool,
    source: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct ToolAvailability {
    tool: String,
    available: bool,
    path: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
struct ProcessInfo {
    pid: u32,
    ppid: Option<u32>,
    name: String,
    cmd: Vec<String>,
    memory_kb: u64,
    cpu_usage: f32,
    run_time_s: u64,
}

#[derive(Serialize, Deserialize, Debug)]
struct DiscoveryAll {
    sessions: Vec<TmuxSession>,
    tools: Vec<ToolAvailability>,
    processes: Vec<ProcessInfo>,
}

// ---------------------------------------------------------------------------
// Implementations
// ---------------------------------------------------------------------------

/// Default tools to probe when running `tools` or `all`
const PROBE_TOOLS: &[&str] = &[
    "claude", "thegent", "tmux", "git", "npx", "node", "python3", "screen", "cargo",
];

/// Default agent process pattern
const DEFAULT_AGENT_PATTERN: &str =
    r"claude|thegent|codex|copilot|cursor.agent|opencode|aider|gemini|droid";

fn discover_sessions() -> Vec<TmuxSession> {
    let mut sessions: Vec<TmuxSession> = Vec::new();

    // tmux sessions
    let tmux_result = Command::new("tmux")
        .args([
            "list-sessions",
            "-F",
            "#{session_name}|#{session_windows}|#{session_created_string}|#{session_attached}",
        ])
        .output();

    if let Ok(output) = tmux_result {
        if output.status.success() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            for line in stdout.lines() {
                let parts: Vec<&str> = line.splitn(4, '|').collect();
                if parts.len() == 4 {
                    sessions.push(TmuxSession {
                        session_name: parts[0].to_string(),
                        windows: parts[1].parse().unwrap_or(0),
                        created: parts[2].to_string(),
                        attached: parts[3].trim() != "0",
                        source: "tmux".to_string(),
                    });
                }
            }
        }
    }

    // GNU screen sessions (best-effort)
    let screen_result = Command::new("screen").args(["-ls"]).output();

    if let Ok(output) = screen_result {
        let stdout = String::from_utf8_lossy(&output.stdout);
        for line in stdout.lines() {
            // Screen output looks like: "	12345.session_name	(Detached)"
            let trimmed = line.trim();
            if trimmed.starts_with(|c: char| c.is_ascii_digit()) {
                let parts: Vec<&str> = trimmed.splitn(2, '.').collect();
                if parts.len() == 2 {
                    let rest = parts[1];
                    let name_end = rest.find('\t').unwrap_or(rest.len());
                    let session_name = &rest[..name_end];
                    let attached = rest.contains("(Attached)");
                    sessions.push(TmuxSession {
                        session_name: session_name.to_string(),
                        windows: 1,
                        created: String::new(),
                        attached,
                        source: "screen".to_string(),
                    });
                }
            }
        }
    }

    sessions
}

fn discover_tools() -> Vec<ToolAvailability> {
    PROBE_TOOLS
        .iter()
        .map(|tool| {
            let result = which::which(tool);
            ToolAvailability {
                tool: tool.to_string(),
                available: result.is_ok(),
                path: result.ok().and_then(|p| p.to_str().map(|s| s.to_string())),
            }
        })
        .collect()
}

fn discover_processes(pattern: Option<&str>) -> Vec<ProcessInfo> {
    let pat = pattern.unwrap_or(DEFAULT_AGENT_PATTERN);
    let re = match Regex::new(&format!("(?i){}", pat)) {
        Ok(r) => r,
        Err(_) => {
            eprintln!("Invalid regex pattern: {}", pat);
            return Vec::new();
        }
    };

    let mut sys = System::new_all();
    sys.refresh_all();

    sys.processes()
        .values()
        .filter_map(|proc| {
            let name = proc.name().to_string_lossy().to_string();
            let cmd: Vec<String> = proc
                .cmd()
                .iter()
                .map(|s| s.to_string_lossy().to_string())
                .collect();
            let cmd_str = cmd.join(" ");

            if re.is_match(&name) || re.is_match(&cmd_str) {
                Some(ProcessInfo {
                    pid: proc.pid().as_u32(),
                    ppid: proc.parent().map(|p| p.as_u32()),
                    name,
                    cmd,
                    memory_kb: proc.memory() / 1024,
                    cpu_usage: proc.cpu_usage(),
                    run_time_s: proc.run_time(),
                })
            } else {
                None
            }
        })
        .collect()
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Sessions => {
            let sessions = discover_sessions();
            println!("{}", serde_json::to_string_pretty(&sessions)?);
        }
        Commands::Tools => {
            let tools = discover_tools();
            println!("{}", serde_json::to_string_pretty(&tools)?);
        }
        Commands::Processes { pattern } => {
            let procs = discover_processes(pattern.as_deref());
            println!("{}", serde_json::to_string_pretty(&procs)?);
        }
        Commands::All { pattern } => {
            let all = DiscoveryAll {
                sessions: discover_sessions(),
                tools: discover_tools(),
                processes: discover_processes(pattern.as_deref()),
            };
            println!("{}", serde_json::to_string_pretty(&all)?);
        }
    }

    Ok(())
}
