//! # thegent-subprocess CLI
//!
//! CLI for subprocess management.

use clap::{Parser, Subcommand};
use thegent_subprocess::domain::entities::Process;
use thegent_subprocess::adapters::inmemory::{InMemoryProcessExecutor, InMemoryProcessRegistry};
use thegent_subprocess::ports::driven::{ProcessExecutorPort, ProcessRegistryPort};

#[derive(Parser, Debug)]
#[command(name = "thegent-subprocess")]
#[command(about = "Subprocess management for thegent", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
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

fn main() {
    let cli = Cli::parse();
    let mut executor = InMemoryProcessExecutor::new();
    let mut registry = InMemoryProcessRegistry::new();

    match cli.command {
        Commands::Spawn { cmd, args, cwd } => {
            let mut process = Process::new(cmd, args);
            if let Some(ref dir) = cwd {
                process = process.with_cwd(dir.to_string());
            }
            
            match executor.execute(&process) {
                Ok(pid) => {
                    let _ = registry.register_process(&process);
                    println!("Spawned process with PID: {}", pid);
                }
                Err(e) => {
                    eprintln!("Failed to spawn process: {}", e);
                    std::process::exit(1);
                }
            }
        }
        
        Commands::List => {
            let processes = registry.list_processes();
            
            if processes.is_empty() {
                println!("No running processes");
            } else {
                for proc in processes {
                    println!("PID: {}, Command: {}", proc.pid.unwrap_or(0), proc.command);
                }
            }
        }
        
        Commands::Status { pid } => {
            match registry.get_process(pid) {
                Some(proc) => {
                    println!("PID: {}", proc.pid.unwrap_or(0));
                    println!("Command: {}", proc.command);
                    println!("Args: {:?}", proc.args);
                }
                None => {
                    eprintln!("Process {} not found", pid);
                    std::process::exit(1);
                }
            }
        }
        
        Commands::Kill { pid } => {
            match executor.kill(pid) {
                Ok(()) => {
                    let _ = registry.unregister_process(pid);
                    println!("Killed process {}", pid);
                }
                Err(e) => {
                    eprintln!("Failed to kill process: {}", e);
                    std::process::exit(1);
                }
            }
        }
        
        Commands::Run { cmd, args } => {
            let process = Process::new(cmd, args);
            match executor.execute_with_output(&process) {
                Ok(exit_status) => {
                    println!("Exit code: {}", exit_status.code());
                }
                Err(e) => {
                    eprintln!("Failed to run command: {}", e);
                    std::process::exit(1);
                }
            }
        }
    }
}
