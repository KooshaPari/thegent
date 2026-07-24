# Cockpit & SOTA Audit Replay Operator Guide

> **Lane:** Phase 3/4 SOTA hardening (WP-3001 / WP-4001 / WP-Y7)
> **Source of truth:** `src/thegent/ux/cli_cockpit.py`, `src/thegent/ux/cli_sota.py`
> **Audience:** operators running `thegent cockpit …` / `thegent sota …` outside the TUI, and SOTA consumers wiring the replay output into CI / nightly harnesses.

This guide complements the inline docstrings at the top of `cli_cockpit.py` and `cli_sota.py`. It walks an operator through the three stable replay output shapes and the new `--snapshot-flip` canary workflow, with concrete CLI invocations and the exit-code contract that shell pipelines can rely on.

---

## 1. Commands at a glance

| Command | Purpose | Stable exit codes |
| --- | --- | --- |
| `thegent cockpit render` | Render the 4-pane operator cockpit from a runs/overrides snapshot. | `0` ok, `1` bad input |
| `thegent cockpit traffic summary` | Render the TRAFFIC KPI dashboard from an events snapshot. | `0` ok, `1` bad input |
| `thegent cockpit pre-check` | Evaluate a `PolicyContext` (or batch) against the governance `PolicyEngine`. | `0` allow, `3` deny, `1` bad input, `2` governance unavailable |
| `thegent cockpit replay` | Replay a corpus against an expected decision snapshot. | `0` match, `4` mismatch, `1` bad input, `2` governance unavailable |
| `thegent cockpit audit tail` | Read the JSONL audit log produced by `DecisionAuditAppender`. | `0` ok, `1` bad input |
| `thegent sota replay` | Same as `cockpit replay` but with multi-format snapshot/report ingestion. | same as `cockpit replay` |

The two replay commands share the **same evaluation + compare pipeline** (`_build_batch_decision_log` + `_compare_decision` in `cli_cockpit.py`). Only the **inputs** and **report rendering** differ.

---

## 2. Replay output shapes

SOTA tooling can consume replay output three ways. The three shapes are guaranteed-stable so CI harnesses can switch between them without rewriting parsers.

### 2.1 `cockpit replay --json`

The default snapshot format (JSON) with a structured JSON envelope:

```bash
thegent cockpit replay --batch corpus/ --compare snapshot.json --json
```

Emits a single JSON object on stdout with these guaranteed keys:

| Key | Type | Meaning |
| --- | --- | --- |
| `matched` | `bool` | `true` if every decision agrees with the snapshot, `false` if at least one mismatches. |
| `mismatches` | `list` | Each entry: `{index, fields, expected, actual}`. Empty when `matched=true`. |
| `decisions` | `list` | The produced `PolicyDecision.to_dict()` output, in corpus order. |
| `audit` | `str \| null` | Path to the JSONL audit file when `--audit-path` was set, else `null`. |

Suitable for `jq`-based pipelines:

```bash
thegent cockpit replay --batch corpus/ --compare snap.json --json \
    | jq '.matched, (.mismatches | length)'
```

### 2.2 `cockpit replay --report-format=json`

Same envelope **shape** (`matched` + `mismatches` keys present, mismatches list shape stable). Delegated to `thegent sota replay`:

```bash
thegent cockpit replay --batch corpus/ --compare snap.json --report-format=json
```

Use this when you want the sota-side report-format dispatch table to win (handy when wiring into a sota-wide ingest pipeline that already routes by `--report-format`).

### 2.3 `cockpit replay --report-format=junitxml`

CI-friendly JUnit-XML output so Jenkins / GitHub Actions / Buildkite can ingest the replay as a native test suite:

```bash
thegent cockpit replay --batch corpus/ --compare snap.json \
    --report-format=junitxml --report-path report.xml
```

Each mismatch becomes a `<failure>` entry; a clean replay becomes a passing `<testsuite>`. Omit `--report-path` to print to stdout (handy for `tee` into a build log).

The parity contract between all three shapes is pinned by `tests/test_unit_cockpit_sota_json_parity.py` — if a refactor drops `matched`/`mismatches` from one shape without touching the other, the test suite fails loudly.

---

## 3. Exit codes (the contract shell pipelines rely on)

