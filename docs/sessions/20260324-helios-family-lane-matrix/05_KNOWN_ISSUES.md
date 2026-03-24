# 05_KNOWN_ISSUES

- `heliosApp` is the largest dirty root in the helios family and needs a dedicated burn-down pass.
- `heliosCLI-composite-actions` is detached; it should be repaired before any migration attempt.
- `heliosApp-*`, `heliosCLI-*`, `helios-cli-wtrees`, `colab-wtrees`, and `helMo-wtrees` are all mixed-layout containers and should be normalized separately from root cleanup.
- `helios-cli` is comparatively small but still dirty, so it should not be treated as automatically migratable.
- `helios-cli/.worktrees/helios-cli--mod-cli-task-surface-v1` and `helios-cli/.worktrees/helios-cli--mod-policy-gate-v1` are clean and should be left alone.
- `colab` and `helMo` are not clean roots even though they are smaller than the main helios roots.
- `colab-wtrees/stabilize` is dirty, while `colab-wtrees/parity-debt-wave-20260303`, `colab-wtrees/ts-debt-parity-20260303`, and `helMo-wtrees/stability-audit` are clean and should not be disturbed.
