# attestation API Reference

> **Source**: `src/thegent/governance/attestation.py`

WP-5008: Compliance attestation generator.

---

## AttestationGenerator

Generates compliance attestations for governance reviews.

### Methods

#### AttestationGenerator.__init__

```python
__init__(self, settings)
```

#### AttestationGenerator.generate_attestation

Generate a signed attestation for a run.

```python
generate_attestation(self, run_id)
```

---

## AuditReportGenerator

WP-15004: Enterprise compliance and audit reports.

### Methods

#### AuditReportGenerator.__init__

```python
__init__(self, settings)
```

#### AuditReportGenerator.generate_monthly_report

Generate a comprehensive monthly compliance report.

```python
generate_monthly_report(self)
```

---

## generate_attestation

Generate a signed attestation for a run.

```python
generate_attestation(self, run_id)
```

---

## generate_monthly_report

Generate a comprehensive monthly compliance report.

```python
generate_monthly_report(self)
```

---

