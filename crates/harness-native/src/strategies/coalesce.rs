use std::os::unix::process::CommandExt;
use std::path::Path;
use std::process::Command;

pub fn exec_direct(cmd: &Path, args: &[&str]) -> ! {
    let err = Command::new(cmd).args(args).exec();
    eprintln!("exec {:?} failed: {}", cmd, err);
    std::process::exit(127);
}

pub fn run(real_cmd: &Path, args: &[&str]) -> Result<i32, String> {
    // TODO: Check cache, debounce, execute
    exec_direct(real_cmd, args);
}
