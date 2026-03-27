# Testing Strategy

## Layer Repo Checks

1. Manifest key presence and shape.
2. Reconcile rules section checks (`modes`, `ownership`).
3. Scaffold smoke script checks required files.

## Program-Level Checks

1. Verify all foundation repos exist.
2. Verify each repo includes CI and release prep task.
3. Verify language layers declare dependency on commons.
