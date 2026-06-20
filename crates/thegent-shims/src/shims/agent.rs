// SPDX-License-Identifier: MIT OR Apache-2.0
use clap::Parser;
use std::process::ExitCode;

/// Agent shim (safe invocation)
#[derive(Parser)]
#[command(name = "thegent-agent")]
#[command(about = "Agent invocation shim")]
struct Args {
    /// Agent name (codex, copilot, dex, claude, cursor)
    agent: String,
    #[arg(trailing_var_arg = true)]
    args: Vec<String>,
}

fn main() -> ExitCode {
    let args = Args::parse();
    let shim = thegent_shims::AgentShim::new();
    shim.exec(&args.agent, &args.args)
}
