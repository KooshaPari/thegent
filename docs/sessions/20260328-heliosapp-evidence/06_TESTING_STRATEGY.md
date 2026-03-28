# Testing strategy & evidence

| Command | Outcome |
| --- | --- |
| `bun run test:integration` | FAIL – 29 tests failed across the renderer/lane/registry/watchdog/performance/storage scenarios (missing `runtime.spawnTerminal`, duplicate session IDs, lane capacity limit, watchdog ordering, storage chaos timeouts, etc.); capture failure stack traces so the next phase can fix those invariants. |
| `bun run gates --json` | PASS – already recorded earlier in the day; all eight gate phases (typecheck, lint, test, e2e, coverage, security, static-analysis, bypass-detect) had zero findings. |
| `bun run docs:build` | PASS – VitePress build succeeded with the known chunk-size warning. |
| `bun run test:desktop` | PASS – 321 unit tests pass with the expected invalid-JSON/context propagation warnings. |
| `bun run deps:status --json` | EXIT CODE 1 – reports upgradeable packages (`electrobun`, `ghostty`, `zellij`, `@types/bun`, `typescript`), so the command succeeded but indicates these pins still lag. |
