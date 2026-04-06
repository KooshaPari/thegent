//! # thegent-shm CLI
//!
//! Command-line interface for shared memory primitives.
//!
//! ## xDD Methodologies Applied
//!
//! - **TDD**: Tests written alongside implementation
//! - **BDD**: CLI output follows behavior patterns
//! - **SOLID**: Single responsibility per command
//! - **DRY**: Reusable parsing logic
//! - **Clean Architecture**: Ports and adapters pattern

#![allow(non_snake_case)]

use clap::{Parser, Subcommand};
use vesselpy::adapters::inmemory::{
    InMemoryCircuitBreaker, InMemoryCommandCache, InMemoryEventStore,
};
use vesselpy::ports::driven::{
    CircuitBreakerPort, CommandCachePort, EventPort,
};

/// CLI for thegent-shm shared memory primitives
#[derive(Parser, Debug)]
#[command(name = "thegent-shm")]
#[command(about = "Shared memory primitives for multi-agent orchestration")]
#[command(version = "0.1.0")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Lock management commands
    Lock {
        #[command(subcommand)]
        action: LockAction,
    },
    /// Circuit breaker management
    Breaker {
        #[command(subcommand)]
        action: BreakerAction,
    },
    /// Event history
    Events {
        /// Show all events
        #[arg(short, long)]
        all: bool,
    },
    /// Health check
    Health,
}

#[derive(Subcommand, Debug)]
enum LockAction {
    /// Acquire a lock
    Acquire {
        /// Command hash to lock
        cmd_hash: String,
        /// Process ID
        pid: u32,
    },
    /// Release a lock
    Release {
        /// Command hash to release
        cmd_hash: String,
        /// Process ID
        pid: u32,
    },
    /// List all locks
    List,
    /// Get a specific lock
    Get {
        /// Command hash
        cmd_hash: String,
    },
}

#[derive(Subcommand, Debug)]
enum BreakerAction {
    /// Record a success
    Success {
        /// Target service name
        target: String,
    },
    /// Record a failure
    Failure {
        /// Target service name
        target: String,
    },
    /// Get breaker state
    Get {
        /// Target service name
        target: String,
    },
    /// List all breakers
    List,
}

fn main() {
    let cli = Cli::parse();

    // Create in-memory adapters for CLI use
    let mut cache = InMemoryCommandCache::new();
    let mut breakers = InMemoryCircuitBreaker::new();
    let events = InMemoryEventStore::new();

    match cli.command {
        Commands::Lock { action } => {
            match action {
                LockAction::Acquire { cmd_hash, pid } => {
                    match cache.acquire_lock(&cmd_hash, pid) {
                        Ok(()) => {
                            println!("Lock acquired: {} for PID {}", cmd_hash, pid);
                        }
                        Err(e) => {
                            eprintln!("Failed to acquire lock: {}", e);
                            std::process::exit(1);
                        }
                    }
                }
                LockAction::Release { cmd_hash, pid } => {
                    match cache.release_lock(&cmd_hash, pid) {
                        Ok(()) => {
                            println!("Lock released: {}", cmd_hash);
                        }
                        Err(e) => {
                            eprintln!("Failed to release lock: {}", e);
                            std::process::exit(1);
                        }
                    }
                }
                LockAction::List => {
                    let locks = cache.list_locks();
                    if locks.is_empty() {
                        println!("No locks held");
                    } else {
                        for lock in locks {
                            println!(
                                "{}: PID={} status={:?}",
                                lock.cmd_hash, lock.pid, lock.status
                            );
                        }
                    }
                }
                LockAction::Get { cmd_hash } => {
                    if let Some(lock) = cache.get_lock(&cmd_hash) {
                        println!("Lock found:");
                        println!("  Hash: {}", lock.cmd_hash);
                        println!("  PID: {}", lock.pid);
                        println!("  Status: {:?}", lock.status);
                    } else {
                        println!("Lock not found: {}", cmd_hash);
                    }
                }
            }
        }
        Commands::Breaker { action } => {
            match action {
                BreakerAction::Success { target } => {
                    if let Err(e) = breakers.record_success(&target) {
                        eprintln!("Failed to record success: {}", e);
                        std::process::exit(1);
                    }
                    println!("Success recorded for: {}", target);
                }
                BreakerAction::Failure { target } => {
                    if let Err(e) = breakers.record_failure(&target) {
                        eprintln!("Failed to record failure: {}", e);
                        std::process::exit(1);
                    }
                    println!("Failure recorded for: {}", target);

                    // Check if breaker opened
                    if let Some(cb) = breakers.get_breaker(&target) {
                        if matches!(cb.state, vesselpy::domain::value_objects::CircuitState::Open) {
                            println!("Circuit breaker OPENED for: {}", target);
                        }
                    }
                }
                BreakerAction::Get { target } => {
                    if let Some(cb) = breakers.get_breaker(&target) {
                        println!("Circuit Breaker: {}", cb.target);
                        println!("  State: {:?}", cb.state);
                        println!("  Failures: {}/{}", cb.failures, cb.threshold);
                    } else {
                        println!("Circuit breaker not found: {}", target);
                    }
                }
                BreakerAction::List => {
                    let breakers_list = breakers.list_breakers();
                    if breakers_list.is_empty() {
                        println!("No circuit breakers");
                    } else {
                        for cb in breakers_list {
                            println!(
                                "{}: {:?} ({}/{} failures)",
                                cb.target, cb.state, cb.failures, cb.threshold
                            );
                        }
                    }
                }
            }
        }
        Commands::Events { all } => {
            if all {
                let all_events = events.get_events_since(std::time::SystemTime::UNIX_EPOCH);
                if all_events.is_empty() {
                    println!("No events");
                } else {
                    for event in all_events {
                        println!("{:?}", event);
                    }
                }
            } else {
                println!("Use --all to show all events");
            }
        }
        Commands::Health => {
            println!("Health check endpoint ready");
            println!("Use thegent-observability crate for full health monitoring");
        }
    }
}
