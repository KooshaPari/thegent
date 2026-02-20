//! harness-cache-key binary: compute cache keys for strategies

use std::env;

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.is_empty() {
        eprintln!("usage: harness-cache-key <mode> <cmd> [args...]");
        std::process::exit(1);
    }
    // TODO: Implement cache key computation
    println!("{}", args.join(":"));
}
