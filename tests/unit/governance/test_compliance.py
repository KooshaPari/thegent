"""Tests for governance/compliance.py - WP-15004 certification export profiles."""

import json
from datetime import UTC, datetime

import pytest

from thegent.governance.compliance import (
    EU_AI_ACT_PROFILE,
    GDPR_PROFILE,
    SOX_PROFILE,
    US_SEC_PROFILE,
    AuditExporter,
    ComplianceAuditTrail,
    ComplianceControl,
    ComplianceEnforcer,
    ComplianceEvidence,
    ComplianceExporter,
    ComplianceProfile,
    ComplianceProfileType,
    ConsentRecord,
    EvidenceKind,
    EvidenceStore,
    RetentionEnforcer,
    RetentionPolicy,
)


class TestComplianceProfileType:
    """Tests for ComplianceProfileType enum."""

    def test_all_profile_types_exist(self):
        assert ComplianceProfileType.EU_AI_ACT.value == "eu-ai-act"
        assert ComplianceProfileType.US_SEC.value == "us-sec"
        assert ComplianceProfileType.SOX.value == "sox"
        assert ComplianceProfileType.GDPR.value == "gdpr"
        assert ComplianceProfileType.SOC2.value == "soc2"
        assert ComplianceProfileType.ISO27001.value == "iso27001"

    def test_profile_type_from_value(self):
        assert ComplianceProfileType("eu-ai-act") == ComplianceProfileType.EU_AI_ACT


class TestComplianceControl:
    """Tests for ComplianceControl dataclass."""

    def test_create_control(self):
        control = ComplianceControl(
            id="TEST-001",
            name="Test Control",
            description="A test control",
            mandatory=True,
            enforcement="automatic",
        )
        assert control.id == "TEST-001"
        assert control.mandatory is True
        assert control.enforcement == "automatic"

    def test_control_enforcement_types(self):
        for enforcement in ["automatic", "manual", "audit"]:
            control = ComplianceControl(
                id=f"TEST-{enforcement}",
                name=f"Test {enforcement}",
                description="Test",
                mandatory=True,
                enforcement=enforcement,
            )
            assert control.enforcement == enforcement


class TestComplianceProfile:
    """Tests for ComplianceProfile dataclass."""

    def test_get_mandatory_controls(self):
        controls = [
            ComplianceControl("C1", "C1", "D", mandatory=True, enforcement="automatic"),
            ComplianceControl("C2", "C2", "D", mandatory=False, enforcement="automatic"),
            ComplianceControl("C3", "C3", "D", mandatory=True, enforcement="manual"),
        ]
        profile = ComplianceProfile(
            profile=ComplianceProfileType.SOC2,
            jurisdiction="US",
            controls=controls,
        )
        mandatory = profile.get_mandatory_controls()
        assert len(mandatory) == 2
        assert all(c.mandatory for c in mandatory)


