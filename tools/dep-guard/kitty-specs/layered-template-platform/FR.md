# Functional Requirements

## FR-001 Layer Contracts
Each template layer repo MUST expose:

- `contracts/template.manifest.json`
- `contracts/reconcile.rules.yaml`
- `Taskfile.yml` with `check`, `quality`, `release:prep`

## FR-002 Reconcile Modes
System MUST support `smart`, `overwrite`, `skip` modes with deterministic behavior.

## FR-003 Version Pinning
Downstream consumers MUST record layer versions and validate compatibility.

## FR-004 Safety by Default
Default mode MUST be `smart` and MUST NOT overwrite local conflicts silently.

## FR-005 Validation
Each layer repo MUST provide smoke checks for contract presence and reconcile-rule structure.
