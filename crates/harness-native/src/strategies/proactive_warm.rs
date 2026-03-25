use std::os::unix::process::CommandExt;
use std::path::Path;
use std::process::Command;

pub fn run(
    real_cmd: &Path,
    args: &[&str],
) -> Result<i32, String> {
    // TODO: Proactive warmup
    let err = Command::new(real_cmd).args(args).exec();
    eprintln!("exec {:?} failed: {}", real_cmd, err);
    std::process::exit(127);
}
