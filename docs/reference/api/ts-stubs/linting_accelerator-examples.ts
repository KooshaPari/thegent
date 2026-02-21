// Auto-generated usage examples for linting_accelerator
// Source: generate-api-docs.py

import { LintResult, LintingAccelerator, is_eslint_available, is_oxlint_available, is_ruff_available, lint, run_eslint, run_oxlint, run_ruff } from "./linting_accelerator";

// Create a LintResult instance
const lintresult = new LintResult();

// Create a LintingAccelerator instance
const lintingaccelerator = new LintingAccelerator();
lintingaccelerator.is_eslint_available();
lintingaccelerator.is_oxlint_available();
lintingaccelerator.is_ruff_available();
lintingaccelerator.lint(undefined as unknown as Array<string>, false, undefined as unknown as any, undefined as unknown as any);
lintingaccelerator.run_eslint(undefined as unknown as Array<string>, undefined as unknown as any);
lintingaccelerator.run_oxlint(undefined as unknown as Array<string>, undefined as unknown as any);
lintingaccelerator.run_ruff(undefined as unknown as Array<string>);

// Call is_eslint_available
is_eslint_available(undefined as unknown as any);
// Call is_oxlint_available
is_oxlint_available(undefined as unknown as any);
// Call is_ruff_available
is_ruff_available(undefined as unknown as any);
// Call lint
lint(undefined as unknown as any, undefined as unknown as Array<string>, false, undefined as unknown as any, undefined as unknown as any);
// Call run_eslint
run_eslint(undefined as unknown as any, undefined as unknown as Array<string>, undefined as unknown as any);
// Call run_oxlint
run_oxlint(undefined as unknown as any, undefined as unknown as Array<string>, undefined as unknown as any);
// Call run_ruff
run_ruff(undefined as unknown as any, undefined as unknown as Array<string>);
