// =============================================================================
// Vitest Configuration — modern test runner for TypeScript
// =============================================================================
// Coverage threshold: 80% — matches the Python coverage standard.
// Uses v8 provider (fast, built-in to Node) over istanbul.
// Globals disabled — explicit imports prevent accidental test leakage.
// =============================================================================

import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    // Explicit imports required (import { describe, it, expect } from 'vitest')
    globals: false,

    // Include test files matching these patterns
    include: ["src/**/*.test.ts", "src/**/*.spec.ts", "tests/**/*.test.ts", "tests/**/*.spec.ts"],

    // Coverage configuration
    coverage: {
      provider: "v8",
      reporter: ["text", "text-summary", "lcov"],
      include: ["src/**/*.ts"],
      exclude: [
        "src/**/*.test.ts",
        "src/**/*.spec.ts",
        "src/**/*.d.ts",
        "src/**/index.ts",
        "src/**/types.ts",
      ],
      thresholds: {
        statements: 80,
        branches: 80,
        functions: 80,
        lines: 80,
      },
    },

    // Timeout per test (10s — generous but prevents hangs)
    testTimeout: 10_000,

    // Isolate test files to prevent cross-contamination
    isolate: true,
  },
});
