# compliance_reports API Reference

> **Source**: `src/thegent/governance/compliance_reports.py`

Automated compliance reporting.

---

## ComplianceReporter

Generate automated compliance reports.

### Methods

#### ComplianceReporter.__init__

```python
__init__(self: Any)
```

Initialize compliance reporter.

---

#### ComplianceReporter.build_governance_queue

```python
build_governance_queue(self: Any, evidence: list[dict[(str, Any)]])
```

Create action queue ordered by severity then time.

---

#### ComplianceReporter.export_report

```python
export_report(self: Any, compliance_data: dict[(str, Any)], output_path: Path, format: str)
```

Export compliance report to file.

**Parameters**:

- `compliance_data`: Compliance data
- `output_path`: Output file path
- `format`: Report format

**Returns**: Path to exported file

---

#### ComplianceReporter.generate_governance_rollup

```python
generate_governance_rollup(self: Any, evidence: list[dict[(str, Any)]])
```

Build deterministic governance rollup aggregates.

---

#### ComplianceReporter.generate_governance_telemetry

```python
generate_governance_telemetry(self: Any)
```

Project key telemetry counters from rollup and queue.

---

#### ComplianceReporter.generate_report

```python
generate_report(self: Any, compliance_data: dict[(str, Any)], format: str)
```

Generate compliance report.

**Parameters**:

- `compliance_data`: Compliance data dictionary
- `format`: Report format (json, markdown, html)

**Returns**: Report content as string

---

---

## build_governance_queue

```python
build_governance_queue(self: Any, evidence: list[dict[(str, Any)]])
```

Create action queue ordered by severity then time.

---

## export_report

```python
export_report(self: Any, compliance_data: dict[(str, Any)], output_path: Path, format: str)
```

Export compliance report to file.

**Parameters**:

- `compliance_data`: Compliance data
- `output_path`: Output file path
- `format`: Report format

**Returns**: Path to exported file

---

## generate_governance_rollup

```python
generate_governance_rollup(self: Any, evidence: list[dict[(str, Any)]])
```

Build deterministic governance rollup aggregates.

---

## generate_governance_telemetry

```python
generate_governance_telemetry(self: Any)
```

Project key telemetry counters from rollup and queue.

---

## generate_report

```python
generate_report(self: Any, compliance_data: dict[(str, Any)], format: str)
```

Generate compliance report.

**Parameters**:

- `compliance_data`: Compliance data dictionary
- `format`: Report format (json, markdown, html)

**Returns**: Report content as string

---

