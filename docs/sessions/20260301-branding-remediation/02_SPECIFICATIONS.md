# Specifications

## Objective
Normalize repository owner references to `kooshapari` while preserving product naming decisions for a separate controlled pass.

## Acceptance Criteria
- No `KooshaPari` / `kooshaPari` remains in active remediation files.
- `portage` excluded.
- No package/module rename performed in this pass.

## ARUs
- Assumption: owner-casing normalization is low-risk and non-breaking.
- Risk: historical reports may intentionally preserve old references.
- Uncertainty: some product-name strings may be intentional compatibility aliases.
