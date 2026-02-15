// Strict Vitest configuration
// Full coverage enforcement, strict assertions
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["**/*.{test,spec}.{ts,tsx,js,jsx}"],
    exclude: ["**/node_modules/**", "**/dist/**", "**/build/**"],
    coverage: {
      enabled: true,
      provider: "v8",
      reporter: ["text", "json", "html", "lcov"],
      reportsDirectory: "./coverage",
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
      exclude: [
        "**/*.d.ts",
        "**/*.config.*",
        "**/types/**",
        "**/__mocks__/**",
        "**/test/**",
      ],
    },
    reporters: ["default", "junit"],
    outputFile: {
      junit: "./test-results/junit.xml",
    },
    typecheck: {
      enabled: true,
      tsconfig: "./tsconfig.json",
    },
    testTimeout: 10000,
    hookTimeout: 10000,
    teardownTimeout: 5000,
    retry: 0,
    bail: 0,
    passWithNoTests: false,
    allowOnly: false,
    sequence: {
      shuffle: false,
    },
  },
});
