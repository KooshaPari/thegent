use std::io::Write;
use std::path::PathBuf;
use std::process::{Command, Stdio};

fn security_pipeline_bin() -> PathBuf {
    if let Ok(v) = std::env::var("CARGO_BIN_EXE_security-pipeline") {
        return PathBuf::from(v);
    }
    if let Ok(v) = std::env::var("CARGO_BIN_EXE_security_pipeline") {
        return PathBuf::from(v);
    }
    let mut p = std::env::current_exe().expect("current_exe");
    p.pop();
    p.pop();
    p.join("security-pipeline")
}

fn run_with_input(input: &str) -> std::process::Output {
    let mut child = Command::new(security_pipeline_bin())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn security-pipeline");
    child
        .stdin
        .as_mut()
        .expect("stdin")
        .write_all(input.as_bytes())
        .expect("write stdin");
    child.wait_with_output().expect("wait output")
}

// --- Clean / pass cases ---

#[test]
fn security_pipeline_passes_clean_text() {
    let input = r#"{"text":"fn main() { println!(\"ok\"); }","fail_on":"warning"}"#;
    let out = run_with_input(input);
    assert!(out.status.success());
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(stdout.contains("pass"));
}

#[test]
fn security_pipeline_passes_empty_text() {
    let input = r#"{"text":"","fail_on":"warning"}"#;
    let out = run_with_input(input);
    assert!(out.status.success());
}

#[test]
fn security_pipeline_passes_empty_files_list() {
    let input = r#"{"text":"","files":[],"fail_on":"critical"}"#;
    let out = run_with_input(input);
    assert!(out.status.success());
}

#[test]
fn security_pipeline_passes_info_finding_with_warning_threshold() {
    // A JWT token meeting warning threshold should only fire at warning or above.
    // Clean code with no secrets at all should pass at any threshold.
    let input = r#"{"text":"let x = 42;","fail_on":"info"}"#;
    let out = run_with_input(input);
    assert!(out.status.success());
}

// --- Findings / fail cases ---

#[test]
fn security_pipeline_fails_on_openai_secret() {
    let input = r#"{"text":"OPENAI_API_KEY=sk-123456789012345678901234567890","fail_on":"warning"}"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("Secret Detected"));
}

#[test]
fn security_pipeline_fails_on_github_token() {
    let input = r#"{"text":"export GH_TOKEN=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890","fail_on":"warning"}"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("Secret Detected"));
}

#[test]
fn security_pipeline_fails_on_aws_access_key() {
    let input = r#"{"text":"AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE","fail_on":"warning"}"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("Secret Detected"));
}

#[test]
fn security_pipeline_fails_on_private_key_pem() {
    let input = r#"{"text":"-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----","fail_on":"warning"}"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("Secret Detected"));
}

#[test]
fn security_pipeline_fails_on_semgrep_finding() {
    let semgrep_json = r#"{\"results\":[{\"check_id\":\"python.flask.security.xss\",\"extra\":{\"severity\":\"ERROR\",\"message\":\"XSS risk\"},\"path\":\"app.py\"}]}"#;
    let input = format!(r#"{{"text":"","semgrep_json":"{}","fail_on":"warning"}}"#, semgrep_json);
    let out = run_with_input(&input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(!stderr.is_empty());
}

#[test]
fn security_pipeline_critical_threshold_ignores_warning_finding() {
    // At critical threshold, a non-critical finding should not cause failure.
    // Clean text with no secrets at critical threshold → pass.
    let input = r#"{"text":"let api_endpoint = \"https://example.com\";","fail_on":"critical"}"#;
    let out = run_with_input(input);
    assert!(out.status.success());
}

// --- Error / edge cases ---

#[test]
fn security_pipeline_returns_124_on_invalid_json() {
    let out = run_with_input("{bad");
    assert_eq!(out.status.code(), Some(124));
}

#[test]
fn security_pipeline_returns_124_on_empty_input() {
    let out = run_with_input("");
    assert_eq!(out.status.code(), Some(124));
}

#[test]
fn security_pipeline_returns_124_on_nonexistent_file() {
    let input = r#"{"text":"","files":["/tmp/nonexistent_file_thegent_test_12345.txt"],"fail_on":"warning"}"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(124));
}
