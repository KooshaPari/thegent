use clap::Parser;
use std::process::ExitCode;

/// Find shim (safe execution)
#[derive(Parser)]
#[command(name = "thegent-find")]
#[command(about = "Find wrapper with fd acceleration")]
struct Args {
    #[arg(trailing_var_arg = true)]
    args: Vec<String>,
}

fn main() -> ExitCode {
    let args = Args::parse();
    let shim = thegent_shims::FindShim::new();
    shim.exec(&args.args)
}
