# evidence API Reference

> **Source**: `src/thegent/orchestration/evidence.py`

Evidence capture at every promotion gate (WP-1005, FR-004).

Captures CSM state as evidence before promotion, with hash verification
and completeness audit trail.

---

## PromotionGate

WP-1005: Evidence capture and validation before state promotion.

### Methods

#### PromotionGate.__init__

```python
__init__(self, session_dir)
```

#### PromotionGate.capture_evidence

Capture CSM state as evidence; return SHA-256 hash. Appends to audit trail.

```python
capture_evidence(self, run_id, csm)
```

#### PromotionGate.validate_promotion

Validate if CSM is ready for promotion based on policy.

```python
validate_promotion(self, csm, policy)
```

#### PromotionGate.verify_evidence_hash

Verify stored evidence hash matches expected. Returns True if valid.

```python
verify_evidence_hash(self, run_id, phase, expected_hash)
```

---

## capture_evidence

Capture CSM state as evidence; return SHA-256 hash. Appends to audit trail.

```python
capture_evidence(self, run_id, csm)
```

---

## validate_promotion

Validate if CSM is ready for promotion based on policy.

```python
validate_promotion(self, csm, policy)
```

---

## verify_evidence_hash

Verify stored evidence hash matches expected. Returns True if valid.

```python
verify_evidence_hash(self, run_id, phase, expected_hash)
```

---

