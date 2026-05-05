# Plan: phench-module-composition-v2

## Objective

Execute wave 2 of the Phench module composition system, adding manifest-driven module composition, CLI entrypoint for `target add-module`, extended runtime selection semantics, and shared-module materialization workflow support.

## Approach

1. Define the module manifest schema (module name, runner, command, profile, exclusions)
2. Implement manifest loading and validation in thegent_bench service and CLI
3. Add `target add-module` CLI command with override support and deterministic lock refresh
4. Extend runtime selection semantics so module-level values apply when `run` is invoked without overrides
5. Validate with test coverage for manifest loading, exclusions, CLI invocation, and module-driven override behavior
