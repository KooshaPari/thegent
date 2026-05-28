use clap::{Parser, Subcommand};
use std::process::ExitCode;

#[derive(Parser, Debug)]
#[command(
    name = "thegent-benchmark",
    version,
    about = "Cross-repo benchmarking entry point for thegent",
    long_about = None
)]
struct Cli {
    #[command(subcommand)]
    command: Option<Command>,
}

#[derive(Subcommand, Debug)]
enum Command {
    /// List the benchmark suites known to this crate
    List,
    /// Print the benchmark invocation that should be run
    Run {
        /// Optional benchmark name to target
        #[arg(default_value = "all")]
        benchmark: String,
    },
    /// Describe what this binary is for
    Describe,
}

fn main() -> ExitCode {
    let cli = Cli::parse();

    match cli.command.unwrap_or(Command::List) {
        Command::List => {
            println!("Available benchmark suites:");
            println!("- audit_bench (criterion)");
            println!("- cross-repo orchestration benchmarks");
            println!();
            println!("Use `thegent-benchmark run <name>` to print the intended benchmark target.");
            ExitCode::SUCCESS
        }
        Command::Run { benchmark } => {
            println!("Benchmark request received: {benchmark}");
            println!("This crate currently provides the launch surface for thegent benchmarking.");
            println!("Typical execution would target a criterion bench such as `cargo bench --bench audit_bench`.");
            ExitCode::SUCCESS
        }
        Command::Describe => {
            println!("thegent-benchmark is the cross-repo benchmarking entry point for thegent.");
            println!("It exists to standardize benchmark discovery and future orchestration hooks.");
            ExitCode::SUCCESS
        }
    }
}
