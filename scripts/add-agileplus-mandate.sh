#!/bin/bash
# Add AgilePlus mandate to all projects missing it

AGENTS_TEMPLATE='
**This project is managed through AgilePlus.**

## AgilePlus Mandate

All work MUST be tracked in AgilePlus:
- Reference: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
- CLI: `cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>`

## Work Requirements

1. **Check for AgilePlus spec before implementing**
2. **Create spec for new work**: `agileplus specify --title "<feature>" --description "<desc>"`
3. **Update work package status**: `agileplus status <feature-id> --wp <wp-id> --state <state>`
4. **No code without corresponding AgilePlus spec**

## Branch Discipline

- Feature branches in `repos/worktrees/<project>/<category>/<branch>`
- Canonical repository tracks `main` only
- Return to `main` for merge/integration checkpoints

## UTF-8 Encoding

All markdown files must use UTF-8.

---

'

CLAUDE_TEMPLATE='
**This project is managed through AgilePlus.**

## AgilePlus Mandate

All work MUST be tracked in AgilePlus:
- Reference: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
- CLI: `cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>`

## Work Requirements

1. **Check for AgilePlus spec before implementing**
2. **Create spec for new work**: `agileplus specify --title "<feature>" --description "<desc>"`
3. **Update work package status**: `agileplus status <feature-id> --wp <wp-id> --state <state>`
4. **No code without corresponding AgilePlus spec**

## Branch Discipline

- Feature branches in `repos/worktrees/<project>/<category>/<branch>`
- Canonical repository tracks `main` only
- Return to `main` for merge/integration checkpoints

## UTF-8 Encoding

All markdown files must use UTF-8.

---

'

count=0
for repo in */; do
  [[ "$repo" == *"-wtrees/" ]] && continue
  [[ "$repo" == "worktrees/" ]] && continue
  [[ "$repo" == ".archive/" ]] && continue
  [[ "$repo" == "docs/" ]] && continue
  
  agents_has=$(grep -l "AgilePlus Mandate\|IS AgilePlus" "$repo/AGENTS.md" 2>/dev/null | wc -l | tr -d ' ')
  claude_has=$(grep -l "AgilePlus Mandate\|IS AgilePlus" "$repo/CLAUDE.md" 2>/dev/null | wc -l | tr -d ' ')
  
  if [[ "$agents_has" != "1" ]] || [[ "$claude_has" != "1" ]]; then
    echo "Processing $repo..."
    
    # Create/Update AGENTS.md
    if [[ "$agents_has" != "1" ]]; then
      if [[ -f "$repo/AGENTS.md" ]]; then
        # Insert mandate after first line (header)
        first_line=$(head -1 "$repo/AGENTS.md")
        rest=$(tail -n +2 "$repo/AGENTS.md")
        printf '%s\n%s\n%s' "$first_line" "$AGENTS_TEMPLATE" "$rest" > "$repo/AGENTS.md"
      else
        printf '# Agent Rules\n%s' "$AGENTS_TEMPLATE" > "$repo/AGENTS.md"
      fi
    fi
    
    # Create/Update CLAUDE.md
    if [[ "$claude_has" != "1" ]]; then
      if [[ -f "$repo/CLAUDE.md" ]]; then
        first_line=$(head -1 "$repo/CLAUDE.md")
        rest=$(tail -n +2 "$repo/CLAUDE.md")
        printf '%s\n%s\n%s' "$first_line" "$CLAUDE_TEMPLATE" "$rest" > "$repo/CLAUDE.md"
      else
        printf '# Project Instructions\n%s' "$CLAUDE_TEMPLATE" > "$repo/CLAUDE.md"
      fi
    fi
    
    count=$((count + 1))
  fi
done

echo ""
echo "Updated $count projects with AgilePlus mandate"
