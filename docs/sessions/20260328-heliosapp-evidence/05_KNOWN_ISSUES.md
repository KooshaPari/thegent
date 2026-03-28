# Known issues

- `bun run test:integration` now runs through the suite but 29 specs fail because the runtime invariants they assert still fail: `runtime.spawnTerminal` is missing in the new API surface, session routing rejects invalid transport/lane combinations, storage chaos timing and capacity tests hit the enforced 50-lane limit, watchdog suggestion sorting/counting asserts fail, and several storage chaos assertions time out or throw storage errors. These failures need engineering attention before the integration suite can pass.
- `bun run deps:status --json` continues to exit code 1 because dependencies (`electrobun`, `ghostty`, `zellij`, `@types/bun`, `typescript`) remain upgradeable; the tool still reports them as upgradeable even after rerunning.
