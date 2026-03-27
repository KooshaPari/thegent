# WBS and DAG

## Phases

1. Foundation contracts (WP01)
2. Language layers (WP02-WP04)
3. Reconcile contract hardening (WP05)
4. Domain discovery and ranking (WP06)

## Work Packages

- WP01: Bootstrap `template-commons`
- WP02: Bootstrap `template-lang-python` (depends on WP01)
- WP03: Bootstrap `template-lang-go` (depends on WP01)
- WP04: Bootstrap `template-lang-typescript` (depends on WP01)
- WP05: Validate cross-layer reconcile contracts (depends on WP02,WP03,WP04)
- WP06: Rank initial domain repos from project inventory (depends on WP05)
