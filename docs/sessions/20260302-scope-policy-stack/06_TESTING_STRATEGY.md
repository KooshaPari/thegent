# 06_TESTING_STRATEGY

- Manual dry-run:
  - `python policy-contract/resolve.py --root . --harness codex --task-domain deployment`
  - verify `policy_hash` changes as scope inputs change.
- Regression tests to add next:
  - scope merge precedence test
  - deny-list replacement and allow-list dedupe test
  - invalid schema rejection test

