# Stacked PRs, Agentic Workflows, and Feature-Freeze Governance — Synthesis

## Source Index
- [deepwiki: CLI Startup Flags](https://deepwiki.com/shanraisshan/claude-code-best-practice/8.2-cli-startup-flags)
- [tomfuertes gist: Claude instructions](https://gist.github.com/tomfuertes/7be9cdb1db5c0fd5737698c270c103f2)
- [middle-finger-labs/forge](https://github.com/middle-finger-labs/forge)
- [josorio7122/pi-flow](https://github.com/josorio7122/pi-flow)
- [GitHub Agentic Workflows](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/)
- [Worktree with multiple AI agents](https://www.nrmitchi.com/2025/10/using-git-worktrees-for-multi-feature-development-with-ai-agents/)
- [Agent skills + worktrees](https://blog.shanelee.name/2026/02/03/agentic-coding-git-worktrees-and-agent-skills-for-parallel-workflows/)
- [Stacked PRs overview](https://stacked-pr.github.io)
- [Stacked PR practitioner guidance](https://www.awesomecodereviews.com/best-practices/stacked-prs/)
- [Stacked PR tooling](https://graphite.com/blog/stacked-prs)
- [Stacked PR notifier/tools](https://pullnotifier.com/tools/stacked-prs)
- [GitHub discussion on safe PR stacks](https://github.com/orgs/community/discussions/179403)

## Why this matters for this workspace
- The workspace already has:
  - `CLAUDE.md`-style policy pressure in `thegent`
  - large `docs/reference/WORK_STREAM.md` backlog surface
  - multi-repo dependencies (`thegent`, `cliproxy++`, `heliosCLI`)
- The active risk is not feature breadth; it is feature **stability under concurrency**.

## Recommended Operating Model
1. **Feature freeze lock**
   - Freeze mode means no new root work for frozen features.
   - New work must resume only from stack roots already approved for this cycle.
2. **Worktree-only execution**
   - All agent branches for implementation should run in dedicated worktrees (not main).
   - Worktree naming: `.worktrees/<task-id>--<agent-id>` (single source of truth).
3. **Stack discipline**
   - `PR1` contains infra/contract baseline, `PR2` feature core, `PR3` polish/tests/docs.
   - Keep stack depth shallow; prefer at most 3–4 children per feature.
4. **Claim-before-change**
   - Read `docs/reference/WORK_STREAM.md`, take unclaimed item, record in `CLAIMED`.
5. **Reviewer contract**
   - Each child PR must declare explicit parent dependency and behavior change contract.
   - If parent changes, descendants must rebase and rebase only after parent is merge-ready.
6. **CI-first guardrails**
   - No merge when primary checks from the parent PR fail.
   - Child PRs can remain WIP if parent blocked; still required to keep scope minimal and deterministic.

### URL-to-practice mapping (high-signal)
- `deepwiki` and `GitHub` entries add explicit "startup controls + policy gates" as required pre/post workflow parameters.
- `tomfuertes`, `nrmitchi`, and `shanelee` reinforce: context-first prompts, worktree isolation, branch naming, and deterministic rebase behavior.
- `forge` and `pi-flow` show staged lanes and review checkpoints before execution starts.
- `stacked-pr` and `Graphite` entries prioritize short, ordered stacks with clear parent-child dependencies.
- community guidance adds enforceable branch hygiene and cleanup rules; include explicit worktree deletion and status handoff.

## Concrete stack template for this repo
- **Lane-0 (owner lane)**: claim + implement one in-progress partial slice in `thegent` or `cliproxy++`.
- **Lane-1 (stability lane)**: add/repair unit tests or integration checks around the same slice.
- **Lane-2 (release lane)**: docs/research updates and workstream closure metadata.
- Merge order: Lane-0 → Lane-1 → Lane-2.

## Process rules that prevent drift
- Every stack PR must mutate a bounded file set.
- No silent compatibility toggles; if a behavior changes, keep one explicit migration decision per file.
- If dynamic behavior changes, include:
  - input contract
  - fallback contract
  - failure behavior
- Keep context files in `docs/research` and `docs/reference` when governance semantics change.

## Repo-specific initial actions (next 20 tasks)
1. Finish pre-existing partial implementations in place:
   - `cliproxy++` benchmark client + resource fallback resolution
   - `thegent` planning D2 resource contention simulation
2. For each finished slice:
   - update `docs/reference/WORK_STREAM.md` if source IDs exist
   - attach stack-ready note in change summary
3. Continue using child agents for non-overlapping slices.

## Recommended command profile
- `git worktree add` for each lane
- `thegent sync work-stream`
- `thegent sync autopilot --once` + `thegent sync autopilot-status`
- `thegent plan do-next` to pull dependency-compatible next item
- Rebase descendants immediately on parent update
