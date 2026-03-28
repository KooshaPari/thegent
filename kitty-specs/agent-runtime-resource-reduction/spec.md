# Agent runtime resource reduction

## Goal
Reduce immediate CPU, memory, process, file descriptor, and avoidable network overhead across agent workflows, with priority on simple high-ROI changes before full speculative scheduling.

## Scope
- Replace expensive shell-outs for search and traversal with faster tools or internal logic
- Scope lint, scan, and test work to changed files where possible
- Add bounded concurrency defaults for CPU- and memory-heavy work
- Cache repeated git/repo metadata lookups
- Reduce duplicate long-lived workers and package-manager contention
- Define later MTSP and scheduler follow-on work separately

## Non-Goals
- Full speculative queueing implementation in this feature
- Complete rewrite of all orchestration into one process

## Functional Requirements
- Inventory and rank high-frequency process spawn hotspots
- Identify exact codepaths where find/grep and generic shell execution can be replaced
- Define immediate work packages for tool substitution, scoping, caching, and concurrency control
- Define success metrics for CPU, memory, process count, FD count, and latency reduction
- Separate immediate wins from major-version MTSP and scheduler work

## Success Metrics
- Fewer repeated search/traversal subprocesses in hot paths
- Lower peak concurrent child-process count
- Lower average hook/tool latency
- Reduced FD pressure during parallel operations
- Measurable reduction in CPU and memory for common agent workflows

## Initial Target Areas
- thegent shell helpers and orchestration wrappers
- thegent hooks/runtime patterns already documented in user-docs
- tooling/thegent-mesh scanner shell loops
- package-manager and search/discovery command paths across active agent projects
