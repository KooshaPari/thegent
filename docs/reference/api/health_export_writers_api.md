# health_export_writers API Reference

> **Source**: `src/thegent/cli/commands/output/health_export_writers.py`

Writers for health report/gate export payloads.

---

## write_health_gate_export

```python
write_health_gate_export(output: Path, report: dict[(str, Any)], export_format: str, overwrite: bool) -> str
```

---

## write_health_trend_export

```python
write_health_trend_export(output: Path, result: dict[(str, Any)], export_format: str, overwrite: bool, print_error: Any) -> str
```

---

## write_report_export

```python
write_report_export(output: Path, report: dict[(str, Any)], export_format: str, overwrite: bool) -> str
```

---

