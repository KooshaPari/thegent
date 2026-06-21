// SPDX-License-Identifier: MIT OR Apache-2.0
use std::fs;
use std::path::PathBuf;
use std::process::Command;

fn hooks_bin() -> PathBuf {
    if let Ok(v) = std::env::var("CARGO_BIN_EXE_thegent-hooks") {
        return PathBuf::from(v);
    }
    let mut p = std::env::current_exe().expect("current_exe");
    p.pop();
    p.pop();
    p.join("thegent-hooks")
}

fn run(args: &[&str]) -> std::process::Output {
    Command::new(hooks_bin())
        .args(args)
        .output()
        .expect("run binary")
}

#[test]
fn help_lists_new_governance_evaluators() {
    let out = run(&["help"]);
    assert!(out.status.success());
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(stdout.contains("artifact-quality-eval"));
    assert!(stdout.contains("playbook-contract-eval"));
    assert!(stdout.contains("debt-registry-eval"));
    assert!(stdout.contains("formal-registry-eval"));
    assert!(stdout.contains("methodology-eval"));
    assert!(stdout.contains("reliability-eval"));
    assert!(stdout.contains("reliability-slo-eval"));
    assert!(stdout.contains("flake-quarantine-eval"));
    assert!(stdout.contains("verifier-dispute-eval"));
    assert!(stdout.contains("claim-lifecycle-eval"));
    assert!(stdout.contains("agent-claim-eval"));
    assert!(stdout.contains("elicitation-closure-eval"));
}

#[test]
fn debt_registry_passes_with_valid_json() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let debt = tmp.path().join("debt-register.json");
    let report = tmp.path().join("debt-report.json");
    fs::write(&debt, "{\"items\":[],\"version\":\"1\"}").expect("write debt");

    let out = run(&[
        "debt-registry-eval",
        "--debt",
        debt.to_str().expect("debt path"),
        "--report",
        report.to_str().expect("report path"),
        "--enabled",
        "true",
    ]);
    assert!(out.status.success());

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("pass").and_then(|v| v.as_bool()),
        Some(true)
    );
}

#[test]
fn formal_registry_fails_for_invalid_json() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let registry = tmp.path().join("FORMAL_REGISTRY.json");
    let report = tmp.path().join("formal-report.json");
    fs::write(&registry, "not-json").expect("write registry");

    let out = run(&[
        "formal-registry-eval",
        "--registry",
        registry.to_str().expect("registry path"),
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert_eq!(out.status.code(), Some(1));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("reason").and_then(|v| v.as_str()),
        Some("invalid_json")
    );
}

#[test]
fn playbook_auto_fails_when_missing() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let project_dir = tmp.path().join("project");
    let report = tmp.path().join("playbook-report.json");
    fs::create_dir_all(&project_dir).expect("create project");

    let out = run(&[
        "playbook-contract-eval",
        "--project-dir",
        project_dir.to_str().expect("project path"),
        "--report",
        report.to_str().expect("report path"),
        "--model",
        "auto",
        "--enabled",
        "true",
    ]);
    assert_eq!(out.status.code(), Some(1));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("pass").and_then(|v| v.as_bool()),
        Some(false)
    );
}

#[test]
fn artifact_quality_not_applicable_returns_three() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let project_dir = tmp.path().join("project");
    let verify_dir = tmp.path().join("verify");
    let report = tmp.path().join("artifact-report.json");
    fs::create_dir_all(&project_dir).expect("create project");
    fs::create_dir_all(&verify_dir).expect("create verify");

    let out = run(&[
        "artifact-quality-eval",
        "--project-dir",
        project_dir.to_str().expect("project path"),
        "--verify-dir",
        verify_dir.to_str().expect("verify path"),
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert_eq!(out.status.code(), Some(3));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("status").and_then(|v| v.as_str()),
        Some("not_applicable")
    );
}

#[test]
fn methodology_eval_passes_when_attestation_is_clean() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let attestation = tmp.path().join("qa-attestation.json");
    let report = tmp.path().join("methodology-report.json");
    fs::write(
        &attestation,
        r#"{
          "summary": {"fr_total": 4, "fr_covered": 4},
          "methodology": {
            "test_first": {"missing_test_pairs": []},
            "missing_required_test_types": []
          }
        }"#,
    )
    .expect("write attestation");

    let out = run(&[
        "methodology-eval",
        "--attestation",
        attestation.to_str().expect("attestation path"),
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert!(out.status.success());

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("pass").and_then(|v| v.as_bool()),
        Some(true)
    );
}

