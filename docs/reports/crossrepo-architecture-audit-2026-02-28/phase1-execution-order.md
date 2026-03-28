# Phase 1 Execution Order (DAG)

## Tasks
- B1: Establish boundary rule files + import-lint hooks in canonical repos.
- B2: Extract shared `spec-kitty-task-engine` package from `/Users/kooshapari/CodeProjects/Phenotype/repos/thegent/.kittify/scripts/tasks/`.
- B3: Replace duplicated task scripts in consumer repos with pinned shared package usage.
- B4: Start cliproxy executor decomposition in `/Users/kooshapari/CodeProjects/Phenotype/repos/cliproxyapi-plusplus`.
- B5: Start helios core decomposition in `/Users/kooshapari/CodeProjects/Phenotype/repos/heliosCLI`.
- B6: Start thegent runtime/tooling boundary hardening in `/Users/kooshapari/CodeProjects/Phenotype/repos/thegent`.

## Dependencies
- B1 -> B2
- B2 -> B3
- B1 -> B4
- B1 -> B5
- B1 -> B6
- B3 -> B4
- B3 -> B5
- B3 -> B6

## Parallelization Guidance
- Run B4, B5, B6 in parallel after B1 and B3 are complete.
- Keep mirrored repos (`/Users/kooshapari/CodeProjects/Phenotype/repos/cliproxyapi++`, `/Users/kooshapari/CodeProjects/Phenotype/repos/helios-cli`) out of first-wave deep refactors.
