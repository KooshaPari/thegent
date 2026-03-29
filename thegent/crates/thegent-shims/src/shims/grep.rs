use clap::Parser;
use std::process::ExitCode;

/// Grep shim (safe execution via std::process)
#[derive(Parser)]
#[command(name = "thegent-grep")]
#[command(about = "Grep wrapper with ripgrep acceleration")]
struct Args {
    #[arg(trailing_var_arg = true)]
    args: Vec<String>,
}

fn main() -> ExitCode {
    let args = Args::parse();
    let shim = thegent_shims::GrepShim::new();
    shim.exec(&args.args)
}
