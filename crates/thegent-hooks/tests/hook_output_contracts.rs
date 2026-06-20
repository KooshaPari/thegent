// SPDX-License-Identifier: MIT OR Apache-2.0
use std::fs;
use std::io::Write;
use std::path::PathBuf;
use std::process::{Command, Stdio};

fn cargo_bin() -> PathBuf {
    if let Ok(var) = std::env::var("CARGO_BIN_EXE_thegent-hooks") {
        return PathBuf::from(var);
    }
    if let Ok(var) = std::env::var("CARGO_BIN_EXE_thegent_hooks") {
        return PathBuf::from(var);
    }
    let mut p = std::env::current_exe().expect("current_exe");
    p.pop();
    p.pop();
    p.join("thegent-hooks")
}

fn workspace_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("crates dir")
        .parent()
        .expect("workspace root")
        .to_path_buf()
}

fn run_with_stdin(args: &[&str], stdin: &str, cwd: &std::path::Path) -> std::process::Output {
    let mut child = Command::new(cargo_bin())
        .args(args)
        .current_dir(cwd)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn command");
    child
        .stdin
        .as_mut()
        .expect("stdin")
        .write_all(stdin.as_bytes())
        .expect("write stdin");
    child.wait_with_output().expect("wait output")
}

#[test]
fn quality_gate_emits_schema_valid_result_artifact() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let project = tmp.path();
    fs::write(project.join("README.md"), "ok\n").expect("write fixture");
    let out_json = project.join("quality-gate-result.json");

    let output = Command::new(cargo_bin())
        .arg("quality-gate")
        .current_dir(project)
        .env("PROJECT_DIR", project)
        .env("CHANGED_FILES", "")
        .env("THEGENT_QUALITY_GATE_RESULT_JSON", &out_json)
        .output()
        .expect("run quality-gate");
    assert!(output.status.success());
    assert!(out_json.exists());

    let schema = workspace_root().join("schemas/thegent-hooks-result-v1.schema.json");
    let status = Command::new(cargo_bin())
        .args([
            "schema-validate",
            schema.to_str().expect("schema utf8"),
            out_json.to_str().expect("json utf8"),
        ])
        .status()
        .expect("schema-validate");
    assert!(status.success());
}

#[test]
fn security_pipeline_emits_schema_valid_result_artifact() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let project = tmp.path();
    fs::write(project.join("main.py"), "print('ok')\n").expect("write fixture");
    let out_json = project.join("security-pipeline-result.json");

    let output = run_with_stdin(
        &["security-pipeline"],
        &format!(r#"{{"project_dir":"{}"}}"#, project.display()),
        project,
    );
    assert!(output.status.success());

    // Re-run once with output env set to verify artifact path contract explicitly.
    let output_with_env = Command::new(cargo_bin())
        .arg("security-pipeline")
        .current_dir(project)
        .env("THEGENT_SECURITY_PIPELINE_RESULT_JSON", &out_json)
        .output()
        .expect("run security-pipeline with env");
    assert!(output_with_env.status.success());
    assert!(out_json.exists());

    let schema = workspace_root().join("schemas/thegent-hooks-result-v1.schema.json");
    let status = Command::new(cargo_bin())
        .args([
            "schema-validate",
            schema.to_str().expect("schema utf8"),
            out_json.to_str().expect("json utf8"),
        ])
        .status()
        .expect("schema-validate");
    assert!(status.success());
}