class TestComplianceEnforcer:
    """Tests for ComplianceEnforcer class."""

    def test_check_control_exists(self):
        profile = EU_AI_ACT_PROFILE
        enforcer = ComplianceEnforcer(profile)
        result = enforcer.check_control("HITL-HIGH-RISK", {})
        assert result is True

    def test_check_control_not_exists(self):
        profile = EU_AI_ACT_PROFILE
        enforcer = ComplianceEnforcer(profile)
        result = enforcer.check_control("NONEXISTENT", {})
        assert result is False

    def test_check_automatic_control(self):
        control = ComplianceControl("AUTO-1", "Auto", "D", mandatory=True, enforcement="automatic")
        profile = ComplianceProfile(ComplianceProfileType.SOC2, "US", [control])
        enforcer = ComplianceEnforcer(profile)
        assert enforcer.check_control("AUTO-1", {}) is True

    def test_check_manual_control_without_verification(self):
        control = ComplianceControl("MANUAL-1", "Manual", "D", mandatory=True, enforcement="manual")
        profile = ComplianceProfile(ComplianceProfileType.SOC2, "US", [control])
        enforcer = ComplianceEnforcer(profile)
        assert enforcer.check_control("MANUAL-1", {}) is False

    def test_check_manual_control_with_verification(self):
        control = ComplianceControl("MANUAL-1", "Manual", "D", mandatory=True, enforcement="manual")
        profile = ComplianceProfile(ComplianceProfileType.SOC2, "US", [control])
        enforcer = ComplianceEnforcer(profile)
        context = {"manual_verification_MANUAL-1": True}
        assert enforcer.check_control("MANUAL-1", context) is True

    def test_check_audit_control(self):
        control = ComplianceControl("AUDIT-1", "Audit", "D", mandatory=True, enforcement="audit")
        profile = ComplianceProfile(ComplianceProfileType.SOC2, "US", [control])
        enforcer = ComplianceEnforcer(profile)
        assert enforcer.check_control("AUDIT-1", {}) is True

    def test_enforce_mandatory_all_pass(self):
        enforcer = ComplianceEnforcer(EU_AI_ACT_PROFILE)
        result = enforcer.enforce_mandatory("test_action", {})
        assert result is True

    def test_enforce_mandatory_with_manual_context(self):
        control = ComplianceControl("MANUAL-1", "Manual", "D", mandatory=True, enforcement="manual")
        profile = ComplianceProfile(ComplianceProfileType.SOC2, "US", [control])
        enforcer = ComplianceEnforcer(profile)
        result = enforcer.enforce_mandatory("test_action", {"manual_verification_MANUAL-1": True})
        assert result is True


class TestComplianceProfiles:
    """Tests for predefined compliance profiles."""

    def test_eu_ai_act_profile(self):
        assert EU_AI_ACT_PROFILE.profile == ComplianceProfileType.EU_AI_ACT
        assert EU_AI_ACT_PROFILE.jurisdiction == "European Union"
        assert len(EU_AI_ACT_PROFILE.controls) >= 2

    def test_us_sec_profile(self):
        assert US_SEC_PROFILE.profile == ComplianceProfileType.US_SEC
        assert US_SEC_PROFILE.jurisdiction == "United States"
        assert len(US_SEC_PROFILE.controls) >= 2

    def test_sox_profile(self):
        assert SOX_PROFILE.profile == ComplianceProfileType.SOX
        assert len(SOX_PROFILE.controls) >= 2

    def test_gdpr_profile(self):
        assert GDPR_PROFILE.profile == ComplianceProfileType.GDPR
        assert GDPR_PROFILE.jurisdiction == "European Union"
        assert len(GDPR_PROFILE.controls) >= 3


class TestComplianceAuditTrail:
    """Tests for ComplianceAuditTrail class."""

    def test_record_action_basic(self, tmp_path):
        trail = ComplianceAuditTrail(tmp_path)
        profile = EU_AI_ACT_PROFILE
        trail.record_action("test_action", {"key": "value"}, profile)
        assert trail.ledger_file.exists()

    def test_record_action_us_sec_hashes(self, tmp_path):
        trail = ComplianceAuditTrail(tmp_path)
        profile = US_SEC_PROFILE
        trail.record_action("test_action", {}, profile)
        entries = list(trail.ledger_file.read_text().splitlines())
        assert len(entries) == 1
        entry = json.loads(entries[0])
        assert "hash" in entry
        assert "previous_hash" in entry

    def test_record_multiple_us_sec_hashes_chain(self, tmp_path):
        trail = ComplianceAuditTrail(tmp_path)
        profile = US_SEC_PROFILE
        trail.record_action("action1", {}, profile)
        trail.record_action("action2", {}, profile)
        entries = list(trail.ledger_file.read_text().splitlines())
        assert len(entries) == 2
        entry1 = json.loads(entries[0])
        entry2 = json.loads(entries[1])
        assert entry2["previous_hash"] == entry1["hash"]

    def test_compute_hash(self, tmp_path):
        trail = ComplianceAuditTrail(tmp_path)
        entry = {"action": "test"}
        h1 = trail._compute_hash(entry)
        h2 = trail._compute_hash(entry)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex length


