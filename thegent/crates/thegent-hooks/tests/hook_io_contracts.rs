use std::fs;
use std::path::PathBuf;
use std::process::Command;

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

fn write_temp_json(contents: &str) -> (tempfile::TempDir, PathBuf) {
    let dir = tempfile::tempdir().expect("tempdir");
    let path = dir.path().join("instance.json");
    fs::write(&path, contents).expect("write temp json");
    (dir, path)
}

#[test]
fn quality_gate_schema_accepts_valid_payload() {
    let root = workspace_root();
    let schema_path = root.join("schemas/thegent-hooks-quality-gate-input-v1.schema.json");
    let (_tmp, instance_path) = write_temp_json(
        r#"{
          "rules": [],
          "context": {},
          "quality": {
            "coverage_percent": 92.5,
            "lint_issues": 0,
            "lint_errors": 0,
            "lint_warnings": 0,
            "cyclomatic_complexity": 3,
            "cognitive_complexity": 5,
            "function_max_lines": 40
          },
          "thresholds": {
            "min_coverage": 80.0,
            "max_lint_errors": 0,
            "max_cyclomatic_complexity": 10,
            "max_cognitive_complexity": 12,
            "max_function_lines": 80
          }
        }"#,
    );

    let status = Command::new(cargo_bin())
        .args([
            "schema-validate",
            schema_path.to_str().expect("schema utf8"),
            instance_path.to_str().expect("instance utf8"),
        ])
        .status()
        .expect("schema-validate");
    assert!(status.success());
}

#[test]
fn quality_gate_schema_rejects_missing_thresholds() {
    let root = workspace_root();
    let schema_path = root.join("schemas/thegent-hooks-quality-gate-input-v1.schema.json");
    let (_tmp, instance_path) = write_temp_json(
        r#"{
          "rules": [],
          "context": {}
        }"#,
    );

    let status = Command::new(cargo_bin())
        .args([
            "schema-validate",
            schema_path.to_str().expect("schema utf8"),
            instance_path.to_str().expect("instance utf8"),
        ])
        .status()
        .expect("schema-validate");
    assert_eq!(status.code(), Some(1));
}

#[test]
fn security_pipeline_schema_accepts_valid_payload() {
    let root = workspace_root();
    let schema_path = root.join("schemas/thegent-hooks-security-pipeline-input-v1.schema.json");
    let (_tmp, instance_path) = write_temp_json(
        r#"{
          "text": "OPENAI_API_KEY=sk-redacted",
          "files": ["src/main.py"],
          "semgrep_json": null,
          "fail_on": "warning"
        }"#,
    );

    let status = Command::new(cargo_bin())
        .args([
            "schema-validate",
            schema_path.to_str().expect("schema utf8"),
            instance_path.to_str().expect("instance utf8"),
        ])
        .status()
        .expect("schema-validate");
    assert!(status.success());
}

#[test]
fn security_pipeline_schema_rejects_unknown_fail_on() {
    let root = workspace_root();
    let schema_path = root.join("schemas/thegent-hooks-security-pipeline-input-v1.schema.json");
    let (_tmp, instance_path) = write_temp_json(
        r#"{
          "text": "",
          "fail_on": "blocker"
        }"#,
    );

    let status = Command::new(cargo_bin())
        .args([
            "schema-validate",
            schema_path.to_str().expect("schema utf8"),
            instance_path.to_str().expect("instance utf8"),
        ])
        .status()
        .expect("schema-validate");
    assert_eq!(status.code(), Some(1));
}
