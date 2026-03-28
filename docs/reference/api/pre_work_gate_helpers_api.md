# pre_work_gate_helpers API Reference

> **Source**: `src/thegent/cli/services/pre_work_gate_helpers.py`

Shared helpers for pre-work governance hard gate enforcement.

---

## enforce_pre_work_hard_gate

```python
enforce_pre_work_hard_gate(project_dir: Path)
```

Enforce freshness evidence before do-next/claim starts new work.

---

## evidence_age_minutes

```python
evidence_age_minutes(path: Path)
```

Return age of evidence file in minutes based on mtime.

---

## pre_work_gate_defaults

Return default regression spiral guard thresholds for pre-work hard gate.

---

## pre_work_gate_thresholds

```python
pre_work_gate_thresholds(project_dir: Path)
```

Load pre-work gate thresholds from hooks/hook-config.yaml with required defaults.

---

## pre_work_governance_block_payload

Build structured governance block payload for pre-work hard gate failures.

---

