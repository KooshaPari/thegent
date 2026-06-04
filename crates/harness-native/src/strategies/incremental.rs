use std::io::{BufRead, BufReader};
use std::path::Path;
use std::process::{Command, Stdio};

pub fn run(real_cmd: &Path, args: &[&str]) -> Result<i32, String> {
    let mut cmd = Command::new(real_cmd);
    cmd.args(args);
    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());

    match cmd.spawn() {
        Ok(mut child) => {
            let stdout = child.stdout.take();
            let stderr = child.stderr.take();

            if let Some(stdout) = stdout {
                for line in BufReader::new(stdout).lines().map_while(Result::ok) {
                    println!("{}", line);
                }
            }

            if let Some(stderr) = stderr {
                for line in BufReader::new(stderr).lines().map_while(Result::ok) {
                    eprintln!("{}", line);
                }
            }

            match child.wait() {
                Ok(exit) => Ok(exit.code().unwrap_or(1)),
                Err(e) => Err(format!("wait failed: {}", e)),
            }
        }
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
            Err(format!("command not found: {:?}", real_cmd))
        }
        Err(e) => Err(format!("failed to spawn {:?}: {}", real_cmd, e)),
    }
}
