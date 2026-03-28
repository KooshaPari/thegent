# governance_health_helpers API Reference

> **Source**: `src/thegent/cli/governance/governance_health_helpers.py`

Shared helpers for governance health-related CLI commands.

---

## build_cycle_json_output

Build the JSON payload for `govern go cycle`.

---

## build_cycle_result_table

Build rich table for `govern go cycle` output.

---

## build_health_dimensions_table

```python
build_health_dimensions_table(health: Any)
```

Build rich table for per-dimension health values.

---

## build_health_json_output

```python
build_health_json_output(health: Any, get_band: Callable[(Any, Any)])
```

Build the JSON payload for `govern go health`.

---

## build_health_summary_table

```python
build_health_summary_table(score: float, band_value: str)
```

Build rich table for top-level health summary.

---

## count_findings

```python
count_findings(dimension_values: dict[(str, float)])
```

Count dimensions with positive findings.

---

## extract_dimension_values

```python
extract_dimension_values(scan_result: Any)
```

Extract per-dimension current values from scanner output.

---

## resolve_band_value

```python
resolve_band_value(health: Any, get_band: Callable[(Any, Any)])
```

Resolve health band string with fallback support.

---

## resolve_status_value

```python
resolve_status_value(status: Any)
```

Resolve status enum to printable value.

---

