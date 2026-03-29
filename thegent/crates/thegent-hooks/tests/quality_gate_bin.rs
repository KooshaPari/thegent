use std::io::Write;
use std::path::PathBuf;
use std::process::{Command, Stdio};

fn quality_gate_bin() -> PathBuf {
    if let Ok(v) = std::env::var("CARGO_BIN_EXE_quality-gate") {
        return PathBuf::from(v);
    }
    if let Ok(v) = std::env::var("CARGO_BIN_EXE_quality_gate") {
        return PathBuf::from(v);
    }
    let mut p = std::env::current_exe().expect("current_exe");
    p.pop();
    p.pop();
    p.join("quality-gate")
}

fn run_with_input(input: &str) -> std::process::Output {
    let mut child = Command::new(quality_gate_bin())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn quality-gate");
    child
        .stdin
        .as_mut()
        .expect("stdin")
        .write_all(input.as_bytes())
        .expect("write stdin");
    child.wait_with_output().expect("wait output")
}

// --- Pass cases ---

#[test]
fn quality_gate_passes_valid_metrics() {
    let input = r#"{
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
    }"#;
    let out = run_with_input(input);
    assert!(out.status.success());
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(stdout.contains("pass"));
}

#[test]
fn quality_gate_passes_at_exact_coverage_threshold() {
    let input = r#"{
      "rules": [],
      "context": {},
      "quality": {
        "coverage_percent": 80.0,
        "lint_issues": 0,
        "lint_errors": 0,
        "lint_warnings": 0,
        "cyclomatic_complexity": 0,
        "cognitive_complexity": 0,
        "function_max_lines": 0
      },
      "thresholds": {
        "min_coverage": 80.0,
        "max_lint_errors": 0,
        "max_cyclomatic_complexity": 10,
        "max_cognitive_complexity": 15,
        "max_function_lines": 40
      }
    }"#;
    let out = run_with_input(input);
    assert!(out.status.success());
}

#[test]
fn quality_gate_passes_with_zero_lint_errors_and_warnings_present() {
    let input = r#"{
      "rules": [],
      "context": {},
      "quality": {
        "coverage_percent": 95.0,
        "lint_issues": 5,
        "lint_errors": 0,
        "lint_warnings": 5,
        "cyclomatic_complexity": 4,
        "cognitive_complexity": 6,
        "function_max_lines": 35
      },
      "thresholds": {
        "min_coverage": 80.0,
        "max_lint_errors": 0,
        "max_cyclomatic_complexity": 10,
        "max_cognitive_complexity": 15,
        "max_function_lines": 40
      }
    }"#;
    let out = run_with_input(input);
    assert!(out.status.success());
}

#[test]
fn quality_gate_passes_with_policy_rule_satisfied() {
    let input = r#"{
      "rules": [
        {
          "id": "cost-limit",
          "name": "Cost Limit",
          "description": "Cost must be under 5",
          "rule_type": "cost",
          "condition": "cost < 5.0",
          "severity": "error",
          "enabled": true
        }
      ],
      "context": {"cost": 3.5},
      "quality": {
        "coverage_percent": 90.0,
        "lint_issues": 0,
        "lint_errors": 0,
        "lint_warnings": 0,
        "cyclomatic_complexity": 2,
        "cognitive_complexity": 3,
        "function_max_lines": 20
      },
      "thresholds": {
        "min_coverage": 80.0,
        "max_lint_errors": 0,
        "max_cyclomatic_complexity": 10,
        "max_cognitive_complexity": 15,
        "max_function_lines": 40
      }
    }"#;
    let out = run_with_input(input);
    assert!(out.status.success());
}

// --- Fail cases ---

#[test]
fn quality_gate_fails_low_coverage() {
    let input = r#"{
      "rules": [],
      "context": {},
      "quality": {
        "coverage_percent": 45.0,
        "lint_issues": 4,
        "lint_errors": 2,
        "lint_warnings": 2,
        "cyclomatic_complexity": 33,
        "cognitive_complexity": 50,
        "function_max_lines": 300
      },
      "thresholds": {
        "min_coverage": 80.0,
        "max_lint_errors": 0,
        "max_cyclomatic_complexity": 10,
        "max_cognitive_complexity": 20,
        "max_function_lines": 100
      }
    }"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("coverage below threshold"));
}

#[test]
fn quality_gate_fails_lint_errors_exceed_threshold() {
    let input = r#"{
      "rules": [],
      "context": {},
      "quality": {
        "coverage_percent": 90.0,
        "lint_issues": 5,
        "lint_errors": 3,
        "lint_warnings": 2,
        "cyclomatic_complexity": 3,
        "cognitive_complexity": 4,
        "function_max_lines": 30
      },
      "thresholds": {
        "min_coverage": 80.0,
        "max_lint_errors": 0,
        "max_cyclomatic_complexity": 10,
        "max_cognitive_complexity": 15,
        "max_function_lines": 40
      }
    }"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("lint errors above threshold"));
}

#[test]
fn quality_gate_fails_cyclomatic_complexity_exceeded() {
    let input = r#"{
      "rules": [],
      "context": {},
      "quality": {
        "coverage_percent": 90.0,
        "lint_issues": 0,
        "lint_errors": 0,
        "lint_warnings": 0,
        "cyclomatic_complexity": 25,
        "cognitive_complexity": 5,
        "function_max_lines": 30
      },
      "thresholds": {
        "min_coverage": 80.0,
        "max_lint_errors": 0,
        "max_cyclomatic_complexity": 10,
        "max_cognitive_complexity": 15,
        "max_function_lines": 40
      }
    }"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("cyclomatic complexity above threshold"));
}

