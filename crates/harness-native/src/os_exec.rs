//! Portable process-exec helper.
//!
//! On Unix, `CommandExt::exec()` replaces the current process image with the
//! child, preserving the same PID and signal handling — which is the correct
//! behavior for a dispatcher (helios-shield) since callers' `$!`, trap
//! handlers, and `wait` calls continue to refer to the real binary.
//!
//! On Windows, `exec` does not exist. We spawn the child, wait for it to
//! finish, and propagate its exit code via `std::process::exit`. This is a
//! spawn+wait fallback as required by the build.
use std::path::Path;
use std::process::Command;

/// Replace the current process with `cmd args`. Never returns.
///
/// On Unix this is a true `exec(2)` — the function does not return on
/// success (and on failure returns `!` after printing an error).
/// On Windows this spawns+waits and exits with the child's status.
#[cfg(unix)]
pub fn exec_replace(cmd: &Path, args: &[&str]) -> ! {
    use std::os::unix::process::CommandExt;
    let err = Command::new(cmd).args(args).exec();
    eprintln!("helios-shield: exec {:?} failed: {}", cmd, err);
    std::process::exit(127);
}

/// Spawn-and-wait fallback for non-Unix platforms. Mirrors the Unix path's
/// "never returns on success" contract by calling `std::process::exit` with
/// the child's status.
#[cfg(not(unix))]
pub fn exec_replace(cmd: &Path, args: &[&str]) -> ! {
    match Command::new(cmd).args(args).status() {
        Ok(status) => {
            let code = status.code().unwrap_or(1);
            std::process::exit(code);
        }
        Err(e) => {
            eprintln!("helios-shield: spawn {:?} failed: {}", cmd, e);
            std::process::exit(127);
        }
    }
}
