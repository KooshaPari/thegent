use std::os::unix::process::CommandExt;
use std::path::Path;
use std::process::Command;

pub fn run(
    _harness_home: &Path,
    real_cmd: &Path,
    _cmd_name: &str,
    _max_concurrent: u32,
    _priority: &str,
    _agent_name: &str,
    args: &[&str],
) -> Result<i32, String> {
    // TODO: Load balancing
    let err = Command::new(real_cmd).args(args).exec();
    eprintln!("exec {:?} failed: {}", real_cmd, err);
    std::process::exit(127);
}
