//! # CLI Module
//!
//! Command-line interface for subprocess management.

use clap::{Parser, Subcommand};

/// CLI for thegent subprocess management
#[derive(Parser, Debug)]
#[command(name = "thegent-subprocess")]
#[command(about = "Subprocess management for thegent", long_about = None)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

/// Subcommands
#[derive(Subcommand, Debug)]
pub enum Commands {
    /// Spawn a new process
    Spawn {
        /// Command to execute
        #[arg(short, long)]
        cmd: String,
        /// Arguments
        #[arg(short, long)]
        args: Vec<String>,
        /// Working directory
        #[arg(short, long)]
        cwd: Option<String>,
    },
    /// List running processes
    List,
    /// Get process status
    Status {
        /// Process ID
        #[arg(short, long)]
        pid: u32,
    },
    /// Kill a process
    Kill {
        /// Process ID
        #[arg(short, long)]
        pid: u32,
    },
    /// Run a command and wait for output
    Run {
        /// Command to execute
        #[arg(short, long)]
        cmd: String,
        /// Arguments
        #[arg(short, long)]
        args: Vec<String>,
    },
}
