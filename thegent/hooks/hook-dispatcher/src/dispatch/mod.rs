use std::collections::HashMap;
use std::path::Path;
use std::process::{Command, Stdio};

pub(crate) fn dispatch_notification(
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    event: &str,
    severity: &str,
    title: &str,
    message: &str,
) {
    let script = hooks_dir.join("notify-agent-event.sh");
    if !script.exists() {
        return;
    }
    let mut cmd = Command::new(script);
    cmd.arg("--event")
        .arg(event)
        .arg("--severity")
        .arg(severity)
        .arg("--title")
        .arg(title)
        .arg("--message")
        .arg(message)
        .current_dir(env_map.get("PROJECT_DIR").cloned().unwrap_or_default())
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    for (k, v) in env_map {
        cmd.env(k, v);
    }
    let _ = cmd.spawn();
}
