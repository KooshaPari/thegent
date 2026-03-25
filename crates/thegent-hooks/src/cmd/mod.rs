use serde_json::Value;

use crate::scan::read_input;

pub(crate) fn cmd_init() {
    let input = read_input().unwrap_or(Value::Null);

    let project_dir = input
        .get("project_dir")
        .and_then(|v| v.as_str())
        .unwrap_or(".");
    let cwd = input.get("cwd").and_then(|v| v.as_str()).unwrap_or(".");
    let session_id = input
        .get("session_id")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    let head_sha = input.get("head_sha").and_then(|v| v.as_str()).unwrap_or("");
    let hook_name = input
        .get("hook_name")
        .and_then(|v| v.as_str())
        .unwrap_or("");

    println!("export PROJECT_DIR={}", project_dir);
    println!("export CWD={}", cwd);
    println!("export SESSION_ID={}", session_id);
    println!("export HEAD_SHA={}", head_sha);
    println!("export HOOK_NAME={}", hook_name);
    println!("export THEGENT_HOOKS_INIT=1");
}
