# Phenotype Shared Governance Blocks

This directory contains the canonical source for governance policy blocks that are shared across
all Phenotype organization repositories. Each file contains one governance block exactly as it
should appear in a repo-level `CLAUDE.md`.

## Block Index

| File | Block Heading | Marker Comment |
|------|--------------|----------------|
| `shared-reuse-protocol.md` | Phenotype Org Cross-Project Reuse Protocol | `PHENOTYPE_SHARED_REUSE_PROTOCOL` |
| `git-delivery-protocol.md` | Phenotype Git and Delivery Workflow Protocol | `PHENOTYPE_GIT_DELIVERY_PROTOCOL` |
| `longterm-stability.md` | Phenotype Long-Term Stability and Non-Destructive Change Protocol | `PHENOTYPE_LONGTERM_STABILITY_PROTOCOL` |
| `github-actions-billing.md` | GitHub Actions Billing Constraint | — |
| `ci-completeness.md` | CI Completeness Policy | — |
| `child-agent-delegation.md` | Child-Agent and Delegation Policy | — |

## Usage in Repo CLAUDE.md Files

Project-specific content (project overview, stack, commands, local patterns) goes **above** the
governance section. Shared governance blocks go at the **bottom**, under a clearly labelled
divider:

```markdown
---
<!-- Shared governance blocks — source: thegent/templates/claude/governance-blocks/ -->
<!-- Do not edit below this line in individual repos. Update the source and re-sync. -->
```

Then append all six blocks in order:

1. `shared-reuse-protocol.md`
2. `github-actions-billing.md`
3. `ci-completeness.md`
4. `git-delivery-protocol.md`
5. `longterm-stability.md`
6. `child-agent-delegation.md`

## Syncing Governance Blocks to a Repo

To append the full shared governance footer to a repo's `CLAUDE.md`:

```bash
REPO=/Users/kooshapari/CodeProjects/Phenotype/repos/<repo-name>
BLOCKS=/Users/kooshapari/CodeProjects/Phenotype/repos/thegent/templates/claude/governance-blocks

# Remove any existing governance footer (from the divider line onward) first if needed,
# then append the canonical blocks:
{
  echo ""
  echo "---"
  echo "<!-- Shared governance blocks — source: thegent/templates/claude/governance-blocks/ -->"
  echo "<!-- Do not edit below this line in individual repos. Update the source and re-sync. -->"
  echo ""
  cat "$BLOCKS/shared-reuse-protocol.md"
  echo ""
  cat "$BLOCKS/github-actions-billing.md"
  echo ""
  cat "$BLOCKS/ci-completeness.md"
  echo ""
  cat "$BLOCKS/git-delivery-protocol.md"
  echo ""
  cat "$BLOCKS/longterm-stability.md"
  echo ""
  cat "$BLOCKS/child-agent-delegation.md"
} >> "$REPO/CLAUDE.md"
```

## Update Policy

- All changes to shared blocks MUST be made here first.
- After updating a block, re-sync to all repos that include it using the script above.
- Do not modify the shared blocks inline in individual repo `CLAUDE.md` files; those edits
  will be overwritten on the next sync.
- Each block file contains exactly one `##`-level section with no surrounding wrapper — this
  allows blocks to be concatenated cleanly.
