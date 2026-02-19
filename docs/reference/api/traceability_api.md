# traceability API Reference

> **Source**: `src/thegent/verification/traceability.py`

WP-25003: Automated Spec-to-Code Traceability.
Scans source code and tests for FR-ID and WP-ID tags to ensure spec adherence.
Provides a coverage report mapping requirements to implementation artifacts.

---

## TraceabilityAuditor

Audits code and specs for traceability links.

### Methods

#### TraceabilityAuditor.__init__

```python
__init__(self, root_dir)
```

#### TraceabilityAuditor.audit

Scan the project for implementation of expected IDs.

```python
audit(self, expected_ids)
```

#### TraceabilityAuditor.generate_markdown_report

Format the traceability report as Markdown.

```python
generate_markdown_report(self, report)
```

---

## TraceabilityReport

Result of a traceability audit.

**Inherits from**: `BaseModel`

---

## audit

Scan the project for implementation of expected IDs.

```python
audit(self, expected_ids)
```

---

## generate_markdown_report

Format the traceability report as Markdown.

```python
generate_markdown_report(self, report)
```

---

