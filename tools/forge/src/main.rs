//! Forge CLI Entry Point
//!
//! Command-line interface for the Forge task runner.

use std::path::PathBuf;
use std::process::ExitCode;

use clap::{Parser, Subcommand};
use tracing_subscriber::{fmt, prelude::*, EnvFilter};

use forge::{config::ForgeConfig, Forge};

/// Forge - CLI Task Runner with Parallel Execution and Hot Reload
#[derive(Parser)]
#[command(
    name = "forge",
    about = "A task runner with parallel execution and hot reload",
    version
)]
struct Cli {
    /// Configuration file path
    #[arg(short, long, default_value = "forge.toml")]
    config: PathBuf,

    /// Verbosity level
    #[arg(short, long, action = clap::ArgAction::Count)]
    verbose: u8,

    /// Suppress output
    #[arg(short, long)]
    quiet: bool,

    /// Working directory
    #[arg(short, long)]
    dir: Option<PathBuf>,

    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    /// Run tasks
    Run {
        /// Tasks to run (default: all)
        tasks: Vec<String>,

        /// Watch for changes and re-run
        #[arg(short, long)]
        watch: bool,

        /// Tasks to re-run on change
        #[arg(long, default_value = "default")]
        watch_tasks: Option<String>,
    },
    /// List available tasks
    List {
        /// Show task descriptions
        #[arg(short, long)]
        verbose: bool,
    },
    /// Initialize a new forge.toml
    Init {
        /// Overwrite existing config
        #[arg(short, long)]
        force: bool,
    },
    /// Show task information
    Info {
        /// Task name
        task: String,
    },
    /// Validate configuration
    Validate,
}

fn setup_logging(verbose: u8, quiet: bool) {
    let filter = if quiet {
        EnvFilter::try_from_default_env()
            .unwrap_or_else(|_| EnvFilter::new("warn"))
    } else {
        match verbose {
            0 => EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| EnvFilter::new("info")),
            1 => EnvFilter::new("info"),
            2 => EnvFilter::new("debug"),
            _ => EnvFilter::new("trace"),
        }
    };

    tracing_subscriber::registry()
        .with(fmt::layer().with_target(true).with_level(true))
        .with(filter)
        .init();
}

async fn run_tasks(
    config: ForgeConfig,
    tasks: Vec<String>,
    watch: bool,
) -> anyhow::Result<ExitCode> {
    let result = forge::Forge::builder(config)
        .watch(watch)
        .run(tasks)
        .await?;

    if result.failed > 0 {
        Ok(ExitCode::FAILURE)
    } else {
        Ok(ExitCode::SUCCESS)
    }
}

fn list_tasks(config: &ForgeConfig, verbose: bool) -> ExitCode {
    let tasks: Vec<_> = config.tasks.iter().collect();
    let max_name_len = tasks
        .iter()
        .map(|(name, _)| name.len())
        .max()
        .unwrap_or(0);

    for (name, task) in tasks {
        if verbose {
            let deps = if task.dependencies.is_empty() {
                String::new()
            } else {
                format!(" (deps: {})", task.dependencies.join(", "))
            };
            let desc = task
                .description
                .as_deref()
                .unwrap_or("No description");
            println!("{name:<max_name_len$} - {desc}{deps}");
        } else {
            println!("{name:<max_name_len$}", name = name);
        }
    }

    ExitCode::SUCCESS
}

fn show_task_info(config: &ForgeConfig, task_name: &str) -> ExitCode {
    match config.get_task(task_name) {
        Some(task) => {
            println!("Task: {}", task_name);
            println!("Command: {}", task.command);

            if let Some(desc) = &task.description {
                println!("Description: {}", desc);
            }

            if !task.dependencies.is_empty() {
                println!("Dependencies: {}", task.dependencies.join(", "));
            }

            if let Some(watch) = &task.watch {
                println!("Watch paths: {}", watch.join(", "));
            }

            if !task.env.is_empty() {
                println!("Environment:");
                for (key, value) in &task.env {
                    println!("  {} = {}", key, value);
                }
            }

            if task.timeout > 0 {
                println!("Timeout: {} seconds", task.timeout);
            }

            ExitCode::SUCCESS
        }
        None => {
            eprintln!("Task '{}' not found", task_name);
            ExitCode::FAILURE
        }
    }
}