#[test]
fn quality_gate_fails_cognitive_complexity_exceeded() {
    let input = r#"{
      "rules": [],
      "context": {},
      "quality": {
        "coverage_percent": 90.0,
        "lint_issues": 0,
        "lint_errors": 0,
        "lint_warnings": 0,
        "cyclomatic_complexity": 5,
        "cognitive_complexity": 40,
        "function_max_lines": 30
      },
      "thresholds": {
        "min_coverage": 80.0,
        "max_lint_errors": 0,
        "max_cyclomatic_complexity": 10,
        "max_cognitive_complexity": 15,
        "max_function_lines": 40
      }
    }"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("cognitive complexity above threshold"));
}

#[test]
fn quality_gate_fails_function_lines_exceeded() {
    let input = r#"{
      "rules": [],
      "context": {},
      "quality": {
        "coverage_percent": 90.0,
        "lint_issues": 0,
        "lint_errors": 0,
        "lint_warnings": 0,
        "cyclomatic_complexity": 5,
        "cognitive_complexity": 10,
        "function_max_lines": 200
      },
      "thresholds": {
        "min_coverage": 80.0,
        "max_lint_errors": 0,
        "max_cyclomatic_complexity": 10,
        "max_cognitive_complexity": 15,
        "max_function_lines": 40
      }
    }"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("max function lines above threshold"));
}

#[test]
fn quality_gate_fails_policy_rule_violation() {
    let input = r#"{
      "rules": [
        {
          "id": "coverage-policy",
          "name": "Coverage Policy",
          "description": "Coverage must be >= 80",
          "rule_type": "quality",
          "condition": "coverage >= 80",
          "severity": "error",
          "enabled": true
        }
      ],
      "context": {"coverage": 60},
      "quality": {
        "coverage_percent": 90.0,
        "lint_issues": 0,
        "lint_errors": 0,
        "lint_warnings": 0,
        "cyclomatic_complexity": 3,
        "cognitive_complexity": 4,
        "function_max_lines": 25
      },
      "thresholds": {
        "min_coverage": 80.0,
        "max_lint_errors": 0,
        "max_cyclomatic_complexity": 10,
        "max_cognitive_complexity": 15,
        "max_function_lines": 40
      }
    }"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("coverage-policy"));
}

// --- Error/edge cases ---

#[test]
fn quality_gate_returns_124_on_invalid_json() {
    let out = run_with_input("{invalid");
    assert_eq!(out.status.code(), Some(124));
}

#[test]
fn quality_gate_returns_124_on_empty_input() {
    let out = run_with_input("");
    assert_eq!(out.status.code(), Some(124));
}

#[test]
fn quality_gate_returns_124_on_missing_thresholds_field() {
    let out = run_with_input(
        r#"{"rules":[],"context":{},"quality":{"coverage_percent":90.0,"lint_issues":0,"lint_errors":0,"lint_warnings":0,"cyclomatic_complexity":0,"cognitive_complexity":0,"function_max_lines":0}}"#,
    );
    assert_eq!(out.status.code(), Some(124));
}

#[test]
fn quality_gate_multiple_violations_all_reported() {
    let input = r#"{
      "rules": [],
      "context": {},
      "quality": {
        "coverage_percent": 10.0,
        "lint_issues": 10,
        "lint_errors": 5,
        "lint_warnings": 5,
        "cyclomatic_complexity": 50,
        "cognitive_complexity": 80,
        "function_max_lines": 500
      },
      "thresholds": {
        "min_coverage": 80.0,
        "max_lint_errors": 0,
        "max_cyclomatic_complexity": 10,
        "max_cognitive_complexity": 15,
        "max_function_lines": 40
      }
    }"#;
    let out = run_with_input(input);
    assert_eq!(out.status.code(), Some(1));
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(stderr.contains("coverage below threshold"));
    assert!(stderr.contains("lint errors above threshold"));
    assert!(stderr.contains("cyclomatic complexity above threshold"));
    assert!(stderr.contains("cognitive complexity above threshold"));
    assert!(stderr.contains("max function lines above threshold"));
}

#[test]
fn quality_gate_passes_disabled_policy_rule() {
    let input = r#"{
      "rules": [
        {
          "id": "disabled-rule",
          "name": "Disabled Coverage Rule",
          "description": "Should not trigger",
          "rule_type": "quality",
          "condition": "coverage >= 99",
          "severity": "error",
          "enabled": false
        }
      ],
      "context": {"coverage": 10},
      "quality": {
        "coverage_percent": 85.0,
        "lint_issues": 0,
        "lint_errors": 0,
        "lint_warnings": 0,
        "cyclomatic_complexity": 2,
        "cognitive_complexity": 3,
        "function_max_lines": 20
      },
      "thresholds": {
        "min_coverage": 80.0,
        "max_lint_errors": 0,
        "max_cyclomatic_complexity": 10,
        "max_cognitive_complexity": 15,
        "max_function_lines": 40
      }
    }"#;
    let out = run_with_input(input);
    assert!(
        out.status.success(),
        "Disabled rule should not cause failure"
    );
}