class TestComplianceExporter:
    """Tests for ComplianceExporter class."""

    def test_export_bundle_soc2(self, tmp_path):
        exporter = ComplianceExporter(tmp_path / "session")
        target = tmp_path / "export.json"
        result = exporter.export_bundle("SOC2", target)
        assert result["framework"] == "SOC2"
        assert "availability_score" in result
        assert target.exists()

    def test_export_bundle_eu_ai_act(self, tmp_path):
        exporter = ComplianceExporter(tmp_path / "session")
        target = tmp_path / "export.json"
        result = exporter.export_bundle("EU-AI-ACT", target)
        assert result["framework"] == "EU-AI-ACT"
        assert "risk_classification" in result

    def test_export_bundle_gdpr(self, tmp_path):
        exporter = ComplianceExporter(tmp_path / "session")
        target = tmp_path / "export.json"
        result = exporter.export_bundle("GDPR", target)
        assert result["framework"] == "GDPR"
        assert "pii_redaction" in result

    def test_export_bundle_unknown_framework(self, tmp_path):
        exporter = ComplianceExporter(tmp_path / "session")
        target = tmp_path / "export.json"
        result = exporter.export_bundle("UNKNOWN", target)
        assert result["framework"] == "UNKNOWN"
        assert result["controls"] == []

    def test_get_mapped_controls(self, tmp_path):
        exporter = ComplianceExporter(tmp_path)
        assert len(exporter._get_mapped_controls("SOC2")) == 2
        assert len(exporter._get_mapped_controls("ISO27001")) == 2
        assert len(exporter._get_mapped_controls("GDPR")) == 2

    def test_collect_session_evidence_nonexistent(self, tmp_path):
        exporter = ComplianceExporter(tmp_path / "nonexistent")
        evidence = exporter._collect_session_evidence()
        assert evidence == []

    def test_collect_session_evidence_with_files(self, tmp_path):
        session = tmp_path / "session"
        session.mkdir()
        (session / "test.json").write_text("{}")
        (session / "test.jsonl").write_text('{"a":1}\n{"b":2}')
        (session / "test.txt").write_text("ignore")
        exporter = ComplianceExporter(session)
        evidence = exporter._collect_session_evidence()
        assert len(evidence) == 2


class TestComplianceEvidence:
    """Tests for ComplianceEvidence Pydantic model."""

    def test_create_evidence(self):
        evidence = ComplianceEvidence(
            evidence_id="test-123",
            kind="agent_decision",
            actor="test-agent",
            resource="test-resource",
            payload={"key": "value"},
            timestamp_utc="2024-01-01T00:00:00+00:00",
            prev_hash="prev",
            entry_hash="entry",
        )
        assert evidence.evidence_id == "test-123"
        assert evidence.kind == "agent_decision"

    def test_compute_hash(self):
        entry = {
            "evidence_id": "test",
            "kind": "agent_decision",
            "actor": "agent",
            "resource": "",
            "payload": {},
            "timestamp_utc": "2024-01-01T00:00:00+00:00",
            "prev_hash": "",
        }
        hash_result = ComplianceEvidence.compute_hash(entry, "prev")
        assert len(hash_result) == 64

    def test_frozen_model(self):
        evidence = ComplianceEvidence(
            evidence_id="test",
            kind="agent_decision",
            actor="agent",
            timestamp_utc="2024-01-01T00:00:00+00:00",
        )
        with pytest.raises(Exception):  # Pydantic frozen model
            evidence.evidence_id = "changed"


