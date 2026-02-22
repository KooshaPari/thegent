### [WL-6700]
**Title:** Make `shell reload` report failure when `source ~/.zshrc` exits non-zero.
**Source Path+Line:** [thegent/src/thegent/shell_cli.py:136]
**Acceptance Checklist:**
- [ ] Capture the `subprocess.run` return code in `shell_reload` and gate success output on `returncode == 0`.
- [ ] Surface stderr/stdout snippets when sourcing fails so users can diagnose bad shell config.
- [ ] Add CLI test coverage for successful reload and non-zero exit paths.
**Notes:** Current behavior always prints success when the subprocess call returns, even if zsh sourcing fails.

### [WL-6701]
**Title:** Convert swallowed alias-probe exceptions in `shell doctor` into explicit health findings.
**Source Path+Line:** [thegent/src/thegent/shell_cli.py:177]
**Acceptance Checklist:**
- [ ] Replace the bare `except` in alias detection with typed exception handling.
- [ ] Append a doctor issue entry when alias inspection fails due to timeout or subprocess error.
- [ ] Add tests asserting failure diagnostics appear in doctor output instead of being silently ignored.
**Notes:** Silent failure in the diagnostic probe can produce false healthy reports.

### [WL-6702]
**Title:** Emit fallback diagnostics when control-plane provider import fails.
**Source Path+Line:** [thegent/src/thegent/config_provider.py:93]
**Acceptance Checklist:**
- [ ] Replace the `except ImportError: pass` branch with a logged warning that includes module context.
- [ ] Preserve fallback to `EnvConfigProvider` so runtime behavior remains compatible.
- [ ] Add tests validating warning emission and fallback selection when control-plane client is unavailable.
**Notes:** Suppressing import failures hides why control-plane mode was not activated.

### [WL-6703]
**Title:** Safely quote remote working-directory changes in SSH command assembly.
**Source Path+Line:** [thegent/src/thegent/research/remote_compute.py:37]
**Acceptance Checklist:**
- [ ] Replace direct string interpolation in `full_command` with shell-safe quoting for `cwd` and command segments.
- [ ] Add tests covering spaces/shell metacharacters in remote paths to avoid command breakage or injection.
- [ ] Preserve existing response payload shape (`stdout`, `stderr`, `exit_code`, `status`).
**Notes:** Building `cd {cwd} && {command}` via raw interpolation is brittle for paths containing shell-sensitive characters.

### [WL-6704]
**Title:** Make Ghostty auto-configuration append logic idempotent with explicit managed markers.
**Source Path+Line:** [thegent/src/thegent/ide/auto_setup.py:193]
**Acceptance Checklist:**
- [ ] Replace free-form block append with begin/end managed markers to prevent duplicate inserts.
- [ ] Add update logic that rewrites an existing managed block instead of appending another copy.
- [ ] Add tests for first-run insert and repeated-run no-op behavior.
**Notes:** Current append-based configuration can drift and produce repeated shell integration snippets.

### [WL-6705]
**Title:** Track skipped files and parse failures during docs index rebuild.
**Source Path+Line:** [thegent/src/docs_engine/cli/commands.py:83]
**Acceptance Checklist:**
- [ ] Replace blanket suppression in `index_cmd` with typed parse/read exception handling.
- [ ] Count and report skipped files plus failure reasons in command output.
- [ ] Add tests for malformed frontmatter and unreadable markdown files.
**Notes:** Fully silent skip behavior makes index coverage and parsing reliability difficult to audit.

### [WL-6706]
**Title:** Add parse-error diagnostics when loading JSON conversation companions.
**Source Path+Line:** [thegent/src/thegent/research/always_write_dumps.py:218]
**Acceptance Checklist:**
- [ ] Catch JSON decode errors explicitly in `load_dump_json` and log the failing file path.
- [ ] Keep fail-open return semantics (`None`) for compatibility with existing callers.
- [ ] Add tests for valid JSON, malformed JSON, and missing companion files.
**Notes:** Returning `None` without diagnostics obscures whether the companion is missing or corrupted.

### [WL-6707]
**Title:** Complete mesh discover flow by surfacing discovered agents to users and state.
**Source Path+Line:** [thegent/src/thegent/mesh/main.py:53]
**Acceptance Checklist:**
- [ ] Replace no-op loop body with concrete registration and/or output behavior for each discovered agent.
- [ ] Add CLI output summarizing discovered agent count and identifiers.
- [ ] Add tests ensuring discover does observable work for both auto-detect and pattern-filter modes.
**Notes:** The current loop executes `pass`, so discovery results are effectively dropped.

### [WL-6708]
**Title:** Prevent partial loader state after artifact parse failures in `load_all`.
**Source Path+Line:** [thegent/src/thegent/planning/board_artifact_loader.py:65]
**Acceptance Checklist:**
- [ ] Isolate JSON/CSV load mutations so failed parse attempts do not leave partially-updated `items`, `slices`, or `metadata`.
- [ ] Include file-specific context in `result["errors"]` entries for each load failure.
- [ ] Add tests for malformed JSON and CSV inputs verifying deterministic post-failure state.
**Notes:** Current exception handling records errors but can leave in-memory loader structures in mixed states.

### [WL-6709]
**Title:** Normalize empty metric stats output to a stable schema.
**Source Path+Line:** [thegent/src/thegent/metrics/collector.py:39]
**Acceptance Checklist:**
- [ ] Change `get_stats` to return a consistent typed payload for empty metrics (for example `count=0` with nullable min/max/avg).
- [ ] Update downstream callers/tests to rely on schema stability rather than truthy dict checks.
- [ ] Add unit tests for empty, single-value, and multi-value metric series.
**Notes:** Returning `{}` for empty series forces callers into shape-branching and weakens interface predictability.
