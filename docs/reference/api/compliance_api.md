# compliance API Reference

> **Source**: `src/thegent/governance/compliance.py`

WP-15004: Certification export profiles for SOC 2, ISO, and EU AI Act.

---

## ComplianceExporter

Exports framework-specific evidence bundles for compliance audits (WP-15004).

### Methods

#### ComplianceExporter.__init__

```python
__init__(self, session_dir)
```

#### ComplianceExporter.export_bundle

Generate an evidence bundle for a specific compliance framework.

```python
export_bundle(self, framework, target_path)
```

---

## export_bundle

Generate an evidence bundle for a specific compliance framework.

```python
export_bundle(self, framework, target_path)
```

---