class TestEvidenceStore:
    """Tests for EvidenceStore class."""

    def test_append(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        evidence = store.append(kind="agent_decision", actor="test-agent")
        assert evidence.evidence_id is not None
        assert evidence.kind == "agent_decision"

    def test_append_with_custom_id(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        evidence = store.append(kind="agent_decision", actor="test", evidence_id="custom-123")
        assert evidence.evidence_id == "custom-123"

    def test_append_with_resource_and_payload(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        evidence = store.append(
            kind="human_approval",
            actor="admin",
            resource="resource-1",
            payload={"approved": True},
        )
        assert evidence.resource == "resource-1"
        assert evidence.payload == {"approved": True}

    def test_list_all_empty(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        assert store.list_all() == []

    def test_list_all(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="a1")
        store.append(kind="human_approval", actor="a2")
        records = store.list_all()
        assert len(records) == 2

    def test_list_since(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="a1")
        import time
        time.sleep(0.01)
        cutoff = datetime.now(UTC)
        time.sleep(0.01)
        store.append(kind="human_approval", actor="a2")
        records = store.list_since(cutoff)
        assert len(records) == 1
        assert records[0].actor == "a2"

    def test_purge_older_than_no_records(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        count = store.purge_older_than(30)
        assert count == 0

    def test_purge_older_than_negative_days_raises(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        with pytest.raises(ValueError, match="non-negative"):
            store.purge_older_than(-1)

    def test_purge_older_than_rebuilds_chain(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="old")
        import time
        time.sleep(0.01)
        cutoff = datetime.now(UTC)
        time.sleep(0.01)
        store.append(kind="human_approval", actor="new")
        count = store.purge_older_than(0)
        assert count == 1
        records = store.list_all()
        assert len(records) == 1
        assert records[0].actor == "new"
        assert store.verify_integrity() is True
        recent_records = store.list_since(cutoff)
        assert len(recent_records) == 1

    def test_verify_integrity_empty(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        assert store.verify_integrity() is True

    def test_verify_integrity_valid(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="a1")
        store.append(kind="human_approval", actor="a2")
        assert store.verify_integrity() is True

    def test_verify_integrity_tampered(self, tmp_path):
        store_path = tmp_path / "evidence.jsonl"
        store = EvidenceStore(store_path)
        store.append(kind="agent_decision", actor="a1")
        # Tamper with the file
        lines = store_path.read_text().splitlines()
        lines[0] = lines[0][:-5] + '"tampered": true}'
        store_path.write_text("\n".join(lines) + "\n")
        assert store.verify_integrity() is False


class TestRetentionPolicy:
    """Tests for RetentionPolicy Pydantic model."""

    def test_create_valid_policy(self):
        policy = RetentionPolicy(
            policy_id="pol-1",
            tenant_id="tenant-1",
            data_category="logs",
            retention_days=30,
            consent_required=False,
            created_at="2024-01-01T00:00:00+00:00",
        )
        assert policy.retention_days == 30

    def test_retention_days_validation(self):
        with pytest.raises(Exception):  # validation error
            RetentionPolicy(
                policy_id="pol-1",
                tenant_id="tenant-1",
                data_category="logs",
                retention_days=-1,  # invalid
                created_at="2024-01-01T00:00:00+00:00",
            )


class TestConsentRecord:
    """Tests for ConsentRecord Pydantic model."""

    def test_create_consent(self):
        record = ConsentRecord(
            consent_id="consent-1",
            tenant_id="tenant-1",
            subject_id="subject-1",
            data_category="marketing",
            granted=True,
            granted_at="2024-01-01T00:00:00+00:00",
        )
        assert record.granted is True
        assert record.withdrawn_at is None

    def test_withdrawn_consent(self):
        record = ConsentRecord(
            consent_id="consent-1",
            tenant_id="tenant-1",
            subject_id="subject-1",
            data_category="marketing",
            granted=True,
            granted_at="2024-01-01T00:00:00+00:00",
            withdrawn_at="2024-06-01T00:00:00+00:00",
        )
        assert record.granted is True
        assert record.withdrawn_at is not None


class TestRetentionEnforcer:
    """Tests for RetentionEnforcer class."""

    def test_add_policy(self, tmp_path):
        enforcer = RetentionEnforcer(tmp_path)
        policy = RetentionPolicy(
            policy_id="pol-1",
            tenant_id="tenant-1",
            data_category="logs",
            retention_days=30,
            created_at="2024-01-01T00:00:00+00:00",
        )
        enforcer.add_policy(policy)
        policies = enforcer.list_policies()
        assert len(policies) == 1
        assert policies[0].policy_id == "pol-1"

    def test_add_duplicate_policy_raises(self, tmp_path):
        enforcer = RetentionEnforcer(tmp_path)
        policy = RetentionPolicy(
            policy_id="pol-1",
            tenant_id="tenant-1",
            data_category="logs",
            retention_days=30,
            created_at="2024-01-01T00:00:00+00:00",
        )
        enforcer.add_policy(policy)
        with pytest.raises(ValueError, match="already exists"):
            enforcer.add_policy(policy)

    def test_get_policy(self, tmp_path):
        enforcer = RetentionEnforcer(tmp_path)
        policy = RetentionPolicy(
            policy_id="pol-1",
            tenant_id="tenant-1",
            data_category="logs",
            retention_days=30,
            created_at="2024-01-01T00:00:00+00:00",
        )
        enforcer.add_policy(policy)
        retrieved = enforcer.get_policy("pol-1")
        assert retrieved.policy_id == "pol-1"

    def test_get_nonexistent_policy_raises(self, tmp_path):
        enforcer = RetentionEnforcer(tmp_path)
        with pytest.raises(KeyError, match="not found"):
            enforcer.get_policy("nonexistent")

    def test_record_consent(self, tmp_path):
        enforcer = RetentionEnforcer(tmp_path)
        record = ConsentRecord(
            consent_id="consent-1",
            tenant_id="tenant-1",
            subject_id="subject-1",
            data_category="marketing",
            granted=True,
            granted_at="2024-01-01T00:00:00+00:00",
        )
        enforcer.record_consent(record)
        consents = enforcer.list_consents()
        assert len(consents) == 1

    def test_list_consents_filter_by_tenant(self, tmp_path):
        enforcer = RetentionEnforcer(tmp_path)
        enforcer.record_consent(
            ConsentRecord(
                consent_id="c1",
                tenant_id="t1",
                subject_id="s1",
                data_category="d1",
                granted=True,
                granted_at="2024-01-01T00:00:00+00:00",
            )
        )
        enforcer.record_consent(
            ConsentRecord(
                consent_id="c2",
                tenant_id="t2",
                subject_id="s2",
                data_category="d2",
                granted=True,
                granted_at="2024-01-01T00:00:00+00:00",
            )
        )
        t1_consents = enforcer.list_consents(tenant_id="t1")
        assert len(t1_consents) == 1

    def test_has_active_consent(self, tmp_path):
        enforcer = RetentionEnforcer(tmp_path)
        enforcer.record_consent(
            ConsentRecord(
                consent_id="c1",
                tenant_id="t1",
                subject_id="s1",
                data_category="marketing",
                granted=True,
                granted_at="2024-01-01T00:00:00+00:00",
            )
        )
        assert enforcer.has_active_consent(
            tenant_id="t1", subject_id="s1", data_category="marketing"
        ) is True

    def test_has_no_active_consent_withdrawn(self, tmp_path):
        enforcer = RetentionEnforcer(tmp_path)
        enforcer.record_consent(
            ConsentRecord(
                consent_id="c1",
                tenant_id="t1",
                subject_id="s1",
                data_category="marketing",
                granted=True,
                granted_at="2024-01-01T00:00:00+00:00",
                withdrawn_at="2024-06-01T00:00:00+00:00",
            )
        )
        assert enforcer.has_active_consent(
            tenant_id="t1", subject_id="s1", data_category="marketing"
        ) is False

    def test_purge_tenant_data_no_policies(self, tmp_path):
        enforcer = RetentionEnforcer(tmp_path)
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        with pytest.raises(KeyError, match="No retention policies"):
            enforcer.purge_tenant_data(tenant_id="nonexistent", evidence_store=store)

    def test_purge_tenant_data_consent_required_missing(self, tmp_path):
        enforcer = RetentionEnforcer(tmp_path)
        enforcer.add_policy(
            RetentionPolicy(
                policy_id="pol-1",
                tenant_id="t1",
                data_category="restricted",
                retention_days=30,
                consent_required=True,
                created_at="2024-01-01T00:00:00+00:00",
            )
        )
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        with pytest.raises(RuntimeError, match="Consent required"):
            enforcer.purge_tenant_data(tenant_id="t1", evidence_store=store)

    def test_purge_tenant_data_success(self, tmp_path):
        enforcer = RetentionEnforcer(tmp_path)
        enforcer.add_policy(
            RetentionPolicy(
                policy_id="pol-1",
                tenant_id="t1",
                data_category="logs",
                retention_days=30,
                consent_required=False,
                created_at="2024-01-01T00:00:00+00:00",
            )
        )
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="test")
        summary = enforcer.purge_tenant_data(tenant_id="t1", evidence_store=store)
        assert summary["tenant_id"] == "t1"
        assert "purged_by_policy" in summary


class TestAuditExporter:
    """Tests for AuditExporter class."""

    def test_export_json_empty(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        exporter = AuditExporter(store)
        result = exporter.export_json()
        assert result["record_count"] == 0
        assert result["integrity_verified"] is True

    def test_export_json_with_records(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="test")
        exporter = AuditExporter(store)
        result = exporter.export_json()
        assert result["record_count"] == 1

    def test_export_json_with_kind_filter(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="a1")
        store.append(kind="human_approval", actor="a2")
        exporter = AuditExporter(store)
        result = exporter.export_json(kind_filter=["agent_decision"])
        assert result["record_count"] == 1

    def test_export_json_invalid_kind_filter(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        exporter = AuditExporter(store)
        with pytest.raises(ValueError, match="Unknown evidence kind"):
            exporter.export_json(kind_filter=["invalid_kind"])

    def test_export_json_since_days(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="a1")
        import time
        time.sleep(0.01)
        exporter = AuditExporter(store)
        result = exporter.export_json(since_days=0)
        assert result["record_count"] == 0

    def test_export_json_to_file(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="test")
        exporter = AuditExporter(store)
        out_path = tmp_path / "export.json"
        result = exporter.export_json(output_path=out_path)
        assert out_path.exists()
        assert result["record_count"] == 1

    def test_reconcile_export_matching(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="a1")
        exporter = AuditExporter(store)
        result = exporter.reconcile_export(expected_count=1)
        assert result["record_count"] == 1

    def test_reconcile_export_mismatch_raises(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="a1")
        exporter = AuditExporter(store)
        with pytest.raises(RuntimeError, match="mismatch"):
            exporter.reconcile_export(expected_count=5)

    def test_enforce_integrity_valid(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="test")
        exporter = AuditExporter(store)
        assert exporter.enforce_integrity() is True

    def test_enforce_integrity_invalid_raises(self, tmp_path):
        store_path = tmp_path / "evidence.jsonl"
        store = EvidenceStore(store_path)
        store.append(kind="agent_decision", actor="a1")
        lines = store_path.read_text().splitlines()
        lines[0] = lines[0][:-5] + '"tampered": true}'
        store_path.write_text("\n".join(lines) + "\n")
        exporter = AuditExporter(store)
        with pytest.raises(RuntimeError, match="integrity verification failed"):
            exporter.enforce_integrity()

    def test_export_checkpoint(self, tmp_path):
        store = EvidenceStore(tmp_path / "evidence.jsonl")
        store.append(kind="agent_decision", actor="test")
        exporter = AuditExporter(store)
        out_path = tmp_path / "checkpoint.json"
        result = exporter.export_checkpoint(checkpoint_id="ckpt-1", output_path=out_path)
        assert result["checkpoint_id"] == "ckpt-1"
        assert result["record_count"] == 1
        assert "evidence_digest_sha256" in result
        assert out_path.exists()


class TestEvidenceKind:
    """Tests for EvidenceKind type literal."""

    def test_all_evidence_kinds_valid(self):
        for kind in EvidenceKind.__args__:
            assert isinstance(kind, str)
            assert len(kind) > 0
