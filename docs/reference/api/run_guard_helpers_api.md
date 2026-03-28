# run_guard_helpers API Reference

> **Source**: `src/thegent/cli/services/run_guard_helpers.py`

Helpers for run_impl pre-flight guard checks and concurrency gating.

---

## enforce_concurrency_limit

Acquire a concurrency slot and return a blocking payload when denied.

---

## enforce_input_guardrails

Validate prompt guardrails and return an error payload when blocked.

---

## get_last_guardrail_diagnostic

Return machine-readable diagnostics for the last guardrail evaluation.

---

## suggest_terminal_reuse

Emit lightweight terminal reuse hints for the current cwd.

---

