// @trace WL-117
// Test runner for the VS Code extension __tests__ suite.
// Runs all compiled test files from the out/__tests__/ directory.
// Uses Node's built-in test infrastructure (no external test framework).

const path = require("node:path");
const fs = require("node:fs");
const assert = require("node:assert/strict");

// Resolve the out/__tests__ directory relative to this file's location
// This file lives in src/__tests__/ and is run from out/__tests__/ after compile.
const outDir = path.join(__dirname);

// Find all compiled test JS files
const testFiles = fs.readdirSync(outDir)
  .filter((f) => f.endsWith(".test.js") && f !== "run-tests.js")
  .map((f) => path.join(outDir, f));

if (testFiles.length === 0) {
  console.error("ERROR: No test files found in", outDir);
  process.exitCode = 1;
} else {
  console.log(`Running ${testFiles.length} test file(s) from ${outDir}\n`);
  for (const file of testFiles) {
    console.log(`--- ${path.basename(file)} ---`);
    try {
      require(file);
    } catch (err) {
      console.error(`FATAL ERROR loading ${file}:`, err);
      process.exitCode = 1;
    }
  }
}
