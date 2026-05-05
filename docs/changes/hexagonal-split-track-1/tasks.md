---
task_id: hexagonal-split-track-1
status: in_progress
---

# Implementation Tasks: Hexagonal Split — Track 1

**Document Version:** 1.0
**Change ID:** hexagonal-split-track-1
**Status:** WIP

---

## Phase 1: Foundation & Architecture

- [ ] T1.1: Finalize architecture decision records — review TRACK1_ARCHITECTURE_DECISIONS.md; resolve open questions
- [ ] T1.2: Scaffold CLIProxy Go module — set up Go workspace, module path, and CI pipeline
- [ ] T1.3: Define routing domain model — port routing data types to Go with Pydantic-equivalent validation

## Phase 2: Core Domain (TDD)

- [ ] T2.1: Router implementation — implement routing engine with failing Go tests first, then implementation
- [ ] T2.2: Provider adapter layer — extract and port provider adapter logic (OpenAI, Anthropic, local)
- [ ] T2.3: Auth integration — port auth token management, refresh, and credential lookup

## Phase 3: Integration & Parity

- [ ] T3.1: Python/Go interop layer — define IPC or FFI contract; implement the bridge
- [ ] T3.2: Parity verification — run full routing test suite against Go implementation; assert output equivalence
- [ ] T3.3: Feature flag rollout — add `THGENT_GO_ROUTING=enabled` toggle; validate in staging
