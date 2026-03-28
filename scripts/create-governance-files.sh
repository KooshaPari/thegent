#!/bin/bash
# Script to create AgilePlus governance files for all projects
# Usage: ./scripts/create-governance-files.sh [--dry-run]

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
  DRY_RUN=true
fi

AGENTS_TEMPLATE='
# Agent Rules

**This project is managed through AgilePlus.**

## AgilePlus Mandate

All work MUST be tracked in AgilePlus:
- Reference: /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
- CLI: cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>

## Branch Discipline

- Feature branches in repos/worktrees/<project>/<category>/<branch>
- Canonical repository tracks main only
- Return to main for merge/integration checkpoints

## Work Requirements

1. Check for AgilePlus spec before implementing
2. Update work package status as work progresses
3. No code without corresponding AgilePlus spec

## UTF-8 Encoding

All markdown files must use UTF-8. Avoid smart quotes, em-dashes, and special characters.

```bash
# Validate encoding (in AgilePlus repo)
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
agileplus validate-encoding --all --fix
```
'

CLAUDE_TEMPLATE='
# Project Instructions

**This project is managed through AgilePlus.**

## AgilePlus Mandate

All work MUST be tracked in AgilePlus:
- Reference: /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
- CLI: cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>

## Work Requirements

1. Check for AgilePlus spec before implementing
2. Create spec for new work: agileplus specify --title "<feature>" --description "<desc>"
3. Update work package status: agileplus status <feature-id> --wp <wp-id> --state <state>
4. No code without corresponding AgilePlus spec

## Branch Discipline

- Feature branches in repos/worktrees/<project>/<category>/<branch>
- Canonical repository tracks main only
- Return to main for merge/integration checkpoints

## UTF-8 Encoding

All markdown files must use UTF-8. Validate with:
```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
agileplus validate-encoding --all --fix
```

## AgilePlus Reference

- Specs: AgilePlus/kitty-specs/<feature-id>/
- Docs: AgilePlus/docs/
- Workflows: AgilePlus/docs/workflow/
- Worklog: AgilePlus/.work-audit/worklog.md
'

WORKLOG_TEMPLATE='
# Worklog

**This project is managed through AgilePlus.**

## AgilePlus Tracking

All feature work is tracked in AgilePlus:
- Reference: /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
- CLI: agileplus (run from AgilePlus directory)

## Quick Commands

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus

# List all features
agileplus list

# Show feature details
agileplus show <feature-id>

# Update work package status
agileplus status <feature-id> --wp <wp-id> --state <state>
```

## Current Work

See AgilePlus database for current work status:
- /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus/.agileplus/agileplus.db

## Work History

Historical work is documented in:
- AgilePlus worklog: /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus/.work-audit/worklog.md
- Git history for merged work
'

cd /Users/kooshapari/CodeProjects/Phenotype/repos

echo "=== Creating AgilePlus Governance Files ==="
echo ""

for repo in */; do
  # Skip worktrees directories (these inherit from parent)
  [[ "$repo" == *"-wtrees/" ]] && continue
  [[ "$repo" == "worktrees/" ]] && continue
  [[ "$repo" == ".archive/" ]] && continue
  [[ "$repo" == "docs/" ]] && continue
  
  needs_agents=false
  needs_claude=false
  needs_worklog=false
  
  if [[ ! -f "${repo}AGENTS.md" ]]; then
    needs_agents=true
  fi
  
  if [[ ! -f "${repo}CLAUDE.md" ]]; then
    needs_claude=true
  fi
  
  if [[ ! -f "${repo}worklog.md" ]] && [[ ! -f "${repo}docs/worklog.md" ]]; then
    needs_worklog=true
  fi
  
  if $needs_agents || $needs_claude || $needs_worklog; then
    echo "=== $repo ==="
    
    if $needs_agents; then
      if $DRY_RUN; then
        echo "  Would create: AGENTS.md"
      else
        echo "$AGENTS_TEMPLATE" > "${repo}AGENTS.md"
        echo "  Created: AGENTS.md"
      fi
    fi
    
    if $needs_claude; then
      if $DRY_RUN; then
        echo "  Would create: CLAUDE.md"
      else
        echo "$CLAUDE_TEMPLATE" > "${repo}CLAUDE.md"
        echo "  Created: CLAUDE.md"
      fi
    fi
    
    if $needs_worklog; then
      if $DRY_RUN; then
        echo "  Would create: worklog.md"
      else
        echo "$WORKLOG_TEMPLATE" > "${repo}worklog.md"
        echo "  Created: worklog.md"
      fi
    fi
    
    echo ""
  fi
done

echo "=== Done ==="
