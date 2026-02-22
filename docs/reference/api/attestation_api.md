# attestation API Reference

> **Source**: `src/thegent/governance/attestation.py`

WP-5008: Compliance attestation generator.

---

## AttestationGenerator

Generates compliance attestations for governance reviews.

### Methods

#### AttestationGenerator.__init__

```python
__init__(self: Any, settings: ThegentSettings)
```

---

#### AttestationGenerator.generate_attestation

```python
generate_attestation(self: Any, run_id: str)
```

Generate a signed attestation for a run.

---

---

## AuditReportGenerator

WP-15004: Enterprise compliance and audit reports.

### Methods

#### AuditReportGenerator.__init__

```python
__init__(self: Any, settings: ThegentSettings)
```

---

#### AuditReportGenerator.generate_monthly_report

```python
generate_monthly_report(self: Any)
```

Generate a comprehensive monthly compliance report.

---

---

## generate_attestation

```python
generate_attestation(self: Any, run_id: str)
```

Generate a signed attestation for a run.

---

## generate_monthly_report

```python
generate_monthly_report(self: Any)
```

Generate a comprehensive monthly compliance report.

---
