# Gamified Development Work Stream

This directory implements the unified work stream system based on:
- 4X game mechanics (eXplore, eXpand, eXploit, eXterminate)
- Agile/Scrum ceremonies mapped to agentic workflows
- DDD bounded contexts for agent specialization
- Vibecoding principles for rapid iteration

## Directory Structure

```
specs/
├── intake/           # Raw ideas enter here (product backlog)
├── breadth/          # Multi-angle research (event storming)
├── depth/            # Deep dives (technical design)
├── devil-advocate/   # Challenge/validation (adversarial review)
├── synthesis/        # Combined findings
├── formalizing/      # Creating SPECs (PRD, FR, WBS)
├── approved/         # FINAL APPROVED SPECS (sprint backlog)
├── implementing/     # Currently being built
├── verifying/        # In review/testing
└── archived/        # Completed/obsolete
```

## Flow

1. **Intake** → Ideas enter as raw prompts
2. **Breadth** → Multi-angle exploration (event storming)
3. **Depth** → Deep technical dive
4. **Devils Advocate** → Challenge/validation
5. **Synthesis** → Combine findings
6. **Formalizing** → Create SPEC, PRD, WBS
7. **Approved** → Ready for implementation
8. **Implementing** → Being built
9. **Verifying** → In review/testing
10. **Archived** → Completed

## Gardener System

The gardener loop automatically:
- Scans for "hunger" states (low coverage, lint errors, missing docs)
- Prioritizes and spawns agents to address issues
- Tracks XP/levels/achievements
- Maintains work stream health

See `hooks/gardener-*.sh` for implementation.