#[test]
fn methodology_eval_fails_when_methodology_has_gaps() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let attestation = tmp.path().join("qa-attestation.json");
    let report = tmp.path().join("methodology-report.json");
    fs::write(
        &attestation,
        r#"{
          "summary": {"fr_total": 3, "fr_covered": 1},
          "methodology": {
            "test_first": {"missing_test_pairs": ["FR-1"]},
            "missing_required_test_types": ["integration"]
          }
        }"#,
    )
    .expect("write attestation");

    let out = run(&[
        "methodology-eval",
        "--attestation",
        attestation.to_str().expect("attestation path"),
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert_eq!(out.status.code(), Some(1));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("error_count").and_then(|v| v.as_u64()),
        Some(3)
    );
}

#[test]
fn methodology_eval_not_applicable_when_attestation_missing() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let attestation = tmp.path().join("missing-qa-attestation.json");
    let report = tmp.path().join("methodology-report.json");

    let out = run(&[
        "methodology-eval",
        "--attestation",
        attestation.to_str().expect("attestation path"),
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert_eq!(out.status.code(), Some(3));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("status").and_then(|v| v.as_str()),
        Some("not_applicable")
    );
}

#[test]
fn reliability_eval_fails_when_flake_exceeds_threshold() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let results = tmp.path().join("results.json");
    let report = tmp.path().join("reliability-report.json");
    fs::write(&results, r#"{"total":10,"failed":2,"flaky":3}"#).expect("write results");

    let out = run(&[
        "reliability-eval",
        "--results",
        results.to_str().expect("results path"),
        "--max-flake",
        "0.10",
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert_eq!(out.status.code(), Some(1));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("pass").and_then(|v| v.as_bool()),
        Some(false)
    );
}

#[test]
fn reliability_slo_warns_in_advisory_mode() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let results = tmp.path().join("results.json");
    let report = tmp.path().join("slo-report.json");
    fs::write(&results, r#"{"total":10,"failed":2,"flaky":3}"#).expect("write results");

    let out = run(&[
        "reliability-slo-eval",
        "--results",
        results.to_str().expect("results path"),
        "--report",
        report.to_str().expect("report path"),
        "--tier",
        "established",
        "--enabled",
        "false",
        "--max-flake",
        "0.10",
        "--min-pass",
        "0.90",
    ]);
    assert!(out.status.success());

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("error_count").and_then(|v| v.as_u64()),
        Some(0)
    );
    assert_eq!(
        report_json.get("warn_count").and_then(|v| v.as_u64()),
        Some(2)
    );
}

#[test]
fn reliability_slo_fails_in_enforced_mode() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let results = tmp.path().join("results.json");
    let report = tmp.path().join("slo-report.json");
    fs::write(&results, r#"{"total":10,"failed":2,"flaky":3}"#).expect("write results");

    let out = run(&[
        "reliability-slo-eval",
        "--results",
        results.to_str().expect("results path"),
        "--report",
        report.to_str().expect("report path"),
        "--tier",
        "critical",
        "--enabled",
        "true",
        "--max-flake",
        "0.10",
        "--min-pass",
        "0.90",
    ]);
    assert_eq!(out.status.code(), Some(1));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("error_count").and_then(|v| v.as_u64()),
        Some(2)
    );
    assert_eq!(
        report_json.get("pass").and_then(|v| v.as_bool()),
        Some(false)
    );
}

#[test]
fn flake_quarantine_warns_in_advisory_mode_for_expired_entries() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let results = tmp.path().join("results.json");
    let quarantine = tmp.path().join("flaky-tests.json");
    let report = tmp.path().join("flake-report.json");
    fs::write(&results, r#"{"total":10,"failed":0,"flaky":0}"#).expect("write results");
    fs::write(
        &quarantine,
        r#"{"generated_at":"2026-01-01T00:00:00Z","entries":[{"test_id":"a","reason":"detected_flaky","introduced_at":"2026-01-01T00:00:00Z","expires_at":"2000-01-01T00:00:00Z","owner":"qa-system","status":"active"}]}"#,
    )
    .expect("write quarantine");

    let out = run(&[
        "flake-quarantine-eval",
        "--results",
        results.to_str().expect("results path"),
        "--quarantine",
        quarantine.to_str().expect("quarantine path"),
        "--report",
        report.to_str().expect("report path"),
        "--tier",
        "established",
        "--enabled",
        "false",
        "--ttl-days",
        "14",
    ]);
    assert!(out.status.success());

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("warn_count").and_then(|v| v.as_u64()),
        Some(1)
    );
    assert_eq!(
        report_json.get("error_count").and_then(|v| v.as_u64()),
        Some(0)
    );
}