fn initialize_config(force: bool) -> ExitCode {
    let config_path = PathBuf::from("forge.toml");

    if config_path.exists() && !force {
        eprintln!(
            "Configuration file already exists: {}\nUse --force to overwrite",
            config_path.display()
        );
        return ExitCode::FAILURE;
    }

    let example_config = r#"# Forge Configuration
# See: https://github.com/phenotype-dev/forge

[env]
# RUST_BACKTRACE = "1"

# Maximum parallel workers (default: number of CPUs)
# workers = 4

[tasks.default]
command = "echo 'No tasks defined. Run `forge init` to see an example.'"
description = "Default task"

# Example tasks (uncomment to use):
#
# [tasks.build]
# command = "cargo build"
# description = "Build the project"
# dependencies = []
#
# [tasks.test]
# command = "cargo test"
# description = "Run tests"
# dependencies = ["build"]
"#;

    if let Err(e) = std::fs::write(&config_path, example_config) {
        eprintln!("Failed to write config: {}", e);
        return ExitCode::FAILURE;
    }

    println!("Created: {}", config_path.display());
    ExitCode::SUCCESS
}

fn validate_config(config: &ForgeConfig) -> ExitCode {
    match config.validate() {
        Ok(_) => {
            println!("Configuration is valid");
            println!("Tasks: {}", config.tasks.len());
            println!("Workers: {:?}", config.workers);
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("Configuration error: {}", e);
            ExitCode::FAILURE
        }
    }
}

#[tokio::main]
async fn main() -> ExitCode {
    let cli = Cli::parse();

    setup_logging(cli.verbose, cli.quiet);

    if let Some(dir) = &cli.dir {
        if let Err(e) = std::env::set_current_dir(dir) {
            eprintln!("Failed to change directory: {}", e);
            return ExitCode::FAILURE;
        }
    }

    match cli.command.unwrap_or_default() {
        Commands::Run {
            tasks,
            watch,
            watch_tasks: _,
        } => {
            let config = match Forge::load_config(Some(cli.config)) {
                Ok(c) => c,
                Err(e) => {
                    eprintln!("Failed to load config: {}", e);
                    return ExitCode::FAILURE;
                }
            };

            if let Err(e) = run_tasks(config, tasks, watch).await {
                eprintln!("Execution failed: {}", e);
                return ExitCode::FAILURE;
            }
        }
        Commands::List { verbose } => {
            let config = match Forge::load_config(Some(cli.config)) {
                Ok(c) => c,
                Err(e) => {
                    eprintln!("Failed to load config: {}", e);
                    return ExitCode::FAILURE;
                }
            };
            return list_tasks(&config, verbose);
        }
        Commands::Init { force } => {
            return initialize_config(force);
        }
        Commands::Info { task } => {
            let config = match Forge::load_config(Some(cli.config)) {
                Ok(c) => c,
                Err(e) => {
                    eprintln!("Failed to load config: {}", e);
                    return ExitCode::FAILURE;
                }
            };
            return show_task_info(&config, &task);
        }
        Commands::Validate => {
            let config = match Forge::load_config(Some(cli.config)) {
                Ok(c) => c,
                Err(e) => {
                    eprintln!("Failed to load config: {}", e);
                    return ExitCode::FAILURE;
                }
            };
            return validate_config(&config);
        }
    }

    ExitCode::SUCCESS
}

impl Default for Commands {
    fn default() -> Self {
        Self::Run {
            tasks: vec![],
            watch: false,
            watch_tasks: None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cli_defaults() {
        let cli = Cli::parse_from(["forge", "run"].as_slice());
        assert_eq!(cli.config, PathBuf::from("forge.toml"));
    }

    #[test]
    fn test_run_command() {
        let cli = Cli::parse_from(["forge", "run", "build", "test"].as_slice());
        if let Commands::Run { tasks, .. } = cli.command.unwrap() {
            assert_eq!(tasks, vec!["build", "test"]);
        } else {
            panic!("Expected Run command");
        }
    }
}
