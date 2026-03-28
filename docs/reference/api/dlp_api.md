# dlp API Reference

> **Source**: `src/thegent/utils/routing_impl/guardrails/dlp.py`

## DlpConfig

---

## DlpMatch

---

## DlpPattern

---

## DlpProfile

**Inherits from**: `str, Enum`

---

## DlpResult

---

## scan_dlp

```python
scan_dlp(text: str, config: Any)
```

Scan text against the configured DLP profile. Returns DlpResult.

---

## should_block_dlp

```python
should_block_dlp(result: DlpResult, config: Any)
```

Return True if the DLP result warrants blocking.

---