#[test]
fn flake_quarantine_fails_in_enforced_mode_for_expired_entries() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let results = tmp.path().join("results.json");
    let quarantine = tmp.path().join("flaky-tests.json");
    let report = tmp.path().join("flake-report.json");
    fs::write(&results, r#"{"total":10,"failed":0,"flaky":0}"#).expect("write results");
    fs::write(
        &quarantine,
        r#"{"generated_at":"2026-01-01T00:00:00Z","entries":[{"test_id":"a","reason":"detected_flaky","introduced_at":"2026-01-01T00:00:00Z","expires_at":"2000-01-01T00:00:00Z","owner":"qa-system","status":"active"}]}"#,
    )
    .expect("write quarantine");

    let out = run(&[
        "flake-quarantine-eval",
        "--results",
        results.to_str().expect("results path"),
        "--quarantine",
        quarantine.to_str().expect("quarantine path"),
        "--report",
        report.to_str().expect("report path"),
        "--tier",
        "critical",
        "--enabled",
        "true",
        "--ttl-days",
        "14",
    ]);
    assert_eq!(out.status.code(), Some(1));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("error_count").and_then(|v| v.as_u64()),
        Some(1)
    );
}

#[test]
fn verifier_dispute_warns_without_policy_in_advisory_mode() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let project = tmp.path().join("project");
    let disputes = tmp.path().join("disputes.jsonl");
    let report = tmp.path().join("dispute-report.json");
    fs::create_dir_all(&project).expect("create project");
    fs::write(&disputes, "{\"status\":\"open\"}\n").expect("write disputes");

    let out = run(&[
        "verifier-dispute-eval",
        "--project-dir",
        project.to_str().expect("project path"),
        "--disputes",
        disputes.to_str().expect("disputes path"),
        "--report",
        report.to_str().expect("report path"),
        "--tier",
        "established",
        "--enabled",
        "false",
        "--max-open-days",
        "14",
    ]);
    assert!(out.status.success());

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("warn_count").and_then(|v| v.as_u64()),
        Some(1)
    );
    assert_eq!(
        report_json.get("open_disputes").and_then(|v| v.as_u64()),
        Some(1)
    );
}

#[test]
fn verifier_dispute_fails_without_policy_in_enforced_mode() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let project = tmp.path().join("project");
    let disputes = tmp.path().join("disputes.jsonl");
    let report = tmp.path().join("dispute-report.json");
    fs::create_dir_all(&project).expect("create project");
    fs::write(&disputes, "{\"status\":\"under_review\"}\n").expect("write disputes");

    let out = run(&[
        "verifier-dispute-eval",
        "--project-dir",
        project.to_str().expect("project path"),
        "--disputes",
        disputes.to_str().expect("disputes path"),
        "--report",
        report.to_str().expect("report path"),
        "--tier",
        "critical",
        "--enabled",
        "true",
        "--max-open-days",
        "14",
    ]);
    assert_eq!(out.status.code(), Some(1));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("error_count").and_then(|v| v.as_u64()),
        Some(1)
    );
}

#[test]
fn claim_lifecycle_fails_for_missing_file_evidence() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let project = tmp.path().join("project");
    let stmt = tmp.path().join("agent-statement.json");
    let report = tmp.path().join("claim-report.json");
    fs::create_dir_all(&project).expect("create project");
    fs::write(
        &stmt,
        r#"{"statements":[{"kind":"claim","evidence":["file://docs/missing.md","url://example.com"]}]}"#,
    )
    .expect("write statement");

    let out = run(&[
        "claim-lifecycle-eval",
        "--statement",
        stmt.to_str().expect("stmt path"),
        "--project-dir",
        project.to_str().expect("project path"),
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert_eq!(out.status.code(), Some(1));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("error_count").and_then(|v| v.as_u64()),
        Some(1)
    );
}

#[test]
fn claim_lifecycle_passes_with_valid_refs() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let project = tmp.path().join("project");
    let stmt = tmp.path().join("agent-statement.json");
    let report = tmp.path().join("claim-report.json");
    fs::create_dir_all(project.join("docs")).expect("create docs");
    fs::write(project.join("docs/existing.md"), "ok").expect("write evidence file");
    fs::write(
        &stmt,
        r#"{"statements":[{"kind":"claim","evidence":["file://docs/existing.md","att://x"]}]}"#,
    )
    .expect("write statement");

    let out = run(&[
        "claim-lifecycle-eval",
        "--statement",
        stmt.to_str().expect("stmt path"),
        "--project-dir",
        project.to_str().expect("project path"),
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert!(out.status.success());

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("pass").and_then(|v| v.as_bool()),
        Some(true)
    );
}

