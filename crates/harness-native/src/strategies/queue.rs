use std::os::unix::process::CommandExt;
use std::path::Path;
use std::process::Command;

pub fn run(
    harness_home: &Path,
    real_cmd: &Path,
    cmd_name: &str,
    max_concurrent: u32,
    priority: &str,
    agent_name: &str,
    args: &[&str],
) -> Result<i32, String> {
    // TODO: Queue implementation
    let err = Command::new(real_cmd).args(args).exec();
    eprintln!("exec {:?} failed: {}", real_cmd, err);
    std::process::exit(127);
}

fn priority_num(_priority: &str) -> u32 {
    5
}