`replay` exits with one of these codes (mirrors `pre-check`'s `0 = allow`, `3 = deny` but kept distinct so the two failure modes are branchable independently):

| Exit code | Meaning | Shell-pipeline recipe |
| --- | --- | --- |
| `0` | Every decision matches the expected snapshot. | `&& proceed` |
| `1` | Bad inputs (missing files, malformed snapshot, unknown format). | `\|\| echo "operator error"` |
| `2` | Governance module unavailable. | `\|\| echo "engine missing"` |
| `3` | At least one deny (also propagates as a mismatch in junitxml). | `\|\| echo "policy denied"` |
| `4` | At least one mismatch (compare-side failure, regardless of deny/allow). | `\|\| echo "regression"` |

---

## 4. The `--snapshot-flip` SOTA canary workflow

The `--snapshot-flip <field>` flag is a SOTA canary knob: it deliberately inverts one field on every loaded snapshot entry **in memory** so the replay walks the mismatch path without the operator having to hand-edit the `--compare` file. This is useful for CI runs that want to exercise the diff machinery + JSON envelope + exit code 4 contract end-to-end on every replay (rather than only when a real regression happens to land).

### 4.1 Supported fields and invert semantics

| Field | Invert semantics |
| --- | --- |
| `verdict` | `allow` ↔ `deny`; `warn` and unknown verdicts flip to `deny` (always disagrees with the engine's actual verdict). |
| `override_applied` | bool negation (with string-bool coercion so yaml/toml snapshots still invert cleanly). |
| `cached` | bool negation (mirror of `override_applied`). |
| any other field | best-effort bool/numeric inversion, or a stable `<flipped:<value>>` string sentinel so the compare step still records a mismatch. |

### 4.2 Example invocations

Force a mismatch on every entry's `verdict`:

```bash
thegent cockpit replay --batch corpus/ --compare snap.json \
    --snapshot-flip verdict --json | jq '.matched, .mismatches'
```

Exercise the JUnit-XML report format on the canary path:

```bash
thegent sota replay --batch corpus/ --compare snap.yaml \
    --snapshot-format yaml --report-format junitxml \
    --report-path report.xml --snapshot-flip verdict
```

The flag is honoured by **both** `cockpit replay` (forwarded through the cockpit→sota shim when a non-default report format is selected) and `sota replay` directly. The `--compare` file on disk is **never** mutated; the hash before+after the run is identical (pinned by `tests/test_unit_cockpit_snapshot_flip.py::TestCockpitReplaySnapshotFlip`).

### 4.3 When to use it

| Scenario | Recipe |
| --- | --- |
| Nightly CI wants to confirm the diff machinery is wired correctly (without waiting for a real regression). | Run `cockpit replay --snapshot-flip verdict --json` on a curated corpus; assert `matched=false` and at least one mismatch row in the envelope. |
| SOTA canary after a governance refactor. | Run `sota replay --report-format junitxml --snapshot-flip override_applied` and confirm Buildkite picks up at least one `<failure>`. |
| Operator wants to eyeball the diff machinery's output shape. | Run `cockpit replay --snapshot-flip verdict` (text mode) — the `mismatch[i]: verdict expected=X actual=Y` lines show the exact format the CI parser will receive. |

---

## 5. Federated policy flags

The replay commands share these flags for the federation contract:

| Flag | Default | Purpose |
| --- | --- | --- |
| `--namespace` | `global` | Federated policy namespace; pinned unless a corpus entry declares its own. |
| `--default-policy` | `None` | Enable federated policy lookup with this default namespace on `--commit`. |
| `--dry-run` / `--commit` | `--dry-run` | `--dry-run` is the default; pass `--commit` to cache decisions in the engine. **The canary workflow is only safe under `--dry-run`**; a flipped `verdict` against a cached engine could poison the cache. |

---

## 6. Cross-references

* `src/thegent/ux/cli_cockpit.py:566` — `_apply_snapshot_flip` / `_invert_snapshot_value` helpers (single source of truth).
* `src/thegent/ux/cli_sota.py:351` — `sota_replay --snapshot-flip` option declaration.
* `tests/test_unit_cockpit_snapshot_flip.py` — 17 tests pinning the canary workflow end-to-end.
* `tests/test_unit_cockpit_sota_json_parity.py` — JSON-shape parity contract between cockpit and sota envelopes.
* `tests/test_unit_ux_cli_cockpit_replay_audit_confirmation.py` — `--audit-append` / `--audit-overwrite` mode reporting.
* `tests/test_unit_ux_cli_cockpit_exit_code_on_cap.py` — `--max-events` + `--exit-code-on-cap` bounded-cap integration.

---

## 7. Operator checklist for nightly replay runs

1. Build a corpus of `PolicyContext` JSONs (or point at a directory of `*.json`).
2. Snapshot the engine's decisions via `thegent cockpit pre-check --batch corpus/ --json > snapshot.json`.
3. Run the canary: `thegent cockpit replay --batch corpus/ --compare snapshot.json --snapshot-flip verdict --json` and confirm exit code 4 + at least one mismatch row.
4. Run the real replay: `thegent cockpit replay --batch corpus/ --compare snapshot.json --report-format junitxml --report-path nightly.xml` and confirm exit code 0 (or branch on 4 for regressions).
5. Pipe the junitxml into your CI runner; the test cases will surface in the test tab.
6. On the next morning, run `thegent cockpit audit tail --lines 50 --path nightly-audit.jsonl` to inspect the audit trail.

If any step exits `2`, the governance module is unavailable — check the operator console for the `governance unavailable:` line.