#[test]
fn agent_claim_fails_when_claim_has_no_evidence() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let stmt = tmp.path().join("agent-statement.json");
    let report = tmp.path().join("agent-claim-report.json");
    fs::write(
        &stmt,
        r#"{"statements":[{"kind":"claim","evidence":[]},{"kind":"decision"}]}"#,
    )
    .expect("write statement");

    let out = run(&[
        "agent-claim-eval",
        "--statement",
        stmt.to_str().expect("stmt path"),
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert_eq!(out.status.code(), Some(1));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("error_count").and_then(|v| v.as_u64()),
        Some(2)
    );
}

#[test]
fn agent_claim_passes_when_evidence_present() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let stmt = tmp.path().join("agent-statement.json");
    let report = tmp.path().join("agent-claim-report.json");
    fs::write(
        &stmt,
        r#"{"statements":[{"kind":"claim","evidence":["file://docs/a.md"]},{"kind":"observation","evidence":["url://x"]}]}"#,
    )
    .expect("write statement");

    let out = run(&[
        "agent-claim-eval",
        "--statement",
        stmt.to_str().expect("stmt path"),
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert!(out.status.success());

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("pass").and_then(|v| v.as_bool()),
        Some(true)
    );
}

#[test]
fn elicitation_closure_fails_when_open_questions_exist() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let project = tmp.path().join("project");
    let contracts = project.join("contracts");
    let items_generated = contracts.join("items-generated");
    fs::create_dir_all(&items_generated).expect("create generated dir");
    let source = project.join("story.md");
    fs::write(&source, "story").expect("write source");
    let ledger = contracts.join("ledger.json");
    fs::write(
        &ledger,
        format!(
            r#"{{"items":[{{"id":"I-1","source":"{}","state":"approved"}}]}}"#,
            source.to_string_lossy()
        ),
    )
    .expect("write ledger");
    fs::write(
        items_generated.join("I-1.json"),
        r#"{"open_questions":["q1"],"decisions":[]}"#,
    )
    .expect("write item");
    fs::write(project.join("ADR.md"), "ADR-001").expect("write adr");

    let report = tmp.path().join("elicitation-report.json");
    let out = run(&[
        "elicitation-closure-eval",
        "--ledger",
        ledger.to_str().expect("ledger path"),
        "--project-dir",
        project.to_str().expect("project path"),
        "--adr-doc",
        project.join("ADR.md").to_str().expect("adr path"),
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert_eq!(out.status.code(), Some(1));

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("error_count").and_then(|v| v.as_u64()),
        Some(1)
    );
}

#[test]
fn elicitation_closure_passes_when_decisions_match_adr() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let project = tmp.path().join("project");
    let contracts = project.join("contracts");
    let items_generated = contracts.join("items-generated");
    fs::create_dir_all(&items_generated).expect("create generated dir");
    let source = project.join("story.md");
    fs::write(&source, "story").expect("write source");
    let ledger = contracts.join("ledger.json");
    fs::write(
        &ledger,
        format!(
            r#"{{"items":[{{"id":"I-1","source":"{}","state":"verified"}}]}}"#,
            source.to_string_lossy()
        ),
    )
    .expect("write ledger");
    fs::write(
        items_generated.join("I-1.json"),
        r#"{"open_questions":[],"decisions":["ADR-001"]}"#,
    )
    .expect("write item");
    fs::write(project.join("ADR.md"), "ADR-001\nsomething").expect("write adr");

    let report = tmp.path().join("elicitation-report.json");
    let out = run(&[
        "elicitation-closure-eval",
        "--ledger",
        ledger.to_str().expect("ledger path"),
        "--project-dir",
        project.to_str().expect("project path"),
        "--adr-doc",
        project.join("ADR.md").to_str().expect("adr path"),
        "--report",
        report.to_str().expect("report path"),
    ]);
    assert!(out.status.success());

    let report_raw = fs::read_to_string(report).expect("read report");
    let report_json: serde_json::Value = serde_json::from_str(&report_raw).expect("parse report");
    assert_eq!(
        report_json.get("pass").and_then(|v| v.as_bool()),
        Some(true)
    );
}
