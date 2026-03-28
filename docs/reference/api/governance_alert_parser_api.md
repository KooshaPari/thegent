# governance_alert_parser API Reference

> **Source**: `src/thegent/governance_alert_parser.py`

Parsing helpers for governance selector alert/fail-closed CI summaries.

---

## GovernanceAlertSummary

---

## extract_fail_closed_signals

```python
extract_fail_closed_signals(log_text: str, max_lines: int)
```

Return up to max_lines lines that indicate fail-closed governance signals.

---

## parse_last_alert_summary

```python
parse_last_alert_summary(log_text: str)
```

Return the last structured governance alert line from log text.

---

## render_markdown_summary

```python
render_markdown_summary(title: str, log_text: str, max_signal_lines: int)
```

Render a markdown summary block suitable for GitHub Step Summary.

---

