# Pull Request Template

## Summary

- Briefly describe what this PR changes.
- Why this change is required and what risk it addresses.

## Artifact Links (required before review)

- [ ] Pytest traceability artifact:
  <!-- Add path or URL, e.g. `artifacts/pytest/traceability/requirements-map.json` -->
- [ ] PR gate artifact (if requirements changed):
  <!-- Add path or URL, e.g. `artifacts/pytest/requirements/requirements-gate.json` -->
- [ ] Benchmark artifact (if benchmark scope changed):
  <!-- Add path or URL, e.g. `benchmarks/results/.../summary.json` -->

## Functional Requirements Mapping (required)

- [ ] FR mapping evidence provided:
  <!-- Add requirement IDs and evidence source per line:
       - FR-XXX-001 -> `tests/...::test_x` -->
- [ ] Traceability evidence included:
  <!-- Reference `traceability-links.json` / `requirements-map.json` rows, or explain why it is still in migration. -->
