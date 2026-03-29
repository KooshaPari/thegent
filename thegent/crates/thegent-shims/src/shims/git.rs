use clap::Parser;
use std::process::ExitCode;

/// Git shim with thegent integration (safe - no shell invocation)
#[derive(Parser)]
#[command(name = "thegent-git")]
#[command(about = "Git wrapper with thegent integration")]
struct Args {
    #[arg(trailing_var_arg = true)]
    args: Vec<String>,
}

fn main() -> ExitCode {
    let args = Args::parse();
    let shim = thegent_shims::GitShim::new();
    shim.exec(&args.args)
}